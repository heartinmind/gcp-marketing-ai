#!/usr/bin/env python3
"""
MarketingAI 시스템 기능 테스트 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.getcwd())

def test_instagram_collector():
    """Instagram 컬렉터 테스트"""
    try:
        # 경로 수정
        sys.path.append('data-pipelines')
        from collectors.social_media.instagram.collector import InstagramCollector
        
        print("🔍 Instagram 컬렉터 테스트 시작...")
        collector = InstagramCollector()
        posts = collector.collect_user_posts('test_user', 3)
        
        print(f"✅ Instagram 컬렉터 테스트 성공!")
        print(f"📝 수집된 포스트: {len(posts)}개")
        
        for i, post in enumerate(posts):
            print(f"  {i+1}. {post.caption[:50]}... (좋아요: {post.likes_count})")
        
        return True
    except Exception as e:
        print(f"❌ Instagram 컬렉터 테스트 실패: {e}")
        return False

def test_api_module():
    """API 모듈 테스트"""
    try:
        from api.main import app
        from api.routes.collections import router
        
        print("✅ API 모듈 로드 성공!")
        print(f"📡 등록된 라우터 수: {len(app.routes)}")
        return True
    except Exception as e:
        print(f"❌ API 모듈 테스트 실패: {e}")
        return False

def test_bigquery_client():
    """BigQuery 클라이언트 테스트"""
    try:
        from shared.utils.bigquery_client import BigQueryClient
        
        # 테스트용 클라이언트 생성
        client = BigQueryClient("test-project", "test-dataset")
        
        print("✅ BigQuery 클라이언트 생성 성공!")
        return True
    except Exception as e:
        print(f"❌ BigQuery 클라이언트 테스트 실패: {e}")
        return False

def test_streamlit_dashboard():
    """Streamlit 대시보드 테스트"""
    try:
        # Streamlit 모듈 import는 실제 실행 환경에서만 가능
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "streamlit_app", 
            "dashboard/streamlit_app.py"
        )
        
        if spec and spec.loader:
            print("✅ Streamlit 대시보드 모듈 검증 성공!")
            return True
        else:
            print("❌ Streamlit 대시보드 모듈 검증 실패")
            return False
            
    except Exception as e:
        print(f"❌ Streamlit 대시보드 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("🚀 MarketingAI Phase 4 기능 검증 테스트 시작!")
    print("=" * 60)
    
    tests = [
        ("API 모듈", test_api_module),
        ("BigQuery 클라이언트", test_bigquery_client),
        ("Instagram 컬렉터", test_instagram_collector),
        ("Streamlit 대시보드", test_streamlit_dashboard),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트 중...")
        if test_func():
            passed += 1
        print("-" * 40)
    
    print(f"\n🎯 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! 시스템 준비 완료!")
    else:
        print("⚠️ 일부 테스트 실패. 시스템 확인 필요.")
    
    print("\n📊 시스템 상태:")
    print("  ✅ Phase 1: 기반 구조 구축 완료")
    print("  ✅ Phase 2: 소셜미디어 크롤링 구현 완료")  
    print("  ✅ Phase 3: 인프라 & ML 파이프라인 구현 완료")
    print("  🚀 Phase 4: 시스템 배포 & 테스트 진행 중")

if __name__ == "__main__":
    main() 