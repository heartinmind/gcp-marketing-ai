# MarketingAI MVP - 권장 프로젝트 구조

```
marketing-ai/
│
├─ marketing-ai.code-workspace          # Cursor 워크스페이스 정의
├─ .cursor/
│  ├─ rules                            # LLM 행동 지침
│  └─ prompts/                         # 커스텀 프롬프트 템플릿
│
├─ infra/                              # 인프라 & DevOps
│  ├─ terraform/                       # GCP 리소스 정의
│  │  ├─ environments/
│  │  │  ├─ dev/
│  │  │  ├─ staging/
│  │  │  └─ prod/
│  │  ├─ modules/
│  │  └─ scripts/
│  ├─ k8s/                            # Kubernetes 매니페스트
│  ├─ docker/                         # Dockerfile들
│  └─ cicd/                           # GitHub Actions / Cloud Build
│
├─ data-pipelines/                     # 데이터 수집 & 처리
│  ├─ collectors/                      # 다양한 소스별 크롤러
│  │  ├─ web-crawler/                 # 웹사이트 크롤러 (현재 구현됨)
│  │  ├─ social-media/                # 소셜미디어 API 연동
│  │  │  ├─ instagram/
│  │  │  ├─ facebook/
│  │  │  ├─ youtube/
│  │  │  ├─ naver-blog/
│  │  │  └─ common/                   # 공통 유틸리티
│  │  └─ ad-platforms/                # 향후 광고 플랫폼 연동
│  ├─ processors/                     # 데이터 전처리 & 변환
│  │  ├─ text-processor/              # 텍스트 정제 및 키워드 추출
│  │  ├─ image-processor/             # 이미지 메타데이터 추출
│  │  └─ scheduler/                   # 수집 스케줄링
│  └─ storage/                        # 데이터 저장 관리
│     ├─ bigquery/                    # BigQuery 스키마 & 쿼리
│     └─ cloud-storage/               # 파일 저장 관리
│
├─ analytics/                          # 분석 엔진
│  ├─ engines/
│  │  ├─ keyword-analyzer/            # 키워드 빈도 분석
│  │  ├─ trend-analyzer/              # 발행 건수 트렌드
│  │  ├─ competitive-analyzer/        # 경쟁사 비교 분석
│  │  └─ basic-nlp/                   # 기본 자연어 처리
│  ├─ metrics/                        # 분석 지표 정의
│  └─ reports/                        # 리포트 생성기
│
├─ ml/                                 # AI/ML 모듈 (향후 확장)
│  ├─ training/                       # 모델 학습
│  │  ├─ text-classification/
│  │  ├─ sentiment-analysis/
│  │  └─ pipelines/                   # Vertex AI Pipelines
│  ├─ serving/                        # 모델 서빙
│  └─ experiments/                    # 실험 코드
│
├─ api/                               # 백엔드 API 서버
│  ├─ auth/                           # 인증 & 권한
│  ├─ endpoints/
│  │  ├─ competitors/                 # 경쟁사 설정 API
│  │  ├─ collections/                 # 데이터 수집 관리 API
│  │  ├─ analytics/                   # 분석 결과 API
│  │  └─ reports/                     # 리포트 API
│  ├─ models/                         # 데이터 모델 정의
│  ├─ middleware/                     # 미들웨어
│  └─ utils/                          # 공통 유틸리티
│
├─ dashboard/                          # 프론트엔드 UI
│  ├─ components/
│  │  ├─ competitor-management/       # 경쟁사 설정 UI
│  │  ├─ content-type-selector/       # 컨텐츠 유형 선택
│  │  ├─ schedule-manager/            # 분석 주기 설정
│  │  ├─ analytics-dashboard/         # 분석 결과 대시보드
│  │  └─ charts/                      # 차트 컴포넌트들
│  ├─ pages/
│  ├─ hooks/                          # React 커스텀 훅
│  ├─ services/                       # API 호출 서비스
│  └─ utils/
│
├─ notifications/                      # 알림 & 리포팅 시스템
│  ├─ email/                          # 이메일 발송
│  ├─ templates/                      # 리포트 템플릿
│  └─ schedulers/                     # 알림 스케줄러
│
├─ config/                            # 설정 관리
│  ├─ environments/                   # 환경별 설정
│  ├─ database/                       # DB 설정 & 마이그레이션
│  └─ secrets/                        # Secret Manager 연동
│
├─ tests/                             # 테스트 코드
│  ├─ unit/                           # 단위 테스트
│  ├─ integration/                    # 통합 테스트
│  ├─ e2e/                            # End-to-End 테스트
│  └─ fixtures/                       # 테스트 데이터
│
├─ docs/                              # 문서화
│  ├─ api/                            # API 문서
│  ├─ architecture/                   # 아키텍처 문서
│  ├─ deployment/                     # 배포 가이드
│  └─ user-guide/                     # 사용자 가이드
│
├─ scripts/                           # 유틸리티 스크립트
│  ├─ setup/                          # 초기 설정 스크립트
│  ├─ migration/                      # 데이터 마이그레이션
│  └─ monitoring/                     # 모니터링 스크립트
│
├─ shared/                            # 공통 라이브러리
│  ├─ utils/                          # 공통 유틸리티
│  ├─ constants/                      # 상수 정의
│  ├─ types/                          # 타입 정의
│  └─ exceptions/                     # 커스텀 예외
│
├─ .gitignore
├─ .env.example
├─ docker-compose.yml                 # 로컬 개발환경
├─ package.json                       # 전체 프로젝트 dependencies
├─ requirements.txt                   # Python dependencies
└─ README.md
```

## 주요 개선사항

### 1. MVP 핵심 기능 지원
- **collectors/social-media/**: 소셜미디어 크롤링
- **api/endpoints/competitors/**: UI 기반 경쟁사 설정
- **dashboard/components/**: 사용자 친화적 UI
- **notifications/**: 이메일 리포팅

### 2. 확장성 확보
- **ml/**: AI/ML 기능 추가 준비
- **ad-platforms/**: 광고 플랫폼 연동 준비
- **analytics/engines/**: 다양한 분석 엔진

### 3. 운영 편의성
- **tests/**: 체계적인 테스트 구조
- **docs/**: 완전한 문서화
- **config/**: 환경별 설정 관리
- **monitoring/**: 시스템 모니터링

### 4. 개발 효율성
- **shared/**: 코드 재사용성 향상
- **scripts/**: 자동화 스크립트
- **.cursor/**: AI 개발 최적화 