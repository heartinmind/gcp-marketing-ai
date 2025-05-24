"""
MarketingAI 프로젝트 설정 파일
"""

import os

# GCP 프로젝트 설정
PROJECT_ID = "marketing-ai-agent-460813"
REGION = "us-central1"
DATASET_ID = "marketing_data"

# BigQuery 테이블 설정
COMPETITOR_DATA_TABLE = "competitor_data"
ANALYSIS_RESULTS_TABLE = "analysis_results"

# Cloud Storage 설정
BUCKET_NAME = f"{PROJECT_ID}-marketing-data"

# 경쟁사 목록 (예시)
COMPETITORS = [
    {
        "name": "competitor_1",
        "url": "https://example1.com",
        "target_pages": ["/products", "/pricing", "/about"]
    },
    {
        "name": "competitor_2", 
        "url": "https://example2.com",
        "target_pages": ["/solutions", "/pricing", "/company"]
    }
]

# 데이터 수집 설정
COLLECTION_SCHEDULE = "0 9 * * *"  # 매일 오전 9시
MAX_PAGES_PER_SITE = 10
REQUEST_DELAY = 1  # 초 단위

# 환경별 설정
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    LOG_LEVEL = "INFO"
else:
    LOG_LEVEL = "DEBUG" 