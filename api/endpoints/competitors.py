"""
경쟁사 관리 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import uuid4
from datetime import datetime
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from api.models.competitor import (
        CompetitorModel, 
        CompetitorCreate, 
        CompetitorUpdate,
        CompetitorStats
    )
    from shared.utils.bigquery_client import BigQueryClient
except ImportError:
    from ..models.competitor import (
        CompetitorModel, 
        CompetitorCreate, 
        CompetitorUpdate,
        CompetitorStats
    )
    try:
        from ...shared.utils.bigquery_client import BigQueryClient
    except ImportError:
        # BigQuery 클라이언트가 없는 경우 더미 클래스 사용
        class BigQueryClient:
            def __init__(self):
                pass

router = APIRouter()

# BigQuery 클라이언트 의존성
def get_bigquery_client() -> BigQueryClient:
    return BigQueryClient()


@router.get("/", response_model=List[CompetitorModel])
async def get_competitors(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(10, ge=1, le=100, description="가져올 항목 수"),
    is_active: Optional[bool] = Query(None, description="활성 상태 필터"),
    bigquery_client: BigQueryClient = Depends(get_bigquery_client)
) -> List[CompetitorModel]:
    """
    등록된 경쟁사 목록을 조회합니다.
    """
    try:
        # BigQuery에서 경쟁사 목록 조회
        # 임시로 더미 데이터 반환
        competitors = [
            CompetitorModel(
                id=str(uuid4()),
                name="경쟁사 A",
                description="주요 경쟁사",
                content_types=["website", "instagram"],
                analysis_frequency="weekly",
                is_active=True,
                urls={"website": "https://competitor-a.com", "instagram": "@competitor_a"},
                keywords=["마케팅", "브랜딩"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        return competitors
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"경쟁사 목록 조회 실패: {str(e)}")


@router.post("/", response_model=CompetitorModel)
async def create_competitor(
    competitor: CompetitorCreate,
    bigquery_client: BigQueryClient = Depends(get_bigquery_client)
) -> CompetitorModel:
    """
    새로운 경쟁사를 등록합니다.
    """
    try:
        # 고유 ID 생성
        competitor_id = str(uuid4())
        current_time = datetime.now()
        
        # BigQuery에 저장하는 로직 (추후 구현)
        # 지금은 생성된 모델만 반환
        
        return CompetitorModel(
            id=competitor_id,
            name=competitor.name,
            description=competitor.description,
            content_types=competitor.content_types,
            analysis_frequency=competitor.analysis_frequency,
            is_active=competitor.is_active,
            urls=competitor.urls,
            keywords=competitor.keywords or [],
            created_at=current_time,
            updated_at=current_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"경쟁사 생성 실패: {str(e)}")


@router.get("/{competitor_id}", response_model=CompetitorModel)
async def get_competitor(
    competitor_id: str,
    bigquery_client: BigQueryClient = Depends(get_bigquery_client)
) -> CompetitorModel:
    """
    특정 경쟁사의 상세 정보를 조회합니다.
    """
    try:
        # BigQuery에서 경쟁사 조회 (추후 구현)
        # 임시 더미 데이터 반환
        
        return CompetitorModel(
            id=competitor_id,
            name="경쟁사 A",
            description="주요 경쟁사",
            content_types=["website", "instagram"],
            analysis_frequency="weekly",
            is_active=True,
            urls={"website": "https://competitor-a.com", "instagram": "@competitor_a"},
            keywords=["마케팅", "브랜딩"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
    except Exception:
        raise HTTPException(status_code=404, detail=f"경쟁사를 찾을 수 없습니다: {competitor_id}")


@router.put("/{competitor_id}", response_model=CompetitorModel)
async def update_competitor(
    competitor_id: str,
    competitor_update: CompetitorUpdate,
    bigquery_client: BigQueryClient = Depends(get_bigquery_client)
) -> CompetitorModel:
    """
    경쟁사 정보를 업데이트합니다.
    """
    try:
        # 기존 경쟁사 조회 및 업데이트 로직 (추후 구현)
        
        return CompetitorModel(
            id=competitor_id,
            name=competitor_update.name or "경쟁사 A",
            description=competitor_update.description,
            content_types=competitor_update.content_types or ["website"],
            analysis_frequency=competitor_update.analysis_frequency or "weekly",
            is_active=competitor_update.is_active if competitor_update.is_active is not None else True,
            urls=competitor_update.urls or {"website": "https://competitor-a.com"},
            keywords=competitor_update.keywords or [],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"경쟁사 업데이트 실패: {str(e)}")


@router.delete("/{competitor_id}")
async def delete_competitor(
    competitor_id: str,
    bigquery_client: BigQueryClient = Depends(get_bigquery_client)
) -> dict:
    """
    경쟁사를 삭제합니다.
    """
    try:
        # BigQuery에서 경쟁사 삭제 (소프트 삭제 권장)
        # 추후 구현
        
        return {"message": f"경쟁사 {competitor_id}가 성공적으로 삭제되었습니다."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"경쟁사 삭제 실패: {str(e)}")


@router.get("/{competitor_id}/stats", response_model=CompetitorStats)
async def get_competitor_stats(
    competitor_id: str,
    bigquery_client: BigQueryClient = Depends(get_bigquery_client)
) -> CompetitorStats:
    """
    경쟁사의 수집 통계를 조회합니다.
    """
    try:
        # BigQuery에서 통계 조회 (추후 구현)
        
        return CompetitorStats(
            competitor_id=competitor_id,
            total_content_collected=150,
            last_7_days_content=25,
            last_30_days_content=80,
            avg_daily_content=2.7,
            top_keywords=[
                {"keyword": "마케팅", "count": 45},
                {"keyword": "브랜딩", "count": 32},
                {"keyword": "광고", "count": 28}
            ],
            content_type_distribution={
                "website": 90,
                "instagram": 60
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"경쟁사 통계 조회 실패: {str(e)}")


@router.post("/{competitor_id}/collect")
async def trigger_collection(
    competitor_id: str,
    bigquery_client: BigQueryClient = Depends(get_bigquery_client)
) -> dict:
    """
    특정 경쟁사의 데이터 수집을 즉시 실행합니다.
    """
    try:
        # 데이터 수집 트리거 로직 (추후 구현)
        # Cloud Pub/Sub 메시지 발행 또는 직접 수집 실행
        
        return {
            "message": f"경쟁사 {competitor_id}의 데이터 수집이 시작되었습니다.",
            "status": "triggered"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 수집 트리거 실패: {str(e)}") 
