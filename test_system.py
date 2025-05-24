"""
MarketingAI 시스템 테스트 스크립트
기본 기능들이 정상적으로 작동하는지 테스트합니다.
"""

import sys
import os
import logging
from datetime import datetime
import hashlib

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import PROJECT_ID, DATASET_ID
from src.data_collection.web_scraper import WebScraper
from src.utils.bigquery_client import BigQueryClient
from src.analysis.basic_analyzer import BasicAnalyzer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_web_scraper():
    """웹 스크래퍼 테스트"""
    logger.info("=== 웹 스크래퍼 테스트 시작 ===")
    
    scraper = WebScraper(delay=1)
    
    # 테스트용 간단한 웹사이트
    test_competitor = {
        "name": "test_site",
        "url": "https://httpbin.org",
        "target_pages": ["/html", "/json"]
    }
    
    try:
        results = scraper.scrape_competitor(test_competitor)
        logger.info(f"스크래핑 결과: {len(results)}개 페이지")
        
        for result in results:
            logger.info(f"- URL: {result['url']}")
            logger.info(f"- 제목: {result['page_title'][:50]}...")
            logger.info(f"- 콘텐츠 길이: {len(result['content'])}자")
        
        return results
        
    except Exception as e:
        logger.error(f"웹 스크래퍼 테스트 실패: {str(e)}")
        return []


def test_bigquery_client():
    """BigQuery 클라이언트 테스트"""
    logger.info("=== BigQuery 클라이언트 테스트 시작 ===")
    
    bq_client = BigQueryClient(PROJECT_ID, DATASET_ID)
    
    try:
        # 기존 데이터 조회 테스트
        existing_data = bq_client.query_competitor_data(limit=5)
        logger.info(f"기존 데이터 조회: {len(existing_data)}개 레코드")
        
        return True
        
    except Exception as e:
        logger.error(f"BigQuery 클라이언트 테스트 실패: {str(e)}")
        return False


def test_basic_analyzer():
    """기본 분석기 테스트"""
    logger.info("=== 기본 분석기 테스트 시작 ===")
    
    analyzer = BasicAnalyzer()
    
    # 테스트 데이터 생성
    test_data = [
        {
            'url': 'https://example.com/product1',
            'page_title': 'Amazing Product - Best Solution',
            'content': 'This is an amazing product that provides the best solution for your business needs. Our innovative technology helps companies grow.',
            'meta_description': 'Best product for business growth',
            'collected_at': '2024-01-01T10:00:00',
            'content_hash': 'hash1'
        },
        {
            'url': 'https://example.com/pricing',
            'page_title': 'Pricing Plans - Affordable Solutions',
            'content': 'Our pricing plans are designed to be affordable for businesses of all sizes. Choose the plan that fits your budget.',
            'meta_description': 'Affordable pricing plans',
            'collected_at': '2024-01-02T10:00:00',
            'content_hash': 'hash2'
        }
    ]
    
    try:
        # 키워드 분석 테스트
        keyword_analysis = analyzer.analyze_keywords(test_data)
        logger.info(f"키워드 분석 완료: {keyword_analysis.get('unique_words', 0)}개 고유 단어")
        
        # 콘텐츠 변경 분석 테스트
        change_analysis = analyzer.analyze_content_changes(test_data)
        logger.info(f"콘텐츠 변경 분석 완료: {change_analysis.get('total_pages_monitored', 0)}개 페이지 모니터링")
        
        # 경쟁사 요약 분석 테스트
        summary = analyzer.generate_competitor_summary('test_competitor', test_data)
        logger.info(f"경쟁사 요약 분석 완료: {summary.get('competitor_name', 'Unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"기본 분석기 테스트 실패: {str(e)}")
        return False


def test_integration():
    """통합 테스트"""
    logger.info("=== 통합 테스트 시작 ===")
    
    try:
        # 1. 웹 스크래핑
        scraped_data = test_web_scraper()
        if not scraped_data:
            logger.warning("웹 스크래핑 데이터가 없어 통합 테스트를 건너뜁니다.")
            return False
        
        # 2. BigQuery 저장
        bq_client = BigQueryClient(PROJECT_ID, DATASET_ID)
        success = bq_client.insert_competitor_data(scraped_data)
        
        if success:
            logger.info("BigQuery 저장 성공")
        else:
            logger.error("BigQuery 저장 실패")
            return False
        
        # 3. 데이터 분석
        analyzer = BasicAnalyzer()
        keyword_analysis = analyzer.analyze_keywords(scraped_data)
        
        # 4. 분석 결과 저장
        analysis_record = analyzer.create_analysis_record(
            competitor_name='test_site',
            analysis_type='keyword',
            results=keyword_analysis,
            summary=f"총 {keyword_analysis.get('unique_words', 0)}개의 고유 키워드 발견"
        )
        
        analysis_success = bq_client.insert_analysis_results([analysis_record])
        
        if analysis_success:
            logger.info("분석 결과 저장 성공")
            logger.info("=== 통합 테스트 완료 ===")
            return True
        else:
            logger.error("분석 결과 저장 실패")
            return False
        
    except Exception as e:
        logger.error(f"통합 테스트 실패: {str(e)}")
        return False


def main():
    """메인 테스트 함수"""
    logger.info("MarketingAI 시스템 테스트 시작")
    
    # 개별 컴포넌트 테스트
    tests = [
        ("웹 스크래퍼", lambda: len(test_web_scraper()) > 0),
        ("BigQuery 클라이언트", test_bigquery_client),
        ("기본 분석기", test_basic_analyzer),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            status = "✅ 성공" if result else "❌ 실패"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            results[test_name] = False
            logger.error(f"{test_name}: ❌ 실패 - {str(e)}")
    
    # 통합 테스트
    if all(results.values()):
        logger.info("모든 개별 테스트 통과. 통합 테스트 실행 중...")
        integration_result = test_integration()
        results["통합 테스트"] = integration_result
        status = "✅ 성공" if integration_result else "❌ 실패"
        logger.info(f"통합 테스트: {status}")
    else:
        logger.warning("일부 개별 테스트 실패로 통합 테스트를 건너뜁니다.")
    
    # 최종 결과
    logger.info("\n=== 테스트 결과 요약 ===")
    for test_name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        logger.info(f"{test_name}: {status}")
    
    success_rate = sum(results.values()) / len(results) * 100
    logger.info(f"전체 성공률: {success_rate:.1f}%")
    
    if success_rate == 100:
        logger.info("🎉 모든 테스트가 성공했습니다! 시스템이 정상적으로 작동합니다.")
    else:
        logger.warning("⚠️ 일부 테스트가 실패했습니다. 문제를 확인해주세요.")


if __name__ == "__main__":
    main() 
