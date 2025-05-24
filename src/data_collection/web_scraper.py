"""
웹 스크래핑 모듈
경쟁사 웹사이트에서 데이터를 수집하는 기능을 제공합니다.
"""

import requests
import time
import hashlib
import uuid
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """웹 스크래핑 클래스"""
    
    def __init__(self, delay: int = 1):
        """
        Args:
            delay: 요청 간 지연 시간 (초)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def scrape_page(self, url: str, competitor_name: str) -> Optional[Dict]:
        """
        단일 페이지를 스크래핑합니다.
        
        Args:
            url: 스크래핑할 URL
            competitor_name: 경쟁사 이름
            
        Returns:
            스크래핑된 데이터 딕셔너리 또는 None
        """
        try:
            logger.info(f"스크래핑 시작: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 페이지 데이터 추출
            page_data = {
                'id': str(uuid.uuid4()),
                'competitor_name': competitor_name,
                'url': url,
                'page_title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'meta_description': self._extract_meta_description(soup),
                'collected_at': datetime.utcnow().isoformat(),
                'content_hash': None
            }
            
            # 콘텐츠 해시 생성
            content_for_hash = f"{page_data['page_title']}{page_data['content']}"
            page_data['content_hash'] = hashlib.md5(
                content_for_hash.encode('utf-8')
            ).hexdigest()
            
            logger.info(f"스크래핑 완료: {url}")
            time.sleep(self.delay)
            
            return page_data
            
        except Exception as e:
            logger.error(f"스크래핑 실패 {url}: {str(e)}")
            return None
    
    def scrape_competitor(self, competitor_config: Dict) -> List[Dict]:
        """
        경쟁사의 여러 페이지를 스크래핑합니다.
        
        Args:
            competitor_config: 경쟁사 설정 딕셔너리
            
        Returns:
            스크래핑된 데이터 리스트
        """
        results = []
        base_url = competitor_config['url']
        competitor_name = competitor_config['name']
        target_pages = competitor_config.get('target_pages', ['/'])
        
        for page_path in target_pages:
            full_url = base_url.rstrip('/') + page_path
            page_data = self.scrape_page(full_url, competitor_name)
            
            if page_data:
                results.append(page_data)
        
        return results
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """페이지 제목 추출"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """페이지 텍스트 콘텐츠 추출"""
        # 스크립트와 스타일 태그 제거
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 텍스트 추출
        text = soup.get_text()
        
        # 공백 정리
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:10000]  # 최대 10,000자로 제한
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """메타 설명 추출"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        return "" 
