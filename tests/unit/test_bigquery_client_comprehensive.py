"""
BigQuery 클라이언트 포괄적 단위 테스트

실제 비즈니스 로직을 검증하는 의미있는 테스트들
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.bigquery_client import BigQueryClient


class TestBigQueryClientComprehensive:
    """BigQuery 클라이언트의 모든 핵심 기능에 대한 포괄적 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출되는 설정"""
        self.project_id = "test-project"
        self.dataset_id = "test_dataset"
        
        # 테스트용 샘플 데이터
        self.sample_competitor_data = [
            {
                'id': 'test-id-1',
                'competitor_name': 'Test Competitor 1',
                'url': 'https://competitor1.com/product',
                'page_title': 'Product Page - Competitor 1',
                'content': 'This is test content for competitor 1 product page.',
                'meta_description': 'Best product from competitor 1',
                'collected_at': '2024-01-01T10:00:00',
                'content_hash': 'hash123456'
            },
            {
                'id': 'test-id-2',
                'competitor_name': 'Test Competitor 1',
                'url': 'https://competitor1.com/pricing',
                'page_title': 'Pricing Page - Competitor 1',
                'content': 'Pricing information for competitor 1 services.',
                'meta_description': 'Affordable pricing plans',
                'collected_at': '2024-01-02T10:00:00',
                'content_hash': 'hash789012'
            }
        ]
        
        self.sample_analysis_results = [
            {
                'id': 'analysis-1',
                'competitor_name': 'Test Competitor 1',
                'analysis_type': 'keyword_analysis',
                'analysis_date': '2024-01-01',
                'results': {'total_keywords': 150, 'top_keywords': ['marketing', 'platform']},
                'summary': 'Found 150 unique keywords',
                'created_at': '2024-01-01T12:00:00'
            }
        ]
    
    @patch('google.cloud.bigquery.Client')
    def test_client_initialization(self, mock_bigquery_client):
        """BigQuery 클라이언트 초기화 테스트"""
        # When: 클라이언트 생성
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # Then: 올바르게 초기화되어야 함
        assert client.project_id == self.project_id
        assert client.dataset_id == self.dataset_id
        mock_bigquery_client.assert_called_once_with(project=self.project_id)
    
    @patch('google.cloud.bigquery.Client')
    def test_insert_competitor_data_success(self, mock_bigquery_client):
        """경쟁사 데이터 삽입 성공 테스트"""
        # Given: 성공적인 BigQuery 응답 모킹
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_table = Mock()
        mock_client_instance.get_table.return_value = mock_table
        mock_client_instance.insert_rows_json.return_value = []  # 에러 없음
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 데이터 삽입
        result = client.insert_competitor_data(self.sample_competitor_data)
        
        # Then: 성공해야 함
        assert result is True
        mock_client_instance.insert_rows_json.assert_called_once()
        
        # 삽입된 데이터 형식 검증
        call_args = mock_client_instance.insert_rows_json.call_args[0]
        inserted_rows = call_args[1]
        
        assert len(inserted_rows) == 2
        assert inserted_rows[0]['id'] == 'test-id-1'
        assert inserted_rows[0]['competitor_name'] == 'Test Competitor 1'
        assert inserted_rows[0]['url'] == 'https://competitor1.com/product'
    
    @patch('google.cloud.bigquery.Client')
    def test_insert_competitor_data_with_errors(self, mock_bigquery_client):
        """경쟁사 데이터 삽입 에러 테스트"""
        # Given: BigQuery 에러 응답 모킹
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_table = Mock()
        mock_client_instance.get_table.return_value = mock_table
        mock_client_instance.insert_rows_json.return_value = [
            {'index': 0, 'errors': [{'reason': 'invalid', 'message': 'Invalid data'}]}
        ]
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 데이터 삽입
        result = client.insert_competitor_data(self.sample_competitor_data)
        
        # Then: 실패해야 함
        assert result is False
    
    @patch('google.cloud.bigquery.Client')
    def test_insert_competitor_data_exception_handling(self, mock_bigquery_client):
        """경쟁사 데이터 삽입 예외 처리 테스트"""
        # Given: 예외를 발생시키는 BigQuery 클라이언트
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_client_instance.get_table.side_effect = Exception("Table not found")
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 데이터 삽입
        result = client.insert_competitor_data(self.sample_competitor_data)
        
        # Then: 예외가 처리되고 False 반환
        assert result is False
    
    @patch('google.cloud.bigquery.Client')
    def test_insert_analysis_results_success(self, mock_bigquery_client):
        """분석 결과 삽입 성공 테스트"""
        # Given: 성공적인 BigQuery 응답 모킹
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_table = Mock()
        mock_client_instance.get_table.return_value = mock_table
        mock_client_instance.insert_rows_json.return_value = []
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 분석 결과 삽입
        result = client.insert_analysis_results(self.sample_analysis_results)
        
        # Then: 성공해야 함
        assert result is True
        
        # 삽입된 데이터 형식 검증 (results가 JSON 문자열로 변환되었는지)
        call_args = mock_client_instance.insert_rows_json.call_args[0]
        inserted_rows = call_args[1]
        
        assert len(inserted_rows) == 1
        assert inserted_rows[0]['id'] == 'analysis-1'
        assert inserted_rows[0]['analysis_type'] == 'keyword_analysis'
        
        # results가 JSON 문자열로 변환되었는지 확인
        results_json = inserted_rows[0]['results']
        parsed_results = json.loads(results_json)
        assert parsed_results['total_keywords'] == 150
    
    @patch('google.cloud.bigquery.Client')
    def test_query_competitor_data_basic(self, mock_bigquery_client):
        """기본 경쟁사 데이터 조회 테스트"""
        # Given: 쿼리 결과 모킹
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_query_job = Mock()
        mock_result_row1 = {
            'id': 'test-id-1',
            'competitor_name': 'Test Competitor',
            'url': 'https://test.com',
            'page_title': 'Test Page',
            'content': 'Test content',
            'collected_at': '2024-01-01T10:00:00'
        }
        mock_result_row2 = {
            'id': 'test-id-2',
            'competitor_name': 'Test Competitor',
            'url': 'https://test.com/about',
            'page_title': 'About Page',
            'content': 'About content',
            'collected_at': '2024-01-02T10:00:00'
        }
        
        mock_query_job.result.return_value = [mock_result_row1, mock_result_row2]
        mock_client_instance.query.return_value = mock_query_job
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 데이터 조회
        results = client.query_competitor_data(limit=100)
        
        # Then: 올바른 결과가 반환되어야 함
        assert len(results) == 2
        assert results[0]['id'] == 'test-id-1'
        assert results[1]['id'] == 'test-id-2'
        
        # 올바른 쿼리가 실행되었는지 확인
        query_call_args = mock_client_instance.query.call_args[0][0]
        assert "SELECT *" in query_call_args
        assert "competitor_data" in query_call_args
        assert "ORDER BY collected_at DESC LIMIT 100" in query_call_args
    
    @patch('google.cloud.bigquery.Client')
    def test_query_competitor_data_with_filter(self, mock_bigquery_client):
        """특정 경쟁사 데이터 조회 테스트"""
        # Given: 쿼리 결과 모킹
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_query_job = Mock()
        mock_query_job.result.return_value = [{'id': 'filtered-id', 'competitor_name': 'Specific Competitor'}]
        mock_client_instance.query.return_value = mock_query_job
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 특정 경쟁사 데이터 조회
        results = client.query_competitor_data(competitor_name='Specific Competitor', limit=50)
        
        # Then: 필터링된 결과가 반환되어야 함
        assert len(results) == 1
        assert results[0]['competitor_name'] == 'Specific Competitor'
        
        # WHERE 절이 포함된 쿼리가 실행되었는지 확인
        query_call_args = mock_client_instance.query.call_args[0][0]
        assert "WHERE competitor_name = 'Specific Competitor'" in query_call_args
        assert "LIMIT 50" in query_call_args
    
    @patch('google.cloud.bigquery.Client')
    def test_query_competitor_data_exception_handling(self, mock_bigquery_client):
        """데이터 조회 예외 처리 테스트"""
        # Given: 예외를 발생시키는 쿼리
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_client_instance.query.side_effect = Exception("Query failed")
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 데이터 조회
        results = client.query_competitor_data()
        
        # Then: 빈 리스트가 반환되어야 함
        assert results == []
    
    @patch('google.cloud.bigquery.Client')
    def test_get_latest_content_hash_found(self, mock_bigquery_client):
        """최신 콘텐츠 해시 조회 성공 테스트"""
        # Given: 해시가 있는 쿼리 결과 모킹
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_query_job = Mock()
        mock_query_job.result.return_value = [{'content_hash': 'existing_hash_123'}]
        mock_client_instance.query.return_value = mock_query_job
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 최신 해시 조회
        hash_value = client.get_latest_content_hash('Test Competitor', 'https://test.com')
        
        # Then: 올바른 해시가 반환되어야 함
        assert hash_value == 'existing_hash_123'
        
        # 올바른 쿼리가 실행되었는지 확인
        query_call_args = mock_client_instance.query.call_args[0][0]
        assert "content_hash" in query_call_args
        assert "WHERE competitor_name = 'Test Competitor'" in query_call_args
        assert "AND url = 'https://test.com'" in query_call_args
        assert "ORDER BY collected_at DESC LIMIT 1" in query_call_args
    
    @patch('google.cloud.bigquery.Client')
    def test_get_latest_content_hash_not_found(self, mock_bigquery_client):
        """최신 콘텐츠 해시가 없는 경우 테스트"""
        # Given: 빈 쿼리 결과 모킹
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_query_job = Mock()
        mock_query_job.result.return_value = []
        mock_client_instance.query.return_value = mock_query_job
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 최신 해시 조회
        hash_value = client.get_latest_content_hash('New Competitor', 'https://new.com')
        
        # Then: 빈 문자열이 반환되어야 함
        assert hash_value == ""
    
    @patch('google.cloud.bigquery.Client')
    def test_get_latest_content_hash_null_value(self, mock_bigquery_client):
        """NULL 해시 값 처리 테스트"""
        # Given: NULL 해시가 있는 쿼리 결과 모킹
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_query_job = Mock()
        mock_query_job.result.return_value = [{'content_hash': None}]
        mock_client_instance.query.return_value = mock_query_job
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 최신 해시 조회
        hash_value = client.get_latest_content_hash('Test Competitor', 'https://test.com')
        
        # Then: 빈 문자열이 반환되어야 함
        assert hash_value == ""
    
    @patch('google.cloud.bigquery.Client')
    def test_get_latest_content_hash_exception_handling(self, mock_bigquery_client):
        """해시 조회 예외 처리 테스트"""
        # Given: 예외를 발생시키는 쿼리
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_client_instance.query.side_effect = Exception("Hash query failed")
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 해시 조회
        hash_value = client.get_latest_content_hash('Test Competitor', 'https://test.com')
        
        # Then: 빈 문자열이 반환되어야 함
        assert hash_value == ""
    
    @patch('google.cloud.bigquery.Client')
    def test_data_format_validation_competitor_data(self, mock_bigquery_client):
        """경쟁사 데이터 형식 검증 테스트"""
        # Given: 다양한 형식의 데이터
        test_data = [
            {
                'id': 'test-id',
                'competitor_name': 'Test Competitor',
                'url': 'https://test.com',
                'page_title': 'Test Page',
                'content': 'Test content',
                'meta_description': 'Test description',
                'collected_at': '2024-01-01T10:00:00',
                'content_hash': 'testhash123'
            }
        ]
        
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_table = Mock()
        mock_client_instance.get_table.return_value = mock_table
        mock_client_instance.insert_rows_json.return_value = []
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 데이터 삽입
        result = client.insert_competitor_data(test_data)
        
        # Then: 성공하고 올바른 형식으로 변환되어야 함
        assert result is True
        
        call_args = mock_client_instance.insert_rows_json.call_args[0]
        formatted_data = call_args[1][0]
        
        # 모든 필수 필드가 포함되어 있는지 확인
        required_fields = ['id', 'competitor_name', 'url', 'page_title', 'content', 
                          'meta_description', 'collected_at', 'content_hash']
        for field in required_fields:
            assert field in formatted_data
            assert formatted_data[field] == test_data[0][field]
    
    @patch('google.cloud.bigquery.Client')
    def test_data_format_validation_analysis_results(self, mock_bigquery_client):
        """분석 결과 데이터 형식 검증 테스트"""
        # Given: 복잡한 분석 결과 데이터
        test_analysis = [
            {
                'id': 'analysis-test',
                'competitor_name': 'Test Competitor',
                'analysis_type': 'comprehensive_analysis',
                'analysis_date': '2024-01-01',
                'results': {
                    'keywords': ['test', 'analysis'],
                    'metrics': {'score': 85.5, 'confidence': 0.92},
                    'nested': {'data': {'value': 100}}
                },
                'summary': 'Comprehensive analysis completed',
                'created_at': '2024-01-01T15:30:00'
            }
        ]
        
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_table = Mock()
        mock_client_instance.get_table.return_value = mock_table
        mock_client_instance.insert_rows_json.return_value = []
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 분석 결과 삽입
        result = client.insert_analysis_results(test_analysis)
        
        # Then: 성공하고 JSON 직렬화가 올바르게 되어야 함
        assert result is True
        
        call_args = mock_client_instance.insert_rows_json.call_args[0]
        formatted_data = call_args[1][0]
        
        # results가 JSON 문자열로 변환되었는지 확인
        assert isinstance(formatted_data['results'], str)
        parsed_results = json.loads(formatted_data['results'])
        assert parsed_results['keywords'] == ['test', 'analysis']
        assert parsed_results['metrics']['score'] == 85.5
        assert parsed_results['nested']['data']['value'] == 100
    
    @patch('google.cloud.bigquery.Client')
    @patch('src.utils.bigquery_client.logger')
    def test_logging_on_success(self, mock_logger, mock_bigquery_client):
        """성공시 로깅 테스트"""
        # Given: 성공적인 삽입
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_table = Mock()
        mock_client_instance.get_table.return_value = mock_table
        mock_client_instance.insert_rows_json.return_value = []
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 데이터 삽입
        client.insert_competitor_data(self.sample_competitor_data)
        
        # Then: 성공 로그가 기록되어야 함
        mock_logger.info.assert_called()
        success_log_calls = [call for call in mock_logger.info.call_args_list 
                           if '성공적으로 삽입' in str(call)]
        assert len(success_log_calls) > 0
    
    @patch('google.cloud.bigquery.Client')
    @patch('src.utils.bigquery_client.logger')
    def test_logging_on_error(self, mock_logger, mock_bigquery_client):
        """에러시 로깅 테스트"""
        # Given: 에러를 발생시키는 삽입
        mock_client_instance = Mock()
        mock_bigquery_client.return_value = mock_client_instance
        
        mock_client_instance.get_table.side_effect = Exception("Database error")
        
        client = BigQueryClient(self.project_id, self.dataset_id)
        
        # When: 데이터 삽입
        client.insert_competitor_data(self.sample_competitor_data)
        
        # Then: 에러 로그가 기록되어야 함
        mock_logger.error.assert_called()
        error_log_calls = [call for call in mock_logger.error.call_args_list 
                          if 'BigQuery' in str(call)]
        assert len(error_log_calls) > 0 