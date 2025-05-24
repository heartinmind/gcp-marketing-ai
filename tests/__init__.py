"""
MarketingAI 테스트 패키지

이 패키지는 MarketingAI 플랫폼의 모든 테스트 코드를 포함합니다.
"""

# 테스트 설정
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

__version__ = "1.0.0"
__author__ = "MarketingAI Team" 