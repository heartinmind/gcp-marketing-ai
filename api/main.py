from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 라우터 임포트
from api.routes.collections import router as collections_router

app = FastAPI(
    title="MarketingAI API",
    description="경쟁사 컨텐츠 동향 분석 자동화 플랫폼",
    version="1.0.0"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(collections_router, prefix="/api/v1", tags=["collections"])

@app.get("/")
async def root():
    return {"message": "MarketingAI API에 오신 것을 환영합니다! 🎉"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 
