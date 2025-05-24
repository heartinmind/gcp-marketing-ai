"""
WebScraper 단위 테스트

WebScraper 클래스의 각 메서드에 대한 단위 테스트를 포함합니다.
"""

from bs4 import BeautifulSoup
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data_collection.web_scraper import WebScraper


class TestWebScraper:
    """WebScraper 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출되는 설정"""
        self.scraper = WebScraper()
    
    def test_extract_title_basic_html(self):
        """기본 HTML 구조에서 제목 추출 테스트"""
        # Given: 기본 HTML 샘플
        html = """
        <html>
            <head>
                <title>MarketingAI - 경쟁사 분석 플랫폼</title>
            </head>
            <body>
                <h1>컨텐츠</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: 올바른 제목이 추출되어야 함
        assert title == "MarketingAI - 경쟁사 분석 플랫폼"
    
    def test_extract_title_no_title_tag(self):
        """title 태그가 없는 HTML에서 빈 문자열 반환 테스트"""
        # Given: title 태그가 없는 HTML
        html = """
        <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body>
                <h1>제목</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: 빈 문자열이 반환되어야 함
        assert title == ""
    
    def test_extract_title_empty_title_tag(self):
        """빈 title 태그에서 빈 문자열 반환 테스트"""
        # Given: 빈 title 태그가 있는 HTML
        html = """
        <html>
            <head>
                <title></title>
            </head>
            <body>
                <h1>컨텐츠</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: 빈 문자열이 반환되어야 함
        assert title == ""
    
    def test_extract_title_whitespace_only(self):
        """공백만 있는 title 태그에서 빈 문자열 반환 테스트"""
        # Given: 공백만 있는 title 태그
        html = """
        <html>
            <head>
                <title>   \n\t   </title>
            </head>
            <body>
                <h1>컨텐츠</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: 빈 문자열이 반환되어야 함 (공백이 strip됨)
        assert title == ""
    
    def test_extract_title_with_leading_trailing_spaces(self):
        """앞뒤 공백이 있는 제목에서 공백 제거 테스트"""
        # Given: 앞뒤 공백이 있는 title
        html = """
        <html>
            <head>
                <title>  Best Marketing Platform  </title>
            </head>
            <body>
                <h1>컨텐츠</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: 공백이 제거된 제목이 반환되어야 함
        assert title == "Best Marketing Platform"
    
    def test_extract_title_special_characters(self):
        """특수문자가 포함된 제목 추출 테스트"""
        # Given: 특수문자가 포함된 title
        html = """
        <html>
            <head>
                <title>Analytics &amp; Intelligence | Company™</title>
            </head>
            <body>
                <h1>컨텐츠</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: HTML 엔티티가 디코딩된 제목이 반환되어야 함
        assert title == "Analytics & Intelligence | Company™"
    
    def test_extract_title_korean_text(self):
        """한글 제목 추출 테스트"""
        # Given: 한글 제목이 있는 HTML
        html = """
        <html>
            <head>
                <title>마케팅AI - 소셜미디어 분석 도구</title>
            </head>
            <body>
                <h1>환영합니다</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: 한글 제목이 올바르게 추출되어야 함
        assert title == "마케팅AI - 소셜미디어 분석 도구"
    
    def test_extract_title_long_title(self):
        """긴 제목 추출 테스트"""
        # Given: 매우 긴 제목이 있는 HTML
        html = """
        <html>
            <head>
                <title>Comprehensive Marketing Analytics Platform for Social Media Monitoring and Competitive Intelligence Analysis</title>
            </head>
            <body>
                <h1>컨텐츠</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: 전체 제목이 추출되어야 함
        expected_title = "Comprehensive Marketing Analytics Platform for Social Media Monitoring and Competitive Intelligence Analysis"
        assert title == expected_title
    
    def test_extract_title_multiple_title_tags(self):
        """여러 title 태그가 있을 때 첫 번째 태그 사용 테스트"""
        # Given: 여러 title 태그가 있는 HTML
        html = """
        <html>
            <head>
                <title>First Title</title>
                <title>Second Title</title>
            </head>
            <body>
                <h1>컨텐츠</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: 첫 번째 title 태그의 내용이 반환되어야 함
        assert title == "First Title"
    
    def test_extract_title_nested_tags(self):
        """title 태그 내부에 다른 태그가 있는 경우 테스트"""
        # Given: title 태그 내부에 다른 태그가 있는 HTML
        html = """
        <html>
            <head>
                <title>Analytics <span>Platform</span> - Home</title>
            </head>
            <body>
                <h1>컨텐츠</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: 모든 텍스트가 추출되어야 함 (태그는 제거됨)
        assert title == "Analytics Platform - Home"
    
    def test_extract_title_malformed_html(self):
        """잘못된 형식의 HTML에서 제목 추출 테스트"""
        # Given: 잘못된 형식의 HTML
        html = """
        <html>
            <head>
                <title>Valid Title
            </head>
            <body>
                <h1>컨텐츠</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: BeautifulSoup가 자동으로 수정한 HTML에서 제목이 추출되어야 함
        assert "Valid Title" in title
    
    def test_extract_title_minimal_html(self):
        """최소한의 HTML 구조에서 제목 추출 테스트"""
        # Given: 최소한의 HTML 구조
        html = "<title>Simple Title</title>"
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: 제목이 올바르게 추출되어야 함
        assert title == "Simple Title"
    
    def test_extract_title_with_newlines(self):
        """제목에 줄바꿈이 포함된 경우 테스트"""
        # Given: 줄바꿈이 포함된 title
        html = """
        <html>
            <head>
                <title>
                    Marketing
                    Analytics
                    Platform
                </title>
            </head>
            <body>
                <h1>컨텐츠</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # When: 제목 추출
        title = self.scraper._extract_title(soup)
        
        # Then: 줄바꿈이 공백으로 변환되고 strip되어야 함
        assert "Marketing" in title
        assert "Analytics" in title
        assert "Platform" in title
        # 정확한 공백 처리 결과는 BeautifulSoup의 get_text() 동작에 따라 결정됨 