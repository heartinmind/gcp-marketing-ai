# 🚀 MarketingAI - 경쟁사 분석 자동화 플랫폼

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![GCP](https://img.shields.io/badge/Google_Cloud-supported-blue.svg)](https://cloud.google.com)
[![Terraform](https://img.shields.io/badge/Terraform-Infrastructure-purple.svg)](https://terraform.io)

> **엔터프라이즈급 경쟁사 소셜미디어 컨텐츠 분석 및 인사이트 자동화 플랫폼**

## 🎯 **프로젝트 목적**

MarketingAI는 경쟁사 소셜미디어 컨텐츠를 자동으로 수집, 분석하여 마케팅 인사이트를 제공하는 자동화 플랫폼입니다.

## 🏗️ **시스템 아키텍처**

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│ Data Pipeline│───▶│   ML Pipeline   │
│ Instagram, etc. │    │  Pub/Sub +   │    │  Vertex AI +    │
└─────────────────┘    │  Dataflow    │    │  Kubeflow       │
                       └──────────────┘    └─────────────────┘
                              │                       │
                              ▼                       ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Dashboard     │◀───│  BigQuery    │◀───│  Cloud Storage  │
│   Streamlit     │    │ Data Warehouse│    │   Data Lake     │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## 📁 **프로젝트 구조**

```
marketing-ai/
├── 📱 api/                     # FastAPI 서버
│   ├── main.py                 # 메인 애플리케이션
│   ├── routes/                 # API 라우터
│   └── models/                 # Pydantic 모델
├── 🔄 data-pipelines/          # 데이터 수집 파이프라인
│   ├── collectors/             # 소셜미디어 수집기
│   ├── processors/             # 데이터 처리기
│   └── schemas/                # Pub/Sub 스키마
├── 🧠 ml/                      # ML 파이프라인
│   ├── training/               # 모델 훈련
│   └── inference/              # 모델 추론
├── 📊 dashboard/               # Streamlit 대시보드
├── 🏗️ infra/                   # Terraform 인프라
├── 🔧 shared/                  # 공통 유틸리티
├── ⚙️ config/                  # 설정 파일
├── 📋 tests/                   # 테스트 파일
└── 📜 requirements.txt         # Python 의존성
```

## 🚀 **설치 및 설정 가이드**

### 📋 **사전 요구사항**

- **Python 3.9+**
- **Git**
- **Google Cloud Platform 계정** (선택사항, 배포시 필요)

### 1️⃣ **프로젝트 복제**

```bash
# GitHub에서 프로젝트 복제
git clone https://github.com/heartinmind/gcp-marketing-ai.git
cd marketing-ai
```

### 2️⃣ **가상환경 생성 및 활성화**

```bash
# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 가상환경 활성화 확인 (프롬프트에 (venv) 표시됨)
which python  # venv/bin/python 경로가 표시되어야 함
```

### 3️⃣ **의존성 설치**

```bash
# requirements.txt에서 모든 의존성 설치
pip install -r requirements.txt

# 설치 확인
pip list | grep fastapi
pip list | grep streamlit
```

### 4️⃣ **환경 변수 설정** (선택사항)

```bash
# .env 파일 생성 (GCP 배포시 필요)
cp .env.example .env
# .env 파일을 편집하여 필요한 설정값 입력
```

## 🖥️ **애플리케이션 실행 방법**

### 🚀 **FastAPI 서버 실행**

```bash
# 개발 모드로 FastAPI 서버 시작 (핫 리로드 포함)
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 또는 간단하게
uvicorn api.main:app --reload

# 서버 접속 확인
# 브라우저에서 http://localhost:8000 접속
# API 문서: http://localhost:8000/docs
```

**FastAPI 서버 옵션:**
- `--host 0.0.0.0`: 모든 네트워크 인터페이스에서 접근 가능
- `--port 8000`: 포트 번호 지정
- `--reload`: 코드 변경시 자동 재시작 (개발용)
- `--log-level info`: 로그 레벨 설정

### 📊 **Streamlit 대시보드 실행**

```bash
# 새 터미널 탭에서 Streamlit 대시보드 시작
streamlit run dashboard/streamlit_app.py --server.port 8501

# 대시보드 접속
# 브라우저에서 http://localhost:8501 접속
```

### 🔄 **동시 실행 (개발용)**

```bash
# 백그라운드에서 FastAPI 서버 실행
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Streamlit 대시보드 실행
streamlit run dashboard/streamlit_app.py --server.port 8501

# 백그라운드 프로세스 확인
jobs

# 백그라운드 프로세스 종료
kill %1  # FastAPI 서버 종료
```

## 🧪 **테스트 실행 방법**

### 📋 **테스트 환경 설정**

```bash
# 테스트용 의존성이 이미 requirements.txt에 포함되어 있음
# pytest, pytest-cov 등이 설치되어 있는지 확인
pip list | grep pytest
```

### 🔍 **단위 테스트 실행**

```bash
# 모든 테스트 실행
pytest

# 상세한 출력과 함께 테스트 실행
pytest -v

# 특정 테스트 파일만 실행
pytest tests/unit/test_api.py

# 특정 테스트 함수만 실행
pytest tests/unit/test_api.py::test_health_check

# 테스트 커버리지 포함
pytest --cov=api --cov=data-pipelines --cov-report=html

# 실패한 테스트만 재실행
pytest --lf
```

### 📊 **테스트 결과 확인**

```bash
# 테스트 커버리지 리포트 확인 (HTML)
# htmlcov/index.html 파일을 브라우저에서 열기

# 테스트 커버리지 리포트 (터미널)
pytest --cov=api --cov=data-pipelines --cov-report=term
```

### 🔧 **통합 테스트**

```bash
# API 통합 테스트 (서버가 실행 중이어야 함)
pytest tests/integration/

# 시스템 전체 테스트
python test_system.py
```

## 🔧 **개발 워크플로우**

### **코드 품질 체크**

```bash
# 코드 린팅 및 포맷팅
ruff check .
ruff format .

# 타입 체크
mypy api/ data-pipelines/

# 전체 품질 체크 파이프라인
ruff check . && mypy . && pytest
```

### **로컬 개발 서버**

```bash
# API 서버 (개발 모드)
python -m uvicorn api.main:app --reload

# 대시보드 (개발 모드)
streamlit run dashboard/streamlit_app.py
```

## 🚀 **GCP 클라우드 배포**

### **Terraform으로 인프라 배포**

```bash
cd infra

# Terraform 초기화
terraform init

# 배포 계획 확인
terraform plan -var="project_id=your-gcp-project-id"

# 인프라 배포
terraform apply -var="project_id=your-gcp-project-id"
```

### **Cloud Build로 애플리케이션 배포**

```bash
# Cloud Build 제출
gcloud builds submit --config=cloudbuild.yaml

# 배포 상태 확인
gcloud run services list
```

## 📊 **API 문서**

FastAPI 서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI 스키마**: http://localhost:8000/openapi.json

## 🛠️ **기술 스택**

### **Backend & API**
- **FastAPI**: 고성능 웹 API 프레임워크
- **Pydantic**: 데이터 검증 및 설정 관리
- **Uvicorn**: ASGI 웹 서버

### **데이터 & ML**
- **Google Cloud BigQuery**: 데이터 웨어하우스
- **Cloud Storage**: 데이터 레이크
- **Pub/Sub**: 실시간 메시징
- **Vertex AI**: ML 파이프라인 및 모델 관리
- **Scikit-learn**: 머신러닝 라이브러리

### **Frontend & 시각화**
- **Streamlit**: 대시보드 프레임워크
- **Plotly**: 인터랙티브 차트

### **인프라 & DevOps**
- **Terraform**: Infrastructure as Code
- **Cloud Build**: CI/CD 파이프라인
- **Cloud Run**: 컨테이너 서비스
- **Docker**: 컨테이너화

### **코드 품질**
- **Ruff**: 린터 및 포맷터
- **MyPy**: 정적 타입 체크
- **Pytest**: 테스트 프레임워크

## 🔧 **트러블슈팅**

### **일반적인 문제들**

#### 1. Python 명령어를 찾을 수 없음
```bash
# 가상환경이 활성화되었는지 확인
source venv/bin/activate

# Python 경로 확인
which python
```

#### 2. 의존성 설치 오류
```bash
# pip 업그레이드
pip install --upgrade pip

# 의존성 재설치
pip install -r requirements.txt --force-reinstall
```

#### 3. 포트 충돌
```bash
# 다른 포트 사용
uvicorn api.main:app --port 8001

# 또는 실행 중인 프로세스 확인
lsof -i :8000
```

## 🤝 **기여하기**

1. Fork 프로젝트
2. Feature 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📝 **라이선스**

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 **지원 & 문의**

- **이슈 리포트**: [GitHub Issues](https://github.com/heartinmind/gcp-marketing-ai/issues)
- **기능 요청**: [GitHub Discussions](https://github.com/heartinmind/gcp-marketing-ai/discussions)

---

**⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!**

Made with ❤️ by MarketingAI Team 