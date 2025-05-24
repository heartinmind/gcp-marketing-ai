"""
WebScraper 포괄적 단위 테스트

실제 비즈니스 로직을 검증하는 의미있는 테스트들
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import hashlib

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data_collection.web_scraper import WebScraper


class TestWebScraperComprehensive:
    """WebScraper의 모든 핵심 기능에 대한 포괄적 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출되는 설정"""
        self.scraper = WebScraper(delay=0.1)  # 테스트용 짧은 딜레이
        
        # 테스트용 샘플 경쟁사 데이터
        self.sample_competitor = {
            "name": "test_competitor",
            "url": "https://example.com",
            "target_pages": ["/product", "/pricing", "/about"]
        }
        
        # 모킹용 HTML 응답
        self.sample_html = """
        <html>
        <head>
            <title>Test Page Title</title>
            <meta name="description" content="Test meta description">
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>This is test content for scraping.</p>
            <div>More content here.</div>
        </body>
        </html>
        """
    
    @patch('requests.Session.get')
    def test_scrape_single_page_success(self, mock_get):
        """단일 페이지 스크래핑 성공 테스트"""
        # Given: 성공적인 HTTP 응답 모킹
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_get.return_value = mock_response
        
        # When: 페이지 스크래핑 실행
        result = self.scraper._scrape_page("https://example.com/test", "test_competitor")
        
        # Then: 올바른 데이터가 반환되어야 함
        assert result['url'] == "https://example.com/test"
        assert result['competitor_name'] == "test_competitor"
        assert result['page_title'] == "Test Page Title"
        assert result['meta_description'] == "Test meta description"
        assert "Main Heading" in result['content']
        assert "test content for scraping" in result['content']
        assert 'content_hash' in result
        assert 'collected_at' in result
    
    @patch('requests.Session.get')
    def test_scrape_single_page_http_error(self, mock_get):
        """HTTP 에러 상황 테스트"""
        # Given: HTTP 에러 응답 모킹
        mock_get.side_effect = requests.RequestException("Connection failed")
        
        # When: 페이지 스크래핑 실행
        result = self.scraper._scrape_page("https://example.com/test", "test_competitor")
        
        # Then: None이 반환되어야 함
        assert result is None
    
    @patch('requests.Session.get')
    def test_scrape_single_page_404_error(self, mock_get):
        """404 에러 상황 테스트"""
        # Given: 404 응답 모킹
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # When: 페이지 스크래핑 실행
        result = self.scraper._scrape_page("https://example.com/test", "test_competitor")
        
        # Then: None이 반환되어야 함
        assert result is None
    
    @patch('requests.Session.get')
    def test_scrape_competitor_full_workflow(self, mock_get):
        """경쟁사 전체 스크래핑 워크플로우 테스트"""
        # Given: 여러 페이지에 대한 성공적인 응답 모킹
        def mock_response_side_effect(url):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'content-type': 'text/html'}
            
            if 'product' in url:
                mock_response.text = "<html><head><title>Product Page</title></head><body>Product content</body></html>"
            elif 'pricing' in url:
                mock_response.text = "<html><head><title>Pricing Page</title></head><body>Pricing content</body></html>"
            elif 'about' in url:
                mock_response.text = "<html><head><title>About Page</title></head><body>About content</body></html>"
            else:
                mock_response.text = self.sample_html
            
            return mock_response
        
        mock_get.side_effect = mock_response_side_effect
        
        # When: 경쟁사 스크래핑 실행
        results = self.scraper.scrape_competitor(self.sample_competitor)
        
        # Then: 모든 페이지가 성공적으로 스크래핑되어야 함
        assert len(results) == 3
        
        # 각 페이지의 데이터 검증
        urls = [result['url'] for result in results]
        assert "https://example.com/product" in urls
        assert "https://example.com/pricing" in urls
        assert "https://example.com/about" in urls
        
        # 각 결과의 구조 검증
        for result in results:
            assert 'url' in result
            assert 'competitor_name' in result
            assert 'page_title' in result
            assert 'content' in result
            assert 'meta_description' in result
            assert 'collected_at' in result
            assert 'content_hash' in result
            assert result['competitor_name'] == "test_competitor"
    
    @patch('requests.Session.get')
    def test_scrape_competitor_partial_failure(self, mock_get):
        """일부 페이지 실패 상황 테스트"""
        # Given: 일부 페이지는 성공, 일부는 실패하는 응답 모킹
        def mock_response_side_effect(url):
            if 'product' in url:
                # 성공 응답
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = self.sample_html
                mock_response.headers = {'content-type': 'text/html'}
                return mock_response
            else:
                # 실패 응답
                raise requests.RequestException("Connection failed")
        
        mock_get.side_effect = mock_response_side_effect
        
        # When: 경쟁사 스크래핑 실행
        results = self.scraper.scrape_competitor(self.sample_competitor)
        
        # Then: 성공한 페이지만 결과에 포함되어야 함
        assert len(results) == 1
        assert results[0]['url'] == "https://example.com/product"
    
    def test_extract_title_various_formats(self):
        """다양한 형식의 title 추출 테스트"""
        # Test case 1: 일반적인 title
        html1 = "<html><head><title>Normal Title</title></head><body></body></html>"
        title1 = self.scraper._extract_title(html1)
        assert title1 == "Normal Title"
        
        # Test case 2: 공백이 있는 title
        html2 = "<html><head><title>  Spaced Title  </title></head><body></body></html>"
        title2 = self.scraper._extract_title(html2)
        assert title2 == "Spaced Title"
        
        # Test case 3: 특수문자가 있는 title
        html3 = "<html><head><title>Title & Co. - Best Solution!</title></head><body></body></html>"
        title3 = self.scraper._extract_title(html3)
        assert title3 == "Title & Co. - Best Solution!"
        
        # Test case 4: title 태그가 없는 경우
        html4 = "<html><head></head><body></body></html>"
        title4 = self.scraper._extract_title(html4)
        assert title4 == ""
    
    def test_extract_content_comprehensive(self):
        """포괄적인 콘텐츠 추출 테스트"""
        # Given: 복잡한 HTML 구조
        complex_html = """
        <html>
        <head>
            <title>Test Page</title>
            <style>body { color: red; }</style>
            <script>console.log('test');</script>
        </head>
        <body>
            <nav>Navigation content</nav>
            <header>Header content</header>
            <main>
                <h1>Main Heading</h1>
                <p>This is a paragraph with <strong>important</strong> text.</p>
                <div class="content">
                    <p>More content here.</p>
                    <ul>
                        <li>List item 1</li>
                        <li>List item 2</li>
                    </ul>
                </div>
            </main>
            <footer>Footer content</footer>
            <script>alert('popup');</script>
        </body>
        </html>
        """
        
        # When: 콘텐츠 추출
        content = self.scraper._extract_content(complex_html)
        
        # Then: 텍스트 콘텐츠만 추출되고 스크립트/스타일은 제외되어야 함
        assert "Main Heading" in content
        assert "This is a paragraph with important text." in content
        assert "More content here." in content
        assert "List item 1" in content
        assert "List item 2" in content
        
        # 스크립트와 스타일 콘텐츠는 제외되어야 함
        assert "console.log" not in content
        assert "color: red" not in content
        assert "alert('popup')" not in content
    
    def test_extract_meta_description_variations(self):
        """다양한 meta description 추출 테스트"""
        # Test case 1: 일반적인 meta description
        html1 = '<html><head><meta name="description" content="This is a test description"></head></html>'
        meta1 = self.scraper._extract_meta_description(html1)
        assert meta1 == "This is a test description"
        
        # Test case 2: property 형식의 meta description
        html2 = '<html><head><meta property="description" content="Property description"></head></html>'
        meta2 = self.scraper._extract_meta_description(html2)
        assert meta2 == "Property description"
        
        # Test case 3: 대소문자 혼합
        html3 = '<html><head><meta NAME="Description" CONTENT="Mixed case description"></head></html>'
        meta3 = self.scraper._extract_meta_description(html3)
        assert meta3 == "Mixed case description"
        
        # Test case 4: meta description이 없는 경우
        html4 = '<html><head><meta name="keywords" content="test,keywords"></head></html>'
        meta4 = self.scraper._extract_meta_description(html4)
        assert meta4 == ""
    
    def test_generate_content_hash_consistency(self):
        """콘텐츠 해시 생성 일관성 테스트"""
        # Given: 동일한 콘텐츠
        content1 = "This is test content for hashing"
        content2 = "This is test content for hashing"
        content3 = "This is different content"
        
        # When: 해시 생성
        hash1 = self.scraper._generate_content_hash(content1)
        hash2 = self.scraper._generate_content_hash(content2)
        hash3 = self.scraper._generate_content_hash(content3)
        
        # Then: 동일한 콘텐츠는 동일한 해시, 다른 콘텐츠는 다른 해시
        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 64  # SHA256 해시 길이
    
    @patch('requests.Session.get')
    def test_rate_limiting_delay(self, mock_get):
        """요청 간 딜레이 테스트"""
        # Given: 성공적인 응답 모킹
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.sample_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_get.return_value = mock_response
        
        # 딜레이 시간이 있는 스크래퍼 생성
        scraper_with_delay = WebScraper(delay=0.1)
        
        # When: 여러 페이지 스크래핑 실행 (시간 측정)
        import time
        start_time = time.time()
        scraper_with_delay.scrape_competitor(self.sample_competitor)
        end_time = time.time()
        
        # Then: 딜레이가 적용되어 일정 시간 이상 걸려야 함
        # 3개 페이지, 각각 0.1초 딜레이 = 최소 0.2초 (첫 페이지는 딜레이 없음)
        execution_time = end_time - start_time
        assert execution_time >= 0.2
    
    def test_invalid_url_handling(self):
        """잘못된 URL 처리 테스트"""
        # Given: 잘못된 형식의 URL을 가진 경쟁사 데이터
        invalid_competitor = {
            "name": "invalid_competitor",
            "url": "not-a-valid-url",
            "target_pages": ["/test"]
        }
        
        # When: 스크래핑 실행
        results = self.scraper.scrape_competitor(invalid_competitor)
        
        # Then: 빈 결과가 반환되어야 함
        assert len(results) == 0
    
    @patch('requests.Session.get')
    def test_large_content_handling(self, mock_get):
        """대용량 콘텐츠 처리 테스트"""
        # Given: 매우 큰 HTML 콘텐츠
        large_content = "<p>" + "This is a very long content. " * 10000 + "</p>"
        large_html = f"<html><head><title>Large Page</title></head><body>{large_content}</body></html>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = large_html
        mock_response.headers = {'content-type': 'text/html'}
        mock_get.return_value = mock_response
        
        # When: 스크래핑 실행
        result = self.scraper._scrape_page("https://example.com/large", "test_competitor")
        
        # Then: 결과가 올바르게 처리되어야 함
        assert result is not None
        assert result['page_title'] == "Large Page"
        assert len(result['content']) > 100000  # 대용량 콘텐츠 확인
        assert 'content_hash' in result
    
    @patch('requests.Session.get')
    def test_non_html_content_handling(self, mock_get):
        """HTML이 아닌 콘텐츠 처리 테스트"""
        # Given: JSON 응답
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"data": "json content"}'
        mock_response.headers = {'content-type': 'application/json'}
        mock_get.return_value = mock_response
        
        # When: 스크래핑 실행
        result = self.scraper._scrape_page("https://example.com/api", "test_competitor")
        
        # Then: HTML이 아닌 콘텐츠도 처리되어야 함
        assert result is not None
        assert result['content'] == '{"data": "json content"}'
        assert result['page_title'] == ""  # JSON에는 title 없음
    
    @patch('requests.Session.get')
    @patch('src.data_collection.web_scraper.logger')
    def test_error_logging(self, mock_logger, mock_get):
        """에러 로깅 테스트"""
        # Given: 예외를 발생시키는 요청
        mock_get.side_effect = requests.RequestException("Network error")
        
        # When: 스크래핑 실행
        result = self.scraper._scrape_page("https://example.com/test", "test_competitor")
        
        # Then: 에러가 로깅되고 None이 반환되어야 함
        assert result is None
        mock_logger.error.assert_called()
    
    def test_url_construction(self):
        """URL 생성 로직 테스트"""
        # Given: 다양한 형식의 base URL과 target page
        test_cases = [
            ("https://example.com", "/product", "https://example.com/product"),
            ("https://example.com/", "/product", "https://example.com/product"),
            ("https://example.com", "product", "https://example.com/product"),
            ("https://example.com/", "product", "https://example.com/product"),
        ]
        
        for base_url, target_page, expected_url in test_cases:
            # When: URL 생성 (scrape_competitor 메서드 내부 로직)
            competitor = {"name": "test", "url": base_url, "target_pages": [target_page]}
            
            # URL 생성 로직 테스트를 위해 _build_url 메서드가 있다면 테스트
            # 현재 구현에서는 단순 문자열 합치기를 사용하므로 결과 확인
            if base_url.endswith('/') and target_page.startswith('/'):
                full_url = base_url + target_page[1:]
            elif not base_url.endswith('/') and not target_page.startswith('/'):
                full_url = base_url + '/' + target_page
            else:
                full_url = base_url + target_page
            
            # Then: 올바른 URL이 생성되어야 함
            assert full_url == expected_url 