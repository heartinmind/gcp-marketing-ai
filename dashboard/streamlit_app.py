"""
MarketingAI 대시보드

Streamlit 기반 실시간 경쟁사 분석 대시보드
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
from typing import Dict, Any
import time
import requests

# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 페이지 설정
st.set_page_config(
    page_title="MarketingAI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    .competitor-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .status-active { color: #28a745; }
    .status-inactive { color: #dc3545; }
    .status-pending { color: #ffc107; }
    
    .analysis-button {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 2rem;
        border-radius: 0.5rem;
        border: none;
        font-weight: bold;
        cursor: pointer;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# FastAPI 서버 URL
API_BASE_URL = "http://localhost:8000"

def call_api(endpoint: str, method: str = "GET", data: dict = None):
    """FastAPI 서버 호출"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API 오류: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"서버 연결 오류: {str(e)}")
        return None

def render_competitor_input_form():
    """경쟁사 추가 폼"""
    st.subheader("🎯 새 경쟁사 추가")
    
    with st.form("add_competitor_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            competitor_name = st.text_input(
                "경쟁사 이름",
                placeholder="예: 삼성전자, 현대자동차"
            )
            platform = st.selectbox(
                "플랫폼 선택",
                ["Instagram", "Facebook", "YouTube", "Naver Blog", "Website"]
            )
        
        with col2:
            username = st.text_input(
                "사용자명/URL",
                placeholder="예: @samsung, www.samsung.com"
            )
            max_posts = st.number_input(
                "수집할 포스트 수",
                min_value=1,
                max_value=50,
                value=10
            )
        
        submitted = st.form_submit_button("➕ 경쟁사 추가", use_container_width=True)
        
        if submitted and competitor_name and username:
            with st.spinner("경쟁사를 추가하는 중..."):
                # API 호출
                result = call_api("/competitors/", "POST", {
                    "name": competitor_name,
                    "platform": platform,
                    "username": username,
                    "max_posts": max_posts
                })
                
                if result:
                    st.success(f"✅ '{competitor_name}' 경쟁사가 성공적으로 추가되었습니다!")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("경쟁사 추가에 실패했습니다.")

def render_analysis_controls():
    """분석 실행 컨트롤"""
    st.subheader("🔍 분석 실행")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 컨텐츠 수집", use_container_width=True, type="primary"):
            with st.spinner("Instagram 컨텐츠를 수집하는 중..."):
                # Instagram 수집 API 호출
                result = call_api("/collections/instagram/?username=competitor_example&max_posts=5", "POST")
                if result:
                    st.success("✅ Instagram 컨텐츠 수집 완료!")
                    st.json(result)
    
    with col2:
        if st.button("🌐 웹 스크래핑", use_container_width=True, type="secondary"):
            with st.spinner("웹사이트를 스크래핑하는 중..."):
                # 웹 스크래핑 API 호출
                result = call_api("/collections/web-scrape/?url=https://example.com&competitor_name=Example", "POST")
                if result:
                    st.success("✅ 웹 스크래핑 완료!")
                    st.json(result)
    
    with col3:
        if st.button("🧮 키워드 분석", use_container_width=True, type="secondary"):
            with st.spinner("키워드를 분석하는 중..."):
                # 키워드 분석 API 호출  
                sample_data = [{"content": "마케팅 분석 도구 소개", "page_title": "마케팅AI"}]
                result = call_api("/analysis/keywords/", "POST", sample_data)
                if result:
                    st.success("✅ 키워드 분석 완료!")
                    st.json(result)

def render_url_scraping_form():
    """URL 직접 스크래핑 폼"""
    st.subheader("🔗 URL 직접 분석")
    
    with st.form("url_scraping_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            url = st.text_input(
                "분석할 URL",
                placeholder="https://www.competitor.com"
            )
        
        with col2:
            competitor_name = st.text_input(
                "경쟁사 이름",
                placeholder="경쟁사명"
            )
        
        submitted = st.form_submit_button("🔍 분석 시작", use_container_width=True)
        
        if submitted and url and competitor_name:
            with st.spinner(f"'{url}' 분석 중..."):
                # 웹 스크래핑 API 호출
                result = call_api(f"/collections/web-scrape/?url={url}&competitor_name={competitor_name}", "POST")
                
                if result:
                    st.success("✅ URL 분석 완료!")
                    
                    # 결과 표시
                    if "scraped_data" in result:
                        data = result["scraped_data"]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("페이지 제목", data.get("page_title", "N/A"))
                            st.metric("수집 시간", data.get("collected_at", "N/A"))
                        
                        with col2:
                            st.metric("컨텐츠 길이", f"{len(data.get('content', ''))} 글자")
                            st.metric("메타 설명", data.get("meta_description", "N/A")[:50] + "...")
                        
                        # 컨텐츠 미리보기
                        with st.expander("📄 수집된 컨텐츠 미리보기"):
                            content = data.get("content", "")
                            st.text_area("컨텐츠", content[:1000] + ("..." if len(content) > 1000 else ""), height=200)

