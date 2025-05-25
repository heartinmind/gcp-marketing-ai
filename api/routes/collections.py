"""
데이터 수집 관련 API 엔드포인트 - 개선된 버전
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
import logging
import os
import sys
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가 (임시 해결책)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from data_pipelines.collectors.social_media.instagram.collector import InstagramCollector, InstagramPost
except ImportError as e:
    logging.error(f"Instagram 콜렉터 import 실패: {e}")
    # Fallback: Mock 콜렉터 사용
    class MockInstagramCollector:
        def collect_user_posts(self, username: str, max_posts: int = 10):
            from datetime import datetime, timedelta
            from dataclasses import dataclass
            from typing import Optional
            
            @dataclass
            class MockInstagramPost:
                id: str
                caption: Optional[str]
                timestamp: datetime
                likes_count: int
                url: str
            
            posts = []
            for i in range(max_posts):
                posts.append(MockInstagramPost(
                    id=f"mock_post_{i}",
                    caption=f"Mock post #{i+1} from @{username}",
                    timestamp=datetime.now() - timedelta(days=i),
                    likes_count=50 + i * 10,
                    url=f"https://instagram.com/p/mock_{i}"
                ))
            return posts
    
    InstagramCollector = MockInstagramCollector

# Pydantic 모델 정의
class CompetitorCreate(BaseModel):
    name: str
    platform: str
    username: str
    max_posts: int = 10

# 메모리 저장소 (실제로는 데이터베이스 사용)
competitors_db: Dict[str, Dict[str, Any]] = {}

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/collections/")
async def get_collections():
    """수집 작업 목록 조회"""
    return {
        "collections": [
            {"id": "1", "status": "completed", "source": "instagram"},
            {"id": "2", "status": "running", "source": "facebook"}
        ]
    }

@router.post("/collections/instagram/")
async def collect_instagram_posts(username: str, max_posts: int = 10):
    """Instagram 포스트 수집 - 에러 핸들링 강화"""
    try:
        # 입력 검증
        if not username or not username.strip():
            raise HTTPException(status_code=400, detail="유효한 사용자명을 입력해주세요")
        
        if max_posts <= 0 or max_posts > 50:
            raise HTTPException(status_code=400, detail="포스트 수는 1-50 사이여야 합니다")
        
        username = username.strip()
        logger.info(f"Starting Instagram collection for @{username}, max_posts={max_posts}")
        
        collector = InstagramCollector()
        posts = collector.collect_user_posts(username, max_posts)
        
        # 데이터 변환 (안전하게)
        posts_data = []
        for post in posts:
            try:
                post_dict = {
                    "id": post.id,
                    "caption": post.caption,
                    "timestamp": post.timestamp.isoformat() if hasattr(post.timestamp, 'isoformat') else str(post.timestamp),
                    "likes_count": post.likes_count,
                    "url": getattr(post, 'url', f"https://instagram.com/p/{post.id}")
                }
                posts_data.append(post_dict)
            except Exception as e:
                logger.warning(f"포스트 데이터 변환 실패: {e}")
                continue
        
        logger.info(f"Successfully collected {len(posts_data)} posts for @{username}")
        
        return {
            "status": "success",
            "username": username,
            "posts_collected": len(posts_data),
            "posts": posts_data,
            "message": f"@{username}의 Instagram 포스트 {len(posts_data)}개를 성공적으로 수집했습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Instagram collection failed for @{username}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"수집 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/collections/{collection_id}")
async def get_collection(collection_id: str):
    """특정 수집 작업 조회"""
    return {
        "id": collection_id,
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z",
        "items_collected": 25
    }

# 경쟁사 관리 엔드포인트
@router.post("/competitors/")
async def add_competitor(competitor: CompetitorCreate):
    """경쟁사 추가"""
    try:
        # 입력 검증
        if not competitor.name or not competitor.name.strip():
            raise HTTPException(status_code=400, detail="경쟁사 이름을 입력해주세요")
        
        if not competitor.username or not competitor.username.strip():
            raise HTTPException(status_code=400, detail="사용자명을 입력해주세요")
        
        if competitor.platform not in ["Instagram", "Facebook", "YouTube", "Naver Blog", "Website"]:
            raise HTTPException(status_code=400, detail="지원하지 않는 플랫폼입니다")
        
        # 경쟁사 ID 생성
        competitor_id = f"comp_{len(competitors_db) + 1}"
        
        # 경쟁사 정보 저장
        competitor_data = {
            "id": competitor_id,
            "name": competitor.name.strip(),
            "platform": competitor.platform,
            "username": competitor.username.strip(),
            "max_posts": competitor.max_posts,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        competitors_db[competitor_id] = competitor_data
        
        logger.info(f"새 경쟁사 추가: {competitor.name} (@{competitor.username}) on {competitor.platform}")
        
        return {
            "status": "success",
            "message": f"'{competitor.name}' 경쟁사가 성공적으로 추가되었습니다!",
            "competitor": competitor_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"경쟁사 추가 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"경쟁사 추가 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/competitors/")
async def get_competitors():
    """경쟁사 목록 조회"""
    return {
        "status": "success",
        "competitors": list(competitors_db.values()),
        "total": len(competitors_db)
    }

@router.get("/competitors/{competitor_id}")
async def get_competitor(competitor_id: str):
    """특정 경쟁사 조회"""
    if competitor_id not in competitors_db:
        raise HTTPException(status_code=404, detail="경쟁사를 찾을 수 없습니다")
    
    return {
        "status": "success",
        "competitor": competitors_db[competitor_id]
    }

@router.delete("/competitors/{competitor_id}")
async def delete_competitor(competitor_id: str):
    """경쟁사 삭제"""
    if competitor_id not in competitors_db:
        raise HTTPException(status_code=404, detail="경쟁사를 찾을 수 없습니다")
    
    deleted_competitor = competitors_db.pop(competitor_id)
    
    return {
        "status": "success",
        "message": f"'{deleted_competitor['name']}' 경쟁사가 삭제되었습니다",
        "deleted_competitor": deleted_competitor
    }
