"""
BigQuery 클라이언트 모듈
데이터 저장 및 조회 기능을 제공합니다.
"""

from google.cloud import bigquery
from typing import List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)


class BigQueryClient:
    """BigQuery 클라이언트 클래스"""
    
    def __init__(self, project_id: str, dataset_id: str):
        """
        Args:
            project_id: GCP 프로젝트 ID
            dataset_id: BigQuery 데이터셋 ID
        """
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.dataset_ref = self.client.dataset(dataset_id)
    
    def insert_competitor_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        경쟁사 데이터를 BigQuery에 삽입합니다.
        
        Args:
            data: 삽입할 데이터 리스트
            
        Returns:
            성공 여부
        """
        try:
            table_ref = self.dataset_ref.table('competitor_data')
            table = self.client.get_table(table_ref)
            
            # 데이터 형식 변환
            rows_to_insert = []
            for row in data:
                formatted_row = {
                    'id': row['id'],
                    'competitor_name': row['competitor_name'],
                    'url': row['url'],
                    'page_title': row['page_title'],
                    'content': row['content'],
                    'meta_description': row['meta_description'],
                    'collected_at': row['collected_at'],
                    'content_hash': row['content_hash']
                }
                rows_to_insert.append(formatted_row)
            
            errors = self.client.insert_rows_json(table, rows_to_insert)
            
            if errors:
                logger.error(f"BigQuery 삽입 오류: {errors}")
                return False
            
            logger.info(f"{len(rows_to_insert)}개 행이 성공적으로 삽입되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"BigQuery 삽입 실패: {str(e)}")
            return False
    
    def insert_analysis_results(self, data: List[Dict[str, Any]]) -> bool:
        """
        분석 결과를 BigQuery에 삽입합니다.
        
        Args:
            data: 삽입할 분석 결과 리스트
            
        Returns:
            성공 여부
        """
        try:
            table_ref = self.dataset_ref.table('analysis_results')
            table = self.client.get_table(table_ref)
            
            # 데이터 형식 변환
            rows_to_insert = []
            for row in data:
                formatted_row = {
                    'id': row['id'],
                    'competitor_name': row['competitor_name'],
                    'analysis_type': row['analysis_type'],
                    'analysis_date': row['analysis_date'],
                    'results': json.dumps(row['results']) if row['results'] else None,
                    'summary': row['summary'],
                    'created_at': row['created_at']
                }
                rows_to_insert.append(formatted_row)
            
            errors = self.client.insert_rows_json(table, rows_to_insert)
            
            if errors:
                logger.error(f"BigQuery 삽입 오류: {errors}")
                return False
            
            logger.info(f"{len(rows_to_insert)}개 분석 결과가 성공적으로 삽입되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"BigQuery 삽입 실패: {str(e)}")
            return False
    
    def query_competitor_data(self, competitor_name: str = None, 
                            limit: int = 100) -> List[Dict]:
        """
        경쟁사 데이터를 조회합니다.
        
        Args:
            competitor_name: 특정 경쟁사 이름 (선택사항)
            limit: 조회할 최대 행 수
            
        Returns:
            조회된 데이터 리스트
        """
        try:
            query = f"""
            SELECT *
            FROM `{self.project_id}.{self.dataset_id}.competitor_data`
            """
            
            if competitor_name:
                query += f" WHERE competitor_name = '{competitor_name}'"
            
            query += f" ORDER BY collected_at DESC LIMIT {limit}"
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"데이터 조회 실패: {str(e)}")
            return []
    
    def get_latest_content_hash(self, competitor_name: str, url: str) -> str:
        """
        특정 URL의 최신 콘텐츠 해시를 조회합니다.
        
        Args:
            competitor_name: 경쟁사 이름
            url: URL
            
        Returns:
            최신 콘텐츠 해시 또는 빈 문자열
        """
        try:
            query = f"""
            SELECT content_hash
            FROM `{self.project_id}.{self.dataset_id}.competitor_data`
            WHERE competitor_name = '{competitor_name}' AND url = '{url}'
            ORDER BY collected_at DESC
            LIMIT 1
            """
            
            query_job = self.client.query(query)
            results = list(query_job.result())
            
            if results:
                return results[0]['content_hash'] or ""
            return ""
            
        except Exception as e:
            logger.error(f"해시 조회 실패: {str(e)}")
            return "" 