@st.cache_data(ttl=300)  # 5분 캐시
def load_sample_data() -> Dict[str, Any]:
    """
    샘플 데이터 로드 (실제로는 BigQuery에서 조회)
    """
    # 경쟁사 목록
    competitors = [
        {"id": "comp_1", "name": "경쟁사 A", "platform": "Instagram", "status": "active"},
        {"id": "comp_2", "name": "경쟁사 B", "platform": "Facebook", "status": "active"},
        {"id": "comp_3", "name": "경쟁사 C", "platform": "YouTube", "status": "pending"},
        {"id": "comp_4", "name": "경쟁사 D", "platform": "Instagram", "status": "inactive"},
    ]
    
    # 수집 데이터 (최근 30일)
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='D'
    )
    
    collection_data = []
    for date in dates:
        for comp in competitors:
            if comp["status"] == "active":
                posts = 5 + int((date.day + hash(comp["id"])) % 10)
                engagement = 100 + int((date.day * hash(comp["id"])) % 500)
                
                collection_data.append({
                    "date": date,
                    "competitor": comp["name"],
                    "platform": comp["platform"],
                    "posts_collected": posts,
                    "total_engagement": engagement,
                    "avg_engagement": engagement / posts if posts > 0 else 0
                })
    
    # 최근 포스트 데이터
    recent_posts = [
        {
            "id": f"post_{i}",
            "competitor": competitors[i % len(competitors)]["name"],
            "platform": competitors[i % len(competitors)]["platform"],
            "content": f"샘플 포스트 내용 {i+1}...",
            "engagement_score": 0.6 + (i % 4) * 0.1,
            "likes": 50 + i * 15,
            "comments": 5 + i * 2,
            "created_at": datetime.now() - timedelta(hours=i*2)
        }
        for i in range(10)
    ]
    
    return {
        "competitors": competitors,
        "collection_data": pd.DataFrame(collection_data),
        "recent_posts": recent_posts
    }


def render_header():
    """헤더 렌더링"""
    st.markdown('<h1 class="main-header">📊 MarketingAI Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### 실시간 경쟁사 컨텐츠 분석 플랫폼")


def render_sidebar():
    """사이드바 렌더링"""
    st.sidebar.title("🎛️ 설정")
    
    # 시간 범위 선택
    time_range = st.sidebar.selectbox(
        "분석 기간",
        ["최근 7일", "최근 30일", "최근 90일"],
        index=1
    )
    
    # 플랫폼 필터
    platforms = st.sidebar.multiselect(
        "플랫폼 선택",
        ["Instagram", "Facebook", "YouTube", "Naver Blog"],
        default=["Instagram", "Facebook"]
    )
    
    # 자동 새로고침
    auto_refresh = st.sidebar.checkbox("자동 새로고침 (30초)", value=True)
    
    if auto_refresh:
        st.sidebar.info("⏱️ 다음 새로고침: 30초 후")
    
    # 수동 새로고침 버튼
    if st.sidebar.button("🔄 수동 새로고침"):
        st.cache_data.clear()
        st.rerun()
    
    return time_range, platforms, auto_refresh


def render_metrics(data: Dict[str, Any]):
    """주요 지표 렌더링"""
    st.subheader("📈 주요 지표")
    
    # 메트릭 계산
    df = data["collection_data"]
    recent_data = df[df["date"] >= datetime.now() - timedelta(days=7)]
    
    total_posts = recent_data["posts_collected"].sum()
    total_engagement = recent_data["total_engagement"].sum()
    active_competitors = len([c for c in data["competitors"] if c["status"] == "active"])
    avg_engagement = recent_data["avg_engagement"].mean()
    
    # 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📝 수집된 포스트 (7일)",
            value=f"{total_posts:,}",
            delta=f"+{int(total_posts * 0.15)}"
        )
    
    with col2:
        st.metric(
            label="💡 총 참여도",
            value=f"{total_engagement:,}",
            delta=f"+{int(total_engagement * 0.08)}"
        )
    
    with col3:
        st.metric(
            label="🏢 활성 경쟁사",
            value=active_competitors,
            delta="+1"
        )
    
    with col4:
        st.metric(
            label="📊 평균 참여도",
            value=f"{avg_engagement:.1f}",
            delta=f"+{avg_engagement * 0.05:.1f}"
        )


