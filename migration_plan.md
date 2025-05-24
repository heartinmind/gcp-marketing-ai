# MarketingAI MVP 마이그레이션 계획

## 🎯 목표
현재 기본 웹 스크래핑 MVP를 경쟁사 컨텐츠 동향 분석 플랫폼으로 확장

## 📋 현재 상태 → 목표 상태

### 현재 구조:
```
GCP_MarketingAI/
├── src/
│   ├── data_collection/web_scraper.py
│   ├── analysis/basic_analyzer.py
│   ├── utils/bigquery_client.py
│   └── main.py
├── config/
└── tests/
```

### 목표 구조:
```
marketing-ai/ (새로운 멀티-루트 워크스페이스)
├── data-pipelines/collectors/
├── analytics/
├── api/
├── dashboard/
├── notifications/
└── 기타 모듈들...
```

## 🚀 단계별 마이그레이션 계획

### Phase 1: 기반 구조 구축 (1-2주)
1. **멀티-루트 워크스페이스 생성**
   - `marketing-ai.code-workspace` 파일 생성
   - `.cursor/rules` 설정

2. **기존 코드 재구성**
   - `src/data_collection/` → `data-pipelines/collectors/web-crawler/`
   - `src/analysis/` → `analytics/engines/`
   - `src/utils/` → `shared/utils/`

3. **기본 API 서버 구축**
   - FastAPI 기반 백엔드 API
   - 경쟁사 설정 CRUD API
   - BigQuery 연동 API

### Phase 2: 소셜미디어 크롤링 (2-3주)
1. **Instagram API 연동**
   - Instagram Basic Display API
   - 게시글 메타데이터 수집

2. **YouTube API 연동**
   - YouTube Data API v3
   - 채널/동영상 정보 수집

3. **네이버 블로그 크롤링**
   - 네이버 검색 API 활용
   - 블로그 포스트 수집

### Phase 3: 프론트엔드 UI 개발 (2-3주)
1. **React/Next.js 대시보드 구축**
   - 경쟁사 설정 페이지
   - 컨텐츠 유형 선택 UI
   - 분석 주기 설정

2. **분석 결과 시각화**
   - Chart.js/D3.js 기반 차트
   - 발행 건수 트렌드 차트
   - 키워드 빈도 테이블

### Phase 4: 고급 분석 기능 (1-2주)
1. **키워드 분석 엔진 개선**
   - TF-IDF 기반 키워드 추출
   - 토픽 모델링 (LDA)

2. **트렌드 분석**
   - 시계열 분석
   - 경쟁사 비교 분석

### Phase 5: 알림 및 리포팅 (1주)
1. **이메일 리포팅 시스템**
   - 주간/월간 자동 리포트
   - 사용자 맞춤 알림

2. **스케줄링 시스템**
   - Cloud Scheduler 기반 자동 실행
   - 사용자 정의 스케줄

## 📊 MVP 핵심 기능 우선순위

### 🥇 높은 우선순위 (Phase 1-2)
- [x] 웹사이트 크롤링 (완료)
- [ ] UI 기반 경쟁사 설정
- [ ] Instagram 크롤링
- [ ] YouTube 크롤링
- [ ] 기본 분석 (키워드, 발행건수)

### 🥈 중간 우선순위 (Phase 3)
- [ ] 분석 결과 시각화
- [ ] 네이버 블로그 크롤링
- [ ] Facebook 크롤링
- [ ] 분석 주기 설정

### 🥉 낮은 우선순위 (Phase 4-5)
- [ ] 이메일 리포팅
- [ ] 고급 분석 기능
- [ ] 실시간 알림
- [ ] 사용자 권한 관리

## 🛠 기술 스택 결정

### 백엔드
- **API**: FastAPI (Python)
- **DB**: BigQuery + Cloud SQL (메타데이터)
- **큐잉**: Cloud Pub/Sub
- **스케줄링**: Cloud Scheduler
- **컨테이너**: Docker + Cloud Run

### 프론트엔드
- **프레임워크**: Next.js (React)
- **상태관리**: Zustand 또는 Redux Toolkit
- **차트**: Chart.js + react-chartjs-2
- **UI**: Tailwind CSS + Headless UI

### 데이터 파이프라인
- **수집**: Python (requests, BeautifulSoup, API clients)
- **처리**: Cloud Dataflow 또는 Cloud Functions
- **저장**: BigQuery + Cloud Storage

### 인프라
- **IaC**: Terraform
- **CI/CD**: GitHub Actions + Cloud Build
- **모니터링**: Cloud Monitoring + Logging

## 📅 타임라인 (총 8-10주)

| 주차 | Phase | 주요 작업 |
|------|-------|-----------|
| 1-2  | Phase 1 | 구조 재편, API 서버 구축 |
| 3-5  | Phase 2 | 소셜미디어 크롤링 개발 |
| 6-8  | Phase 3 | 프론트엔드 UI 개발 |
| 9    | Phase 4 | 고급 분석 기능 |
| 10   | Phase 5 | 알림/리포팅 시스템 |

## 🎯 다음 단계

1. **멀티-루트 워크스페이스 설정**
2. **기존 코드 리팩토링**
3. **FastAPI 기반 API 서버 구축**
4. **Instagram API 연동 개발** 