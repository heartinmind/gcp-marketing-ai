"""
MarketingAI ML 파이프라인

Vertex AI Pipelines를 사용한 경쟁사 컨텐츠 분석 모델 훈련 파이프라인
"""

import logging

import joblib
import pandas as pd
from google.cloud import aiplatform
from kfp.dsl import Dataset, Metrics, Model, component, pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@component(
    base_image="python:3.9",
    packages_to_install=[
        "pandas==2.0.3",
        "scikit-learn==1.3.0",
        "google-cloud-bigquery==3.11.4",
        "google-cloud-storage==2.10.0"
    ]
)
def extract_data_component(
    project_id: str,
    dataset_id: str,
    table_id: str
) -> Dataset:
    """
    BigQuery에서 훈련 데이터를 추출하는 컴포넌트
    """
    import pandas as pd
    from google.cloud import bigquery

    # BigQuery 클라이언트 초기화
    client = bigquery.Client(project=project_id)

    # 데이터 추출 쿼리
    query = f"""
    SELECT 
        id,
        competitor_name,
        platform,
        content,
        JSON_EXTRACT_SCALAR(engagement_metrics, '$.likes_count') as likes,
        JSON_EXTRACT_SCALAR(engagement_metrics, '$.comments_count') as comments,
        CASE 
            WHEN JSON_EXTRACT_SCALAR(engagement_metrics, '$.likes_count') > 100 THEN 'high_engagement'
            WHEN JSON_EXTRACT_SCALAR(engagement_metrics, '$.likes_count') > 50 THEN 'medium_engagement'
            ELSE 'low_engagement'
        END as engagement_level,
        collected_at
    FROM `{project_id}.{dataset_id}.{table_id}`
    WHERE content IS NOT NULL
    AND collected_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    """

    # 데이터 추출
    df = client.query(query).to_dataframe()

    # 데이터 저장
    output_path = "/tmp/extracted_data.csv"
    df.to_csv(output_path, index=False)

    logger.info(f"데이터 추출 완료: {len(df)} 행")

    return Dataset(
        uri=output_path,
        metadata={
            "rows": len(df),
            "columns": list(df.columns),
            "extracted_at": pd.Timestamp.now().isoformat()
        }
    )


@component(
    base_image="python:3.9",
    packages_to_install=[
        "pandas==2.0.3",
        "scikit-learn==1.3.0",
        "nltk==3.8.1",
        "konlpy==0.6.0"
    ]
)
def preprocess_data_component(
    input_data: Dataset
) -> Dataset:
    """
    데이터 전처리 컴포넌트
    """
    import re

    import pandas as pd

    # 데이터 로드
    df = pd.read_csv(input_data.uri)

    # 텍스트 전처리 함수
    def clean_text(text):
        if pd.isna(text):
            return ""

        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', str(text))

        # 특수문자 정리 (한글, 영문, 숫자, 공백만 유지)
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)

        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    # 텍스트 전처리 적용
    df['cleaned_content'] = df['content'].apply(clean_text)

    # 빈 컨텐츠 제거
    df = df[df['cleaned_content'].str.len() > 10]

    # 학습/테스트 데이터 분할
    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        stratify=df['engagement_level'],
        random_state=42
    )

    # 데이터 저장
    train_path = "/tmp/train_data.csv"
    test_path = "/tmp/test_data.csv"

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    logger.info(f"전처리 완료 - 훈련: {len(train_df)}, 테스트: {len(test_df)}")

    return Dataset(
        uri=train_path,
        metadata={
            "train_rows": len(train_df),
            "test_rows": len(test_df),
            "test_path": test_path,
            "features": ["cleaned_content", "platform", "competitor_name"],
            "target": "engagement_level"
        }
    )


@component(
    base_image="python:3.9",
    packages_to_install=[
        "pandas==2.0.3",
        "scikit-learn==1.3.0",
        "joblib==1.3.2"
    ]
)
def train_model_component(
    train_data: Dataset
) -> Model:
    """
    ML 모델 훈련 컴포넌트
    """
    import joblib
    import pandas as pd
    from sklearn.compose import ColumnTransformer

    # 훈련 데이터 로드
    train_df = pd.read_csv(train_data.uri)

    # 특성과 타겟 분리
    X = train_df[['cleaned_content', 'platform']]
    y = train_df['engagement_level']

    # 파이프라인 구성
    text_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english'
        ))
    ])

    # 컬럼 변환기 (텍스트만 사용)
    preprocessor = ColumnTransformer([
        ('text', text_pipeline, 'cleaned_content')
    ], remainder='drop')

    # 전체 ML 파이프라인
    ml_pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', MultinomialNB(alpha=0.1))
    ])

    # 모델 훈련
    logger.info("모델 훈련 시작...")
    ml_pipeline.fit(X, y)

    # 모델 저장
    model_path = "/tmp/engagement_prediction_model.joblib"
    joblib.dump(ml_pipeline, model_path)

    logger.info("모델 훈련 완료")

    return Model(
        uri=model_path,
        metadata={
            "model_type": "MultinomialNB",
            "features": ["cleaned_content"],
            "target_classes": list(y.unique()),
            "training_samples": len(train_df)
        }
    )


@component(
    base_image="python:3.9",
    packages_to_install=[
        "pandas==2.0.3",
        "scikit-learn==1.3.0",
        "joblib==1.3.2"
    ]
)
def evaluate_model_component(
    model: Model,
    train_data: Dataset
) -> Metrics:
    """
    모델 평가 컴포넌트
    """

    import pandas as pd

    # 모델 로드
    ml_pipeline = joblib.load(model.uri)

    # 테스트 데이터 로드
    test_path = train_data.metadata.get("test_path", "/tmp/test_data.csv")
    test_df = pd.read_csv(test_path)

    # 예측
    X_test = test_df[['cleaned_content', 'platform']]
    y_test = test_df['engagement_level']
    y_pred = ml_pipeline.predict(X_test)

    # 평가 지표 계산
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    # 메트릭 저장
    metrics = {
        "accuracy": accuracy,
        "precision_macro": report['macro avg']['precision'],
        "recall_macro": report['macro avg']['recall'],
        "f1_macro": report['macro avg']['f1-score'],
        "test_samples": len(test_df)
    }

    logger.info(f"모델 평가 완료 - 정확도: {accuracy:.3f}")

    return Metrics(
        uri="/tmp/metrics.json",
        metadata=metrics
    )


@component(
    base_image="python:3.9",
    packages_to_install=[
        "google-cloud-storage==2.10.0",
        "joblib==1.3.2"
    ]
)
def deploy_model_component(
    model: Model,
    metrics: Metrics,
    project_id: str,
    model_bucket: str,
    min_accuracy: float = 0.7
) -> str:
    """
    모델 배포 컴포넌트
    """
    import json

    from google.cloud import storage

    # 최소 정확도 체크
    accuracy = metrics.metadata.get("accuracy", 0.0)

    if accuracy < min_accuracy:
        logger.warning(f"모델 정확도({accuracy:.3f})가 최소 기준({min_accuracy})보다 낮습니다.")
        return "deployment_skipped"

    # Cloud Storage에 모델 업로드
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(model_bucket)

    # 모델 파일 업로드
    model_blob_name = f"models/engagement_prediction/v_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}/model.joblib"
    model_blob = bucket.blob(model_blob_name)
    model_blob.upload_from_filename(model.uri)

    # 메타데이터 업로드
    metadata_blob_name = model_blob_name.replace('model.joblib', 'metadata.json')
    metadata_blob = bucket.blob(metadata_blob_name)
    metadata_blob.upload_from_string(json.dumps(metrics.metadata))

    model_uri = f"gs://{model_bucket}/{model_blob_name}"

    logger.info(f"모델 배포 완료: {model_uri}")

    return model_uri


@pipeline(
    name="marketing-ai-training-pipeline",
    description="MarketingAI 경쟁사 컨텐츠 참여도 예측 모델 훈련 파이프라인"
)
def marketing_ai_training_pipeline(
    project_id: str,
    dataset_id: str = "marketing_ai_dev",
    table_id: str = "competitors_data",
    model_bucket: str = "marketing-ai-models-dev",
    min_accuracy: float = 0.7
):
    """
    MarketingAI ML 훈련 파이프라인
    
    Args:
        project_id: GCP 프로젝트 ID
        dataset_id: BigQuery 데이터셋 ID
        table_id: BigQuery 테이블 ID
        model_bucket: 모델 저장용 Cloud Storage 버킷
        min_accuracy: 배포를 위한 최소 정확도
    """

    # 1. 데이터 추출
    extract_task = extract_data_component(
        project_id=project_id,
        dataset_id=dataset_id,
        table_id=table_id
    )

    # 2. 데이터 전처리
    preprocess_task = preprocess_data_component(
        input_data=extract_task.outputs["output"]
    )

    # 3. 모델 훈련
    train_task = train_model_component(
        train_data=preprocess_task.outputs["output"]
    )

    # 4. 모델 평가
    evaluate_task = evaluate_model_component(
        model=train_task.outputs["output"],
        train_data=preprocess_task.outputs["output"]
    )

    # 5. 모델 배포
    deploy_task = deploy_model_component(
        model=train_task.outputs["output"],
        metrics=evaluate_task.outputs["output"],
        project_id=project_id,
        model_bucket=model_bucket,
        min_accuracy=min_accuracy
    )


# 파이프라인 실행 함수
def run_pipeline(
    project_id: str,
    region: str = "us-central1",
    pipeline_root: str = None
):
    """
    Vertex AI에서 파이프라인 실행
    """
    if pipeline_root is None:
        pipeline_root = f"gs://{project_id}-marketing-ai-datalake-dev/pipeline_runs"

    # Vertex AI 초기화
    aiplatform.init(
        project=project_id,
        location=region
    )

    # 파이프라인 컴파일 및 실행
    from kfp import compiler

    compiler.Compiler().compile(
        pipeline_func=marketing_ai_training_pipeline,
        package_path="marketing_ai_pipeline.json"
    )

    # 파이프라인 작업 생성
    job = aiplatform.PipelineJob(
        display_name="marketing-ai-training",
        template_path="marketing_ai_pipeline.json",
        pipeline_root=pipeline_root,
        parameter_values={
            "project_id": project_id
        }
    )

    # 실행
    job.run(sync=True)

    logger.info("파이프라인 실행 완료")

    return job


if __name__ == "__main__":
    # 파이프라인 테스트 실행
    import os

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")

    run_pipeline(project_id=project_id)
