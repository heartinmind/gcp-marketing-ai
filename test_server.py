#!/usr/bin/env python3
"""
서버 시작 테스트 스크립트
"""

import sys
import traceback

def test_imports():
    """필요한 모듈들이 정상적으로 import되는지 테스트"""
    try:
        print("1. FastAPI import 테스트...")
        from fastapi import FastAPI
        print("   ✅ FastAPI import 성공")
        
        print("2. uvicorn import 테스트...")
        import uvicorn
        print(f"   ✅ uvicorn import 성공 (버전: {uvicorn.__version__})")
        
        print("3. API main 모듈 import 테스트...")
        from api.main import app
        print("   ✅ API main 모듈 import 성공")
        
        print("4. Instagram 컬렉터 import 테스트...")
        from data_pipelines.collectors.social_media.instagram.collector import InstagramCollector
        print("   ✅ Instagram 컬렉터 import 성공")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import 실패: {e}")
        traceback.print_exc()
        return False

def test_app_creation():
    """FastAPI 앱이 정상적으로 생성되는지 테스트"""
    try:
        print("5. FastAPI 앱 생성 테스트...")
        from api.main import app
        print(f"   ✅ FastAPI 앱 생성 성공: {app}")
        return True
    except Exception as e:
        print(f"   ❌ FastAPI 앱 생성 실패: {e}")
        traceback.print_exc()
        return False

def test_server_start():
    """서버 시작 테스트"""
    try:
        print("6. 서버 시작 테스트...")
        import uvicorn
        from api.main import app
        
        print("   서버를 127.0.0.1:8000에서 시작합니다...")
        print("   (Ctrl+C로 중단하세요)")
        
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
        
    except Exception as e:
        print(f"   ❌ 서버 시작 실패: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Marketing AI 서버 진단 시작...\n")
    
    # Import 테스트
    if not test_imports():
        print("\n❌ Import 테스트 실패. 종료합니다.")
        sys.exit(1)
    
    # 앱 생성 테스트
    if not test_app_creation():
        print("\n❌ 앱 생성 테스트 실패. 종료합니다.")
        sys.exit(1)
    
    print("\n✅ 모든 기본 테스트 통과!")
    print("\n🚀 서버 시작을 시도합니다...")
    
    # 서버 시작 테스트
    test_server_start() 
