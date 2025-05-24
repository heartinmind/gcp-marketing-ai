# MarketingAI 프로젝트 GCP 인프라
# Terraform 설정

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# 변수 정의
variable "project_id" {
  description = "GCP 프로젝트 ID"
  type        = string
}

variable "region" {
  description = "기본 리전"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "환경 (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# Provider 설정
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# 데이터 소스
data "google_project" "project" {
  project_id = var.project_id
}

# 로컬 변수
locals {
  common_labels = {
    project     = "marketing-ai"
    environment = var.environment
    managed_by  = "terraform"
  }
}

# ====== 스토리지 ======

# 데이터 레이크용 Cloud Storage
resource "google_storage_bucket" "data_lake" {
  name     = "${var.project_id}-marketing-ai-datalake-${var.environment}"
  location = var.region
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  
  labels = local.common_labels
}

# ML 모델 저장용 버킷
resource "google_storage_bucket" "ml_models" {
  name     = "${var.project_id}-marketing-ai-models-${var.environment}"
  location = var.region
  
  uniform_bucket_level_access = true
  
  labels = local.common_labels
}

# ====== BigQuery ======

# 데이터 웨어하우스
resource "google_bigquery_dataset" "marketing_dw" {
  dataset_id  = "marketing_ai_${var.environment}"
  description = "MarketingAI 데이터 웨어하우스"
  location    = var.region
  
  labels = local.common_labels
  
  access {
    role          = "OWNER"
    user_by_email = data.google_project.project.editors[0]
  }
}

# 경쟁사 데이터 테이블
resource "google_bigquery_table" "competitors_data" {
  dataset_id = google_bigquery_dataset.marketing_dw.dataset_id
  table_id   = "competitors_data"
  
  schema = jsonencode([
    {
      name = "id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "competitor_name"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "platform"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "content"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "engagement_metrics"
      type = "JSON"
      mode = "NULLABLE"
    },
    {
      name = "collected_at"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    }
  ])
  
  labels = local.common_labels
}

# ====== Pub/Sub ======

# 데이터 수집 작업 토픽
resource "google_pubsub_topic" "collection_tasks" {
  name = "marketing-ai-collection-tasks-${var.environment}"
  
  labels = local.common_labels
}

# 수집 결과 토픽  
resource "google_pubsub_topic" "collection_results" {
  name = "marketing-ai-collection-results-${var.environment}"
  
  labels = local.common_labels
}

# 분석 작업 토픽
resource "google_pubsub_topic" "analysis_tasks" {
  name = "marketing-ai-analysis-tasks-${var.environment}"
  
  labels = local.common_labels
}

# ====== Cloud Functions ======

# 데이터 수집 함수용 소스 버킷
resource "google_storage_bucket" "functions_source" {
  name     = "${var.project_id}-functions-source-${var.environment}"
  location = var.region
  
  labels = local.common_labels
}

# ====== Cloud Run ======

# API 서버용 Cloud Run 서비스
resource "google_cloud_run_service" "api_server" {
  name     = "marketing-ai-api-${var.environment}"
  location = var.region
  
  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/marketing-ai-api:latest"
        
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }
    
    metadata {
      labels = local.common_labels
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Cloud Run 서비스에 대한 IAM 정책
resource "google_cloud_run_service_iam_member" "api_server_public" {
  count = var.environment == "dev" ? 1 : 0
  
  service  = google_cloud_run_service.api_server.name
  location = google_cloud_run_service.api_server.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ====== Vertex AI ======

# Vertex AI 데이터셋
resource "google_vertex_ai_dataset" "marketing_dataset" {
  provider     = google-beta
  display_name = "marketing-ai-dataset-${var.environment}"
  region       = var.region
  
  metadata_schema_uri = "gs://google-cloud-aiplatform/schema/dataset/metadata/text_1.0.0.yaml"
  
  labels = local.common_labels
}

# ====== IAM ======

# 서비스 계정
resource "google_service_account" "marketing_ai_sa" {
  account_id   = "marketing-ai-${var.environment}"
  display_name = "MarketingAI Service Account"
  description  = "MarketingAI 워크플로우용 서비스 계정"
}

# 서비스 계정 권한
resource "google_project_iam_member" "marketing_ai_permissions" {
  for_each = toset([
    "roles/bigquery.dataEditor",
    "roles/storage.objectAdmin",
    "roles/pubsub.editor",
    "roles/aiplatform.user",
    "roles/cloudfunctions.invoker"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.marketing_ai_sa.email}"
}

# ====== 출력 값 ======

output "data_lake_bucket" {
  description = "데이터 레이크 버킷 이름"
  value       = google_storage_bucket.data_lake.name
}

output "ml_models_bucket" {
  description = "ML 모델 버킷 이름"  
  value       = google_storage_bucket.ml_models.name
}

output "bigquery_dataset" {
  description = "BigQuery 데이터셋 ID"
  value       = google_bigquery_dataset.marketing_dw.dataset_id
}

output "api_server_url" {
  description = "API 서버 URL"
  value       = google_cloud_run_service.api_server.status[0].url
}

output "service_account_email" {
  description = "서비스 계정 이메일"
  value       = google_service_account.marketing_ai_sa.email
} 