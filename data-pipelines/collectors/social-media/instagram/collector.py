from datetime import datetime
 from dataclasses import dataclass
 from typing import List
 import logging
 logger = logging.getLogger(__name__)
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
 post = InstagramPost(id=f"post_{i}", caption=f"Sample post #{i+1} from @{username}", timestamp=datetime.now(), likes_count=50 + i * 10)
 posts.append(post)
 return posts
