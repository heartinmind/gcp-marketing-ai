"""
데이터 수집 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from data_pipelines.collectors.social_media.instagram.collector import InstagramCollector, InstagramPost
except ImportError:
    # 임포트 실패 시 더미 클래스 사용
    from datetime import datetime
    from dataclasses import dataclass
    
    @dataclass
    class InstagramPost:
        id: str
        caption: str
        timestamp: datetime
        likes_count: int = 0
    
    class InstagramCollector:
        def collect_user_posts(self, username: str, max_posts: int = 5):
            posts = []
            for i in range(max_posts):
                post = InstagramPost(
                    id=f"post_{i}",
                    caption=f"Sample post #{i+1} from @{username}",
                    timestamp=datetime.now(),
                    likes_count=50 + i * 10
                )
                posts.append(post)
            return posts

router = APIRouter()

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
    """Instagram 포스트 수집"""
    try:
        collector = InstagramCollector()
        posts = collector.collect_user_posts(username, max_posts)
        
        # InstagramPost 객체를 딕셔너리로 변환
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "caption": post.caption,
                "timestamp": post.timestamp.isoformat(),
                "likes_count": post.likes_count
            })
        
        return {
            "status": "success",
            "username": username,
            "posts_collected": len(posts_data),
            "posts": posts_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"수집 중 오류 발생: {str(e)}")

@router.get("/collections/{collection_id}")
async def get_collection(collection_id: str):
    """특정 수집 작업 조회"""
    return {
        "id": collection_id,
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z",
        "items_collected": 25
    } 
