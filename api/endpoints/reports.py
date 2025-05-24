"""
리포트 API 엔드포인트
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_reports():
    """리포트 목록 조회"""
    return {"message": "리포트 목록 - 추후 구현 예정"}

@router.post("/generate")
async def generate_report():
    """새로운 리포트 생성"""
    return {"message": "리포트 생성 - 추후 구현 예정"} 
