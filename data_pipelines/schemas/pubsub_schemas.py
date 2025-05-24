"""
Pub/Sub 메시지 스키마 정의

소셜미디어 크롤링 작업을 위한 표준화된 메시지 구조
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ContentSource(str, Enum):
    """컨텐츠 소스 유형"""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    YOUTUBE = "youtube"
    NAVER_BLOG = "naver_blog"
    WEBSITE = "website"


class CollectionTaskMessage(BaseModel):
    """데이터 수집 작업 메시지"""
    task_id: str = Field(..., description="고유 작업 ID")
    competitor_id: str = Field(..., description="경쟁사 ID")
    source: ContentSource = Field(..., description="수집 소스")
    target_url: str = Field(..., description="수집 대상 URL")
    collection_config: Dict[str, Any] = Field(default_factory=dict, description="수집 설정")
    priority: int = Field(default=5, ge=1, le=10, description="우선순위 (1=최고, 10=최저)")
    scheduled_at: datetime = Field(default_factory=datetime.now, description="예약 시간")
    retry_count: int = Field(default=0, description="재시도 횟수")
    max_retries: int = Field(default=3, description="최대 재시도 횟수")


class CollectionResultMessage(BaseModel):
    """데이터 수집 결과 메시지"""
    task_id: str = Field(..., description="작업 ID")
    status: str = Field(..., description="수집 상태 (success/failed)")
    collected_at: datetime = Field(default_factory=datetime.now, description="수집 완료 시간")
    items_collected: int = Field(default=0, description="수집된 항목 수")
    data_location: Optional[str] = Field(None, description="수집된 데이터 저장 위치")
    error_message: Optional[str] = Field(None, description="오류 메시지")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")


class AnalysisTaskMessage(BaseModel):
    """분석 작업 메시지"""
    analysis_id: str = Field(..., description="분석 ID")
    competitor_id: str = Field(..., description="경쟁사 ID")
    analysis_type: str = Field(..., description="분석 유형")
    data_range: Dict[str, datetime] = Field(..., description="분석 데이터 범위")
    config: Dict[str, Any] = Field(default_factory=dict, description="분석 설정")


class ContentItem(BaseModel):
    """수집된 컨텐츠 항목"""
    id: str = Field(..., description="컨텐츠 고유 ID")
    source: ContentSource = Field(..., description="컨텐츠 소스")
    url: str = Field(..., description="원본 URL")
    title: Optional[str] = Field(None, description="제목")
    content: Optional[str] = Field(None, description="본문 내용")
    author: Optional[str] = Field(None, description="작성자")
    published_at: Optional[datetime] = Field(None, description="게시 시간")
    collected_at: datetime = Field(default_factory=datetime.now, description="수집 시간")
    hashtags: List[str] = Field(default_factory=list, description="해시태그")
    mentions: List[str] = Field(default_factory=list, description="멘션")
    engagement: Dict[str, int] = Field(default_factory=dict, description="참여도 (좋아요, 댓글 등)")
    media_urls: List[str] = Field(default_factory=list, description="미디어 URL")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="원본 데이터")


# Pub/Sub 토픽 이름 상수
class PubSubTopics:
    """Pub/Sub 토픽 이름"""
    COLLECTION_TASKS = "marketing-ai-collection-tasks"
    COLLECTION_RESULTS = "marketing-ai-collection-results"
    ANALYSIS_TASKS = "marketing-ai-analysis-tasks"
    ANALYSIS_RESULTS = "marketing-ai-analysis-results"
    
    # 소스별 특화 토픽
    INSTAGRAM_TASKS = "marketing-ai-instagram-tasks"
    FACEBOOK_TASKS = "marketing-ai-facebook-tasks"
    YOUTUBE_TASKS = "marketing-ai-youtube-tasks"
    NAVER_BLOG_TASKS = "marketing-ai-naver-blog-tasks" 
