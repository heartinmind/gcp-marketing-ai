"""
분석 결과 API 엔드포인트
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_analysis_results():
    """분석 결과 목록 조회"""
    return {"message": "분석 결과 목록 - 추후 구현 예정"}

@router.get("/keywords")
async def get_keyword_analysis():
    """키워드 분석 결과"""
    return {"message": "키워드 분석 - 추후 구현 예정"}

@router.get("/trends")
async def get_trend_analysis():
    """트렌드 분석 결과"""
    return {"message": "트렌드 분석 - 추후 구현 예정"} 