def render_competitor_analysis(data: Dict[str, Any]):
    """경쟁사 분석 차트"""
    st.subheader("🏢 경쟁사별 성과 분석")
    
    df = data["collection_data"]
    
    # 탭으로 구분
    tab1, tab2, tab3 = st.tabs(["📊 참여도 트렌드", "📈 포스트 수집량", "🎯 플랫폼별 분석"])
    
    with tab1:
        # 참여도 트렌드 차트
        fig = px.line(
            df.groupby(["date", "competitor"])["total_engagement"].sum().reset_index(),
            x="date",
            y="total_engagement", 
            color="competitor",
            title="경쟁사별 일일 참여도 트렌드",
            markers=True
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # 포스트 수집량 차트
        posts_summary = df.groupby("competitor")["posts_collected"].sum().reset_index()
        fig = px.bar(
            posts_summary,
            x="competitor",
            y="posts_collected",
            title="경쟁사별 총 포스트 수집량",
            color="posts_collected"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # 플랫폼별 분석
        platform_summary = df.groupby("platform").agg({
            "posts_collected": "sum",
            "total_engagement": "sum",
            "avg_engagement": "mean"
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                platform_summary,
                values="posts_collected",
                names="platform",
                title="플랫폼별 포스트 비율"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                platform_summary,
                x="platform",
                y="avg_engagement",
                title="플랫폼별 평균 참여도",
                color="avg_engagement"
            )
            st.plotly_chart(fig, use_container_width=True)


def render_recent_posts(data: Dict[str, Any]):
    """최근 포스트 목록"""
    st.subheader("📝 최근 수집된 포스트")
    
    posts = data["recent_posts"]
    
    for post in posts[:5]:  # 최근 5개만 표시
        with st.container():
            st.markdown(f"""
            <div class="competitor-card">
                <h4>{post['competitor']} ({post['platform']})</h4>
                <p>{post['content']}</p>
                <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                    <span>❤️ {post['likes']} | 💬 {post['comments']}</span>
                    <span>📊 참여도 점수: {post['engagement_score']:.2f}</span>
                    <span>🕒 {post['created_at'].strftime('%Y-%m-%d %H:%M')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_competitor_status(data: Dict[str, Any]):
    """경쟁사 상태 모니터링"""
    st.subheader("🎯 경쟁사 모니터링 상태")
    
    competitors = data["competitors"]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 상태별 그룹화
        status_counts = {}
        for comp in competitors:
            status = comp["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 상태별 파이 차트
        fig = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="경쟁사 모니터링 상태",
            color_discrete_map={
                "active": "#28a745",
                "inactive": "#dc3545", 
                "pending": "#ffc107"
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**경쟁사 목록**")
        for comp in competitors:
            status_class = f"status-{comp['status']}"
            st.markdown(f"""
            <div style="margin-bottom: 0.5rem;">
                <strong>{comp['name']}</strong><br>
                <small>{comp['platform']}</small><br>
                <span class="{status_class}">● {comp['status'].upper()}</span>
            </div>
            """, unsafe_allow_html=True)


def render_realtime_alerts():
    """실시간 알림"""
    st.subheader("🔔 실시간 알림")
    
    # 샘플 알림 데이터
    alerts = [
        {"type": "success", "message": "경쟁사 A의 새로운 포스트 10개 수집 완료", "time": "2분 전"},
        {"type": "warning", "message": "경쟁사 C의 API 한도 임박 (85% 사용)", "time": "15분 전"},
        {"type": "info", "message": "ML 모델 재훈련 완료 (정확도: 87.3%)", "time": "1시간 전"},
        {"type": "error", "message": "경쟁사 D 수집 실패 - 재시도 예정", "time": "2시간 전"},
    ]
    
    for alert in alerts:
        if alert["type"] == "success":
            st.success(f"✅ {alert['message']} ({alert['time']})")
        elif alert["type"] == "warning":
            st.warning(f"⚠️ {alert['message']} ({alert['time']})")
        elif alert["type"] == "info":
            st.info(f"ℹ️ {alert['message']} ({alert['time']})")
        elif alert["type"] == "error":
            st.error(f"❌ {alert['message']} ({alert['time']})")


def main():
    """메인 애플리케이션"""
    # 헤더 렌더링
    render_header()
    
    # 사이드바
    time_range, platforms, auto_refresh = render_sidebar()
    
    # 탭으로 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 대시보드", "🎯 경쟁사 관리", "🔍 분석 도구", "⚙️ 설정"])
    
    with tab1:
        # 기존 대시보드
        try:
            data = load_sample_data()
            
            # 메인 대시보드
            render_metrics(data)
            
            st.divider()
            
            # 두 컬럼으로 레이아웃
            col1, col2 = st.columns([2, 1])
            
            with col1:
                render_competitor_analysis(data)
            
            with col2:
                render_competitor_status(data)
            
            st.divider()
            
            # 하단 섹션
            col1, col2 = st.columns(2)
            
            with col1:
                render_recent_posts(data)
            
            with col2:
                render_realtime_alerts()
        
        except Exception as e:
            st.error(f"대시보드 로딩 오류: {str(e)}")
    
    with tab2:
        # 경쟁사 관리 탭
        st.header("🎯 경쟁사 관리")
        
        # 경쟁사 추가 폼
        render_competitor_input_form()
        
        st.divider()
        
        # 기존 경쟁사 목록 표시
        st.subheader("📋 등록된 경쟁사 목록")
        
        # 샘플 경쟁사 데이터 (실제로는 API에서 가져와야 함)
        competitors_df = pd.DataFrame([
            {"이름": "삼성전자", "플랫폼": "Instagram", "사용자명": "@samsung", "상태": "🟢 활성", "마지막 수집": "2시간 전"},
            {"이름": "LG전자", "플랫폼": "Facebook", "사용자명": "@lgelectronics", "상태": "🟢 활성", "마지막 수집": "30분 전"},
            {"이름": "현대자동차", "플랫폼": "YouTube", "사용자명": "@hyundai", "상태": "🟡 대기", "마지막 수집": "1일 전"},
        ])
        
        st.dataframe(competitors_df, use_container_width=True)
        
        # 경쟁사 관리 버튼들
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 전체 새로고침", use_container_width=True):
                st.success("모든 경쟁사 데이터를 새로고침합니다...")
        with col2:
            if st.button("⏸️ 수집 일시정지", use_container_width=True):
                st.warning("데이터 수집을 일시정지합니다...")
        with col3:
            if st.button("🗑️ 비활성 제거", use_container_width=True):
                st.info("비활성 경쟁사를 제거합니다...")
    
    with tab3:
        # 분석 도구 탭
        st.header("🔍 분석 도구")
        
        # 분석 실행 컨트롤
        render_analysis_controls()
        
        st.divider()
        
        # URL 직접 분석
        render_url_scraping_form()
        
        st.divider()
        
        # 키워드 분석 폼
        st.subheader("🔤 텍스트 키워드 분석")
        with st.form("keyword_analysis_form"):
            text_input = st.text_area(
                "분석할 텍스트 입력",
                placeholder="경쟁사의 마케팅 컨텐츠나 웹사이트 텍스트를 입력하세요...",
                height=150
            )
            
            if st.form_submit_button("🧮 키워드 분석 실행", use_container_width=True):
                if text_input:
                    with st.spinner("텍스트를 분석하는 중..."):
                        # 키워드 분석 시뮬레이션
                        keywords = ["마케팅", "디지털", "혁신", "고객", "서비스", "품질", "기술"]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.success("✅ 키워드 분석 완료!")
                            st.write("**추출된 키워드:**")
                            for keyword in keywords:
                                st.badge(keyword)
                        
                        with col2:
                            # 키워드 빈도 차트
                            keyword_counts = {k: len(k) * 10 for k in keywords}  # 더미 데이터
                            fig = px.bar(
                                x=list(keyword_counts.keys()),
                                y=list(keyword_counts.values()),
                                title="키워드 빈도"
                            )
                            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # 설정 탭
        st.header("⚙️ 시스템 설정")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔗 API 연결 설정")
            
            # API 상태 확인
            api_status = call_api("/")
            if api_status:
                st.success("✅ FastAPI 서버 연결됨")
            else:
                st.error("❌ FastAPI 서버 연결 실패")
            
            st.text_input("API 서버 URL", value=API_BASE_URL, disabled=True)
            
            if st.button("🔍 연결 테스트", use_container_width=True):
                with st.spinner("API 연결을 테스트하는 중..."):
                    result = call_api("/")
                    if result:
                        st.success("✅ API 서버가 정상적으로 응답합니다!")
                        st.json(result)
                    else:
                        st.error("❌ API 서버에 연결할 수 없습니다.")
        
        with col2:
            st.subheader("📊 데이터 설정")
            
            # 수집 주기 설정
            st.selectbox(
                "데이터 수집 주기",
                ["15분", "30분", "1시간", "2시간", "6시간", "12시간", "24시간"],
                index=2
            )
            
            # 데이터 보관 기간
            st.selectbox(
                "데이터 보관 기간",
                ["7일", "30일", "90일", "180일", "1년"],
                index=2
            )
            
            # 알림 설정
            st.subheader("🔔 알림 설정")
            enable_notifications = st.checkbox("알림 활성화", value=True)
            
            if enable_notifications:
                st.checkbox("새 포스트 수집 알림", value=True)
                st.checkbox("오류 발생 알림", value=True)
                st.checkbox("일일 요약 리포트", value=False)
            
            if st.button("💾 설정 저장", use_container_width=True):
                st.success("✅ 설정이 저장되었습니다!")
    
    # 자동 새로고침
    if auto_refresh:
        time.sleep(30)
        st.rerun()


if __name__ == "__main__":
    main() 
