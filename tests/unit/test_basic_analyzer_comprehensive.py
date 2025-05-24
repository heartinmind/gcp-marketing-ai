"""
BasicAnalyzer 포괄적 테스트
실제 비즈니스 로직과 전체 워크플로우를 검증하는 테스트
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import json
import time
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.analysis.basic_analyzer import BasicAnalyzer


class TestBasicAnalyzerComprehensive:
    """BasicAnalyzer의 모든 핵심 기능에 대한 포괄적 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출되는 설정"""
        self.analyzer = BasicAnalyzer()
        
        # 테스트용 샘플 데이터
        self.sample_competitor_data = [
            {
                'url': 'https://competitor.com/product',
                'page_title': 'AI Marketing Platform - Best Solution',
                'content': 'Our AI-powered marketing platform provides comprehensive analytics and competitive intelligence for modern businesses.',
                'meta_description': 'Best AI marketing solution',
                'collected_at': '2024-01-01T10:00:00',
                'content_hash': 'hash1'
            },
            {
                'url': 'https://competitor.com/pricing',
                'page_title': 'Pricing Plans - Affordable Solutions',
                'content': 'Choose from our flexible pricing plans designed for businesses of all sizes. Free trial available.',
                'meta_description': 'Affordable pricing plans',
                'collected_at': '2024-01-02T10:00:00',
                'content_hash': 'hash2'
            },
            {
                'url': 'https://competitor.com/about',
                'page_title': 'About Our Company - Innovation Leaders',
                'content': 'We are innovation leaders in marketing technology, serving thousands of customers worldwide.',
                'meta_description': 'About our innovative company',
                'collected_at': '2024-01-03T10:00:00',
                'content_hash': 'hash3'
            }
        ]
    
    def test_analyze_keywords_full_analysis(self):
        """키워드 분석의 전체 워크플로우 테스트"""
        # When: 키워드 분석 실행
        result = self.analyzer.analyze_keywords(self.sample_competitor_data)
        
        # Then: 분석 결과가 올바른 구조를 가져야 함
        assert 'total_content_pieces' in result
        assert 'unique_words' in result
        assert 'word_frequency' in result
        assert 'top_keywords' in result
        assert 'analysis_summary' in result
        
        # 실제 데이터가 분석되었는지 확인
        assert result['total_content_pieces'] == 3
        assert result['unique_words'] > 0
        assert isinstance(result['word_frequency'], dict)
        assert len(result['top_keywords']) <= 20
        
        # 예상 키워드들이 포함되어 있는지 확인
        all_keywords = list(result['word_frequency'].keys())
        expected_keywords = ['marketing', 'platform', 'business', 'pricing']
        for keyword in expected_keywords:
            assert keyword in all_keywords
    
    def test_analyze_keywords_empty_data(self):
        """빈 데이터에 대한 키워드 분석 테스트"""
        # When: 빈 데이터로 키워드 분석
        result = self.analyzer.analyze_keywords([])
        
        # Then: 빈 결과가 반환되어야 함
        assert result == {}
    
    def test_analyze_keywords_invalid_data(self):
        """잘못된 형식의 데이터에 대한 에러 처리 테스트"""
        # Given: 잘못된 형식의 데이터
        invalid_data = [{'invalid': 'data'}]
        
        # When: 분석 실행
        result = self.analyzer.analyze_keywords(invalid_data)
        
        # Then: 에러가 발생하지 않고 빈 결과 반환
        assert result == {}
    
    def test_analyze_content_changes_basic(self):
        """콘텐츠 변경 분석 기본 기능 테스트"""
        # When: 콘텐츠 변경 분석 실행
        result = self.analyzer.analyze_content_changes(self.sample_competitor_data)
        
        # Then: 올바른 구조의 결과가 반환되어야 함
        assert 'total_pages_monitored' in result
        assert 'total_data_points' in result
        assert 'average_change_frequency' in result
        assert 'page_analysis' in result
        assert 'most_dynamic_pages' in result
        
        # 실제 분석이 수행되었는지 확인
        assert result['total_pages_monitored'] == 3
        assert result['total_data_points'] == 3
        assert isinstance(result['average_change_frequency'], float)
    
    def test_analyze_content_changes_duplicate_urls(self):
        """동일 URL의 여러 수집 데이터에 대한 변경 분석 테스트"""
        # Given: 동일 URL의 다른 시점 데이터
        duplicate_data = [
            {
                'url': 'https://competitor.com/product',
                'content': 'Version 1 content',
                'collected_at': '2024-01-01T10:00:00',
                'content_hash': 'hash1'
            },
            {
                'url': 'https://competitor.com/product',
                'content': 'Version 2 content (updated)',
                'collected_at': '2024-01-02T10:00:00',
                'content_hash': 'hash2'
            },
            {
                'url': 'https://competitor.com/product',
                'content': 'Version 2 content (updated)',  # 동일 내용
                'collected_at': '2024-01-03T10:00:00',
                'content_hash': 'hash2'  # 동일 해시
            }
        ]
        
        # When: 변경 분석 실행
        result = self.analyzer.analyze_content_changes(duplicate_data)
        
        # Then: 변경 빈도가 올바르게 계산되어야 함
        page_analysis = result['page_analysis']['https://competitor.com/product']
        assert page_analysis['total_collections'] == 3
        assert page_analysis['unique_versions'] == 2  # 2개의 고유 버전
        assert page_analysis['change_frequency'] == 2/3  # 2개 고유 버전 / 3개 수집
    
    def test_generate_competitor_summary_complete(self):
        """경쟁사 요약 분석 전체 기능 테스트"""
        # When: 경쟁사 요약 생성
        result = self.analyzer.generate_competitor_summary('Test Competitor', self.sample_competitor_data)
        
        # Then: 완전한 요약 구조가 반환되어야 함
        assert 'competitor_name' in result
        assert 'monitoring_summary' in result
        assert 'page_type_distribution' in result
        assert 'content_insights' in result
        
        # 경쟁사 이름이 올바르게 설정되었는지 확인
        assert result['competitor_name'] == 'Test Competitor'
        
        # 모니터링 요약 검증
        monitoring = result['monitoring_summary']
        assert monitoring['total_pages_monitored'] == 3
        assert monitoring['total_data_collections'] == 3
        assert 'latest_collection_date' in monitoring
        assert 'average_content_length' in monitoring
        
        # 페이지 유형 분포 검증
        page_types = result['page_type_distribution']
        assert isinstance(page_types, dict)
        assert 'product' in page_types or 'pricing' in page_types or 'about' in page_types
        
        # 콘텐츠 인사이트 검증
        insights = result['content_insights']
        assert 'shortest_content' in insights
        assert 'longest_content' in insights
        assert 'content_length_variance' in insights
    
    def test_generate_competitor_summary_empty_data(self):
        """빈 데이터에 대한 경쟁사 요약 테스트"""
        # When: 빈 데이터로 요약 생성
        result = self.analyzer.generate_competitor_summary('Empty Competitor', [])
        
        # Then: 빈 결과가 반환되어야 함
        assert result == {}
    
    def test_create_analysis_record_structure(self):
        """분석 레코드 생성 구조 테스트"""
        # Given: 분석 결과 데이터
        analysis_results = {
            'total_keywords': 150,
            'top_keywords': ['marketing', 'platform', 'analytics']
        }
        
        # When: 분석 레코드 생성
        record = self.analyzer.create_analysis_record(
            competitor_name='Test Competitor',
            analysis_type='keyword_analysis',
            results=analysis_results,
            summary='Found 150 unique keywords in competitor content'
        )
        
        # Then: 올바른 레코드 구조가 생성되어야 함
        assert 'id' in record
        assert 'competitor_name' in record
        assert 'analysis_type' in record
        assert 'analysis_date' in record
        assert 'results' in record
        assert 'summary' in record
        assert 'created_at' in record
        
        # 실제 값들이 올바르게 설정되었는지 확인
        assert record['competitor_name'] == 'Test Competitor'
        assert record['analysis_type'] == 'keyword_analysis'
        assert record['results'] == analysis_results
        assert record['summary'] == 'Found 150 unique keywords in competitor content'
    
    def test_page_type_analysis_accuracy(self):
        """페이지 유형 분석 정확성 테스트"""
        # Given: 다양한 페이지 유형의 URL들
        mixed_data = [
            {'url': 'https://competitor.com/product/ai-platform'},
            {'url': 'https://competitor.com/pricing/enterprise'},
            {'url': 'https://competitor.com/about/company'},
            {'url': 'https://competitor.com/blog/latest-news'},
            {'url': 'https://competitor.com/contact/support'},
            {'url': 'https://competitor.com/solutions/marketing'},
            {'url': 'https://competitor.com/home'}
        ]
        
        # When: 페이지 유형 분석 (private 메서드 직접 테스트)
        page_types = self.analyzer._analyze_page_types(mixed_data)
        
        # Then: 올바른 유형 분류가 되어야 함
        assert page_types['product'] == 1
        assert page_types['pricing'] == 1
        assert page_types['about'] == 1
        assert page_types['content'] == 1  # blog
        assert page_types['contact'] == 1
        assert page_types['service'] == 1  # solutions
        assert page_types['other'] == 1    # home
    
    def test_keyword_extraction_edge_cases(self):
        """키워드 추출의 엣지 케이스 테스트"""
        # Test case 1: 매우 긴 텍스트
        long_text = "marketing " * 1000 + "platform analytics"
        keywords = self.analyzer._extract_keywords(long_text)
        assert 'marketing' in keywords
        assert 'platform' in keywords
        assert 'analytics' in keywords
        
        # Test case 2: 특수 문자가 많은 텍스트
        special_text = "AI/ML-powered @marketing #platform & analytics 2024"
        keywords = self.analyzer._extract_keywords(special_text)
        expected = ['powered', 'marketing', 'platform', 'analytics']
        for word in expected:
            assert word in keywords
        
        # Test case 3: 다국어 혼합 텍스트
        mixed_text = "마케팅 marketing プラットフォーム platform"
        keywords = self.analyzer._extract_keywords(mixed_text)
        # 현재 구현은 isalpha()를 사용하므로 각 언어의 알파벳 문자를 인식
        assert len(keywords) > 0
    
    @patch('src.analysis.basic_analyzer.logger')
    def test_error_handling_with_logging(self, mock_logger):
        """에러 처리 및 로깅 테스트"""
        # Given: 에러를 발생시킬 수 있는 잘못된 데이터
        invalid_data = None
        
        # When: 분석 실행
        result = self.analyzer.analyze_keywords(invalid_data)
        
        # Then: 빈 결과 반환 및 에러 로깅 확인
        self.assertEqual(result['total_words'], 0)
        self.assertEqual(result['unique_words'], 0)
        mock_logger.warning.assert_called()
    
    def test_performance_with_large_dataset(self):
        """대용량 데이터에 대한 성능 테스트"""
        # Given: 대용량 테스트 데이터 생성
        large_data = []
        for i in range(100):
            large_data.append({
                'url': f'https://competitor.com/page{i}',
                'page_title': f'Page {i} Title',
                'content': f'This is content for page {i} with marketing analytics platform data ' * 10,
                'meta_description': f'Page {i} description',
                'collected_at': f'2024-01-{i%30+1:02d}T10:00:00',
                'content_hash': f'hash{i}'
            })
        
        # When: 분석 실행 (성능 측정)
        start_time = time.time()
        result = self.analyzer.analyze_keywords(large_data)
        end_time = time.time()
        
        # Then: 합리적인 시간 내에 완료되어야 함 (5초 이내)
        execution_time = end_time - start_time
        assert execution_time < 5.0
        
        # 결과가 올바르게 생성되었는지 확인
        assert result['total_content_pieces'] == 100
        assert result['unique_words'] > 0 