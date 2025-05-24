"""
MarketingAI 메인 실행 스크립트
경쟁사 데이터 수집 및 BigQuery 저장을 수행합니다.
"""

import sys
import os
import logging
from datetime import datetime
import hashlib

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import (
    PROJECT_ID, DATASET_ID, COMPETITORS, REQUEST_DELAY, LOG_LEVEL
)
from src.data_collection.web_scraper import WebScraper
from src.utils.bigquery_client import BigQueryClient
from analytics.engines.basic_analyzer import BasicAnalyzer

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """메인 실행 함수"""
    logger.info("MarketingAI 데이터 수집 시작")
    
    # 클라이언트 초기화
    scraper = WebScraper(delay=REQUEST_DELAY)
    bq_client = BigQueryClient(PROJECT_ID, DATASET_ID)
    
    all_data = []
    
    # 각 경쟁사 데이터 수집
    for competitor in COMPETITORS:
        logger.info(f"경쟁사 '{competitor['name']}' 데이터 수집 시작")
        
        try:
            competitor_data = scraper.scrape_competitor(competitor)
            
            # 중복 체크 및 필터링
            filtered_data = []
            for data in competitor_data:
                latest_hash = bq_client.get_latest_content_hash(
                    data['competitor_name'], 
                    data['url']
                )
                
                if latest_hash != data['content_hash']:
                    filtered_data.append(data)
                    logger.info(f"새로운 콘텐츠 발견: {data['url']}")
                else:
                    logger.info(f"콘텐츠 변경 없음: {data['url']}")
            
            all_data.extend(filtered_data)
            logger.info(f"경쟁사 '{competitor['name']}' 수집 완료: {len(filtered_data)}개 새 페이지")
            
        except Exception as e:
            logger.error(f"경쟁사 '{competitor['name']}' 수집 실패: {str(e)}")
    
    # BigQuery에 데이터 저장
    if all_data:
        logger.info(f"총 {len(all_data)}개 페이지를 BigQuery에 저장 중...")
        success = bq_client.insert_competitor_data(all_data)
        
        if success:
            logger.info("데이터 저장 완료")
        else:
            logger.error("데이터 저장 실패")
    else:
        logger.info("저장할 새로운 데이터가 없습니다.")
    
    logger.info("MarketingAI 데이터 수집 완료")


if __name__ == "__main__":
    main() 
