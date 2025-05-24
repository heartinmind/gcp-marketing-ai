"""
BasicAnalyzer 단위 테스트

BasicAnalyzer 클래스의 각 메서드에 대한 단위 테스트를 포함합니다.
"""

import sys
import os

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analysis.basic_analyzer import BasicAnalyzer


class TestBasicAnalyzer:
    """BasicAnalyzer 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출되는 설정"""
        self.analyzer = BasicAnalyzer()
    
    def test_extract_keywords_removes_stop_words(self):
        """불용어가 올바르게 제거되는지 테스트"""
        # Given: 불용어를 포함한 텍스트
        text = "The quick brown fox jumps over the lazy dog and runs very fast"
        
        # When: 키워드 추출
        keywords = self.analyzer._extract_keywords(text)
        
        # Then: 불용어가 제거되고 의미있는 단어만 남아있어야 함
        expected_keywords = ["quick", "brown", "fox", "jumps", "lazy", "dog", "runs", "fast"]
        assert set(keywords) == set(expected_keywords)
        
        # 불용어가 포함되지 않았는지 확인
        stop_words = ["the", "and", "very", "over"]
        for stop_word in stop_words:
            assert stop_word not in keywords
    
    def test_extract_keywords_filters_short_words(self):
        """길이가 2자 이하인 단어가 필터링되는지 테스트"""
        # Given: 짧은 단어들을 포함한 텍스트
        text = "AI ML is a good technology to use"
        
        # When: 키워드 추출
        keywords = self.analyzer._extract_keywords(text)
        
        # Then: 3자 이상의 단어만 포함되어야 함
        for keyword in keywords:
            assert len(keyword) > 2
        
        # 예상 결과 확인
        expected_keywords = ["good", "technology", "use"]
        assert set(keywords) == set(expected_keywords)
    
    def test_extract_keywords_removes_punctuation(self):
        """구두점이 올바르게 제거되는지 테스트"""
        # Given: 구두점을 포함한 텍스트
        text = "Hello, world! This is amazing. Technology-driven solutions?"
        
        # When: 키워드 추출
        keywords = self.analyzer._extract_keywords(text)
        
        # Then: 구두점이 제거된 단어들만 포함되어야 함 ("this"는 불용어로 제거됨)
        expected_keywords = ["hello", "world", "amazing", "technology", "driven", "solutions"]
        assert set(keywords) == set(expected_keywords)
        
        # 구두점이 포함된 문자열이 없어야 함
        for keyword in keywords:
            assert keyword.isalpha()
    
    def test_extract_keywords_converts_to_lowercase(self):
        """대소문자가 올바르게 소문자로 변환되는지 테스트"""
        # Given: 대소문자가 섞인 텍스트
        text = "MARKETING Analytics Platform"
        
        # When: 키워드 추출
        keywords = self.analyzer._extract_keywords(text)
        
        # Then: 모든 키워드가 소문자여야 함
        expected_keywords = ["marketing", "analytics", "platform"]
        assert set(keywords) == set(expected_keywords)
        
        for keyword in keywords:
            assert keyword.islower()
    
    def test_extract_keywords_empty_text(self):
        """빈 텍스트에 대한 처리 테스트"""
        # Given: 빈 텍스트
        text = ""
        
        # When: 키워드 추출
        keywords = self.analyzer._extract_keywords(text)
        
        # Then: 빈 리스트가 반환되어야 함
        assert keywords == []
    
    def test_extract_keywords_whitespace_only(self):
        """공백만 있는 텍스트에 대한 처리 테스트"""
        # Given: 공백만 있는 텍스트
        text = "   \n\t   "
        
        # When: 키워드 추출
        keywords = self.analyzer._extract_keywords(text)
        
        # Then: 빈 리스트가 반환되어야 함
        assert keywords == []
    
    def test_extract_keywords_only_stop_words(self):
        """불용어만 있는 텍스트에 대한 처리 테스트"""
        # Given: 불용어만 있는 텍스트
        text = "the and or but in on at to for of with by"
        
        # When: 키워드 추출
        keywords = self.analyzer._extract_keywords(text)
        
        # Then: 빈 리스트가 반환되어야 함
        assert keywords == []
    
    def test_extract_keywords_numbers_removed(self):
        """숫자가 포함된 단어가 필터링되는지 테스트"""
        # Given: 숫자가 포함된 텍스트
        text = "product123 version2 price100 marketing analytics"
        
        # When: 키워드 추출
        keywords = self.analyzer._extract_keywords(text)
        
        # Then: 알파벳만 있는 단어만 포함되어야 함
        expected_keywords = ["marketing", "analytics"]
        assert set(keywords) == set(expected_keywords)
    
    def test_extract_keywords_korean_text_handling(self):
        """한글 텍스트 처리 테스트 (한글도 포함됨)"""
        # Given: 한글이 포함된 텍스트
        text = "마케팅 analytics 플랫폼 platform"
        
        # When: 키워드 추출
        keywords = self.analyzer._extract_keywords(text)
        
        # Then: 한글과 영어 단어 모두 추출되어야 함
        expected_keywords = ["마케팅", "analytics", "플랫폼", "platform"]
        assert set(keywords) == set(expected_keywords)
    
    def test_extract_keywords_complex_text(self):
        """복잡한 실제 텍스트에 대한 종합 테스트"""
        # Given: 실제와 유사한 복잡한 텍스트
        text = """
        Our innovative marketing platform provides comprehensive analytics 
        and competitive intelligence. The system analyzes social media content, 
        web scraping data, and customer feedback to generate actionable insights.
        """
        
        # When: 키워드 추출
        keywords = self.analyzer._extract_keywords(text)
        
        # Then: 의미있는 키워드들이 추출되어야 함
        expected_words = [
            "innovative", "marketing", "platform", "provides", "comprehensive", 
            "analytics", "competitive", "intelligence", "system", "analyzes", 
            "social", "media", "content", "web", "scraping", "data", "customer", 
            "feedback", "generate", "actionable", "insights"
        ]
        
        # 모든 예상 단어가 포함되어 있는지 확인
        for word in expected_words:
            assert word in keywords
        
        # 불용어가 제거되었는지 확인
        stop_words = ["our", "and", "the", "to"]
        for stop_word in stop_words:
            assert stop_word not in keywords 