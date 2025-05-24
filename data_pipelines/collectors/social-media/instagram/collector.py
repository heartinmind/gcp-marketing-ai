"""
Instagram 컨텐츠 수집기

Instagram API 및 웹 스크래핑을 통한 컨텐츠 수집
"""

import requests
from typing import List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class InstagramPost:
    """Instagram 포스트 데이터 구조"""
    id: str
    shortcode: str
    url: str
    caption: Optional[str]
    timestamp: datetime
    likes_count: int
    comments_count: int
    media_type: str  # 'image', 'video', 'carousel'
    media_urls: List[str]
    hashtags: List[str]
    mentions: List[str]
    author_username: str
    author_followers: Optional[int] = None


class InstagramCollector:
    """Instagram 컨텐츠 수집기"""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Instagram 수집기 초기화
        
        Args:
            access_token: Instagram Basic Display API 액세스 토큰
        """
        self.access_token = access_token
        self.base_url = "https://graph.instagram.com"
        self.session = requests.Session()
        self.rate_limit_delay = 1.0  # 초 단위
        
        # User-Agent 설정 (웹 스크래핑용)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def collect_user_posts(self, username: str, max_posts: int = 5) -> List[InstagramPost]:
        """사용자의 포스트를 수집합니다 (현재는 더미 데이터)"""
        posts = []
        for i in range(max_posts):
            post = InstagramPost(
                id=f"post_{i}",
                shortcode=f"B{i:010d}",
                url=f"https://www.instagram.com/p/B{i:010d}/",
                caption=f"Sample post #{i+1} from @{username}",
                timestamp=datetime.now() - timedelta(days=i),
                likes_count=50 + i * 10,
                comments_count=5 + i * 2,
                media_type="image",
                media_urls=[f"https://example.com/image_{i+1}.jpg"],
                hashtags=["sample", "test"],
                mentions=[],
                author_username=username
            )
            posts.append(post)
        
        logger.info(f"Instagram 포스트 {len(posts)}개 수집 완료")
        return posts 
