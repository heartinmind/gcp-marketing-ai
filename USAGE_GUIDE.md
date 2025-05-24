# MarketingAI 사용 가이드

## 시작하기

### 1. 환경 설정 확인

```bash
# 가상 환경 활성화
source venv/bin/activate

# 의존성 설치 확인
pip install -r requirements.txt

# GCP 인증 확인
gcloud auth list
gcloud config get-value project
```

### 2. 시스템 테스트

```bash
# 전체 시스템 테스트 실행
python test_system.py
```

## 주요 기능 사용법

### 1. 데이터 수집 실행

```bash
# 메인 데이터 수집 스크립트 실행
python src/main.py
```

### 2. 경쟁사 설정 변경

`config/config.py` 파일에서 `COMPETITORS` 리스트를 수정하여 모니터링할 경쟁사를 설정할 수 있습니다:

```python
COMPETITORS = [
    {
        "name": "경쟁사1",
        "url": "https://competitor1.com",
        "target_pages": ["/products", "/pricing", "/about"]
    },
    {
        "name": "경쟁사2",
        "url": "https://competitor2.com",
        "target_pages": ["/solutions", "/pricing", "/company"]
    }
]
```

### 3. BigQuery 데이터 조회

```bash
# 수집된 데이터 조회
bq query --use_legacy_sql=false "
SELECT competitor_name, url, page_title, collected_at 
FROM \`marketing-ai-agent-460813.marketing_data.competitor_data\` 
ORDER BY collected_at DESC 
LIMIT 10"

# 분석 결과 조회
bq query --use_legacy_sql=false "
SELECT competitor_name, analysis_type, summary, created_at 
FROM \`marketing-ai-agent-460813.marketing_data.analysis_results\` 
ORDER BY created_at DESC 
LIMIT 10"
```

## 개별 모듈 사용법

### 웹 스크래퍼 사용

```python
from src.data_collection.web_scraper import WebScraper

scraper = WebScraper(delay=1)
competitor_config = {
    "name": "test_site",
    "url": "https://example.com",
    "target_pages": ["/", "/about"]
}

results = scraper.scrape_competitor(competitor_config)
```

### BigQuery 클라이언트 사용

```python
from src.utils.bigquery_client import BigQueryClient

bq_client = BigQueryClient("marketing-ai-agent-460813", "marketing_data")

# 데이터 저장
success = bq_client.insert_competitor_data(data_list)

# 데이터 조회
data = bq_client.query_competitor_data(competitor_name="test_site")
```

### 분석기 사용

```python
from src.analysis.basic_analyzer import BasicAnalyzer

analyzer = BasicAnalyzer()

# 키워드 분석
keyword_results = analyzer.analyze_keywords(competitor_data)

# 콘텐츠 변경 분석
change_results = analyzer.analyze_content_changes(competitor_data)

# 경쟁사 요약
summary = analyzer.generate_competitor_summary("competitor_name", competitor_data)
```

## 자동화 설정 (향후 확장)

### Cloud Functions 배포 준비

1. `functions/` 디렉토리에 Cloud Functions 코드 작성
2. `requirements.txt`를 functions 디렉토리에 복사
3. Cloud Functions 배포

### Cloud Scheduler 설정

```bash
# 매일 오전 9시 실행되는 스케줄러 생성
gcloud scheduler jobs create http marketing-data-collection \
    --schedule="0 9 * * *" \
    --uri="https://REGION-PROJECT_ID.cloudfunctions.net/collect-competitor-data" \
    --http-method=POST
```

## 문제 해결

### 일반적인 문제

1. **BigQuery 권한 오류**
   ```bash
   gcloud auth application-default login
   ```

2. **웹 스크래핑 실패**
   - 대상 웹사이트의 robots.txt 확인
   - 요청 지연 시간 증가 (`REQUEST_DELAY` 설정)

3. **메모리 부족**
   - 한 번에 처리하는 페이지 수 제한 (`MAX_PAGES_PER_SITE` 설정)

### 로그 확인

로그 레벨은 `config/config.py`의 `LOG_LEVEL` 설정으로 조정할 수 있습니다:

```python
LOG_LEVEL = "DEBUG"  # 상세한 로그
LOG_LEVEL = "INFO"   # 일반적인 로그
```

## 확장 가능성

### 1. AI/ML 분석 추가
- Vertex AI를 활용한 텍스트 감정 분석
- 이미지 분석 (로고, 제품 이미지)
- 자연어 처리를 통한 키워드 트렌드 분석

### 2. 실시간 모니터링
- Pub/Sub를 활용한 실시간 데이터 처리
- Cloud Monitoring을 통한 알림 설정

### 3. 대시보드 구축
- Data Studio를 활용한 시각화
- 웹 기반 대시보드 개발

### 4. 고급 분석
- 경쟁사 가격 변동 추적
- SEO 키워드 분석
- 소셜 미디어 모니터링 연동 