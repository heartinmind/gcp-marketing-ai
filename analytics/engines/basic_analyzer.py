"""
기본 분석 모듈
경쟁사 데이터에 대한 기본적인 분석을 수행합니다.
"""

import uuid
from datetime import datetime, date
from typing import Dict, List, Any
from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)


class BasicAnalyzer:
    """기본 분석 클래스"""
    
    def __init__(self):
        """분석기 초기화"""
        pass
    
    def analyze_keywords(self, competitor_data: List[Dict]) -> Dict[str, Any]:
        """
        키워드 분석을 수행합니다.
        
        Args:
            competitor_data: 경쟁사 데이터 리스트
            
        Returns:
            키워드 분석 결과
        """
        try:
            all_text = ""
            for data in competitor_data:
                content = data.get('content', '') or ''
                title = data.get('page_title', '') or ''
                meta_desc = data.get('meta_description', '') or ''
                all_text += f" {content} {title} {meta_desc}"
            
            # 텍스트 전처리 및 키워드 추출
            words = self._extract_keywords(all_text)
            keyword_counts = Counter(words)
            
            # 상위 키워드 추출
            top_keywords = keyword_counts.most_common(20)
            
            analysis_result = {
                'total_words': len(words),
                'unique_words': len(keyword_counts),
                'top_keywords': [
                    {'keyword': word, 'count': count} 
                    for word, count in top_keywords
                ],
                'keyword_density': {
                    word: round(count / len(words) * 100, 2) 
                    for word, count in top_keywords[:10]
                }
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"키워드 분석 실패: {str(e)}")
            return {}
    
    def analyze_content_changes(self, competitor_data: List[Dict]) -> Dict[str, Any]:
        """
        콘텐츠 변경 분석을 수행합니다.
        
        Args:
            competitor_data: 경쟁사 데이터 리스트
            
        Returns:
            콘텐츠 변경 분석 결과
        """
        try:
            # URL별로 데이터 그룹화
            url_groups = {}
            for data in competitor_data:
                url = data['url']
                if url not in url_groups:
                    url_groups[url] = []
                url_groups[url].append(data)
            
            # 각 URL의 변경 빈도 계산
            change_analysis = {}
            for url, data_list in url_groups.items():
                # 시간순 정렬
                sorted_data = sorted(data_list, key=lambda x: x['collected_at'])
                
                change_analysis[url] = {
                    'total_collections': len(sorted_data),
                    'first_collected': sorted_data[0]['collected_at'] if sorted_data else None,
                    'last_collected': sorted_data[-1]['collected_at'] if sorted_data else None,
                    'unique_versions': len(set(d['content_hash'] for d in sorted_data)),
                    'change_frequency': len(set(d['content_hash'] for d in sorted_data)) / len(sorted_data) if sorted_data else 0
                }
            
            # 전체 통계
            total_pages = len(url_groups)
            total_collections = sum(len(data_list) for data_list in url_groups.values())
            avg_change_frequency = sum(
                analysis['change_frequency'] for analysis in change_analysis.values()
            ) / total_pages if total_pages > 0 else 0
            
            result = {
                'total_pages_monitored': total_pages,
                'total_data_points': total_collections,
                'average_change_frequency': round(avg_change_frequency, 3),
                'page_analysis': change_analysis,
                'most_dynamic_pages': sorted(
                    change_analysis.items(),
                    key=lambda x: x[1]['change_frequency'],
                    reverse=True
                )[:5]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"콘텐츠 변경 분석 실패: {str(e)}")
            return {}
    
    def generate_competitor_summary(self, competitor_name: str, 
                                  competitor_data: List[Dict]) -> Dict[str, Any]:
        """
        경쟁사별 요약 분석을 생성합니다.
        
        Args:
            competitor_name: 경쟁사 이름
            competitor_data: 경쟁사 데이터 리스트
            
        Returns:
            경쟁사 요약 분석 결과
        """
        try:
            if not competitor_data:
                return {}
            
            # 기본 통계
            total_pages = len(set(data['url'] for data in competitor_data))
            total_collections = len(competitor_data)
            
            # 최근 활동
            latest_collection = max(competitor_data, key=lambda x: x['collected_at'])
            
            # 페이지 유형 분석 (URL 패턴 기반)
            page_types = self._analyze_page_types(competitor_data)
            
            # 콘텐츠 길이 분석
            content_lengths = [len(data.get('content', '')) for data in competitor_data]
            avg_content_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
            
            summary = {
                'competitor_name': competitor_name,
                'monitoring_summary': {
                    'total_pages_monitored': total_pages,
                    'total_data_collections': total_collections,
                    'latest_collection_date': latest_collection['collected_at'],
                    'average_content_length': round(avg_content_length, 0)
                },
                'page_type_distribution': page_types,
                'content_insights': {
                    'shortest_content': min(content_lengths) if content_lengths else 0,
                    'longest_content': max(content_lengths) if content_lengths else 0,
                    'content_length_variance': round(
                        sum((x - avg_content_length) ** 2 for x in content_lengths) / len(content_lengths), 2
                    ) if content_lengths else 0
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"경쟁사 요약 분석 실패: {str(e)}")
            return {}
    
    def create_analysis_record(self, competitor_name: str, analysis_type: str,
                             results: Dict[str, Any], summary: str = "") -> Dict[str, Any]:
        """
        분석 결과 레코드를 생성합니다.
        
        Args:
            competitor_name: 경쟁사 이름
            analysis_type: 분석 유형
            results: 분석 결과
            summary: 분석 요약
            
        Returns:
            BigQuery 삽입용 분석 결과 레코드
        """
        return {
            'id': str(uuid.uuid4()),
            'competitor_name': competitor_name,
            'analysis_type': analysis_type,
            'analysis_date': date.today().isoformat(),
            'results': results,
            'summary': summary,
            'created_at': datetime.utcnow().isoformat()
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드를 추출합니다."""
        # 텍스트 정리
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 단어 분리
        words = text.split()
        
        # 불용어 제거 및 길이 필터링
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
            'his', 'her', 'its', 'our', 'their', 'about', 'above', 'after', 'again', 'against', 'all',
            'am', 'any', 'as', 'because', 'before', 'below', 'between', 'both', 'down', 'during', 'each',
            'few', 'from', 'further', 'here', 'how', 'if', 'into', 'more', 'most', 'no', 'not', 'now',
            'only', 'other', 'out', 'over', 'own', 'same', 'so', 'some', 'such', 'than', 'then', 'there',
            'through', 'too', 'under', 'until', 'up', 'very', 'what', 'when', 'where', 'which', 'while',
            'who', 'why', 'with', 'without'
        }
        
        filtered_words = [
            word for word in words 
            if len(word) > 2 and word not in stop_words and word.isalpha()
        ]
        
        return filtered_words
    
    def _analyze_page_types(self, competitor_data: List[Dict]) -> Dict[str, int]:
        """URL 패턴을 기반으로 페이지 유형을 분석합니다."""
        page_types = {}
        
        for data in competitor_data:
            url = data['url'].lower()
            
            if '/product' in url or '/item' in url:
                page_type = 'product'
            elif '/pricing' in url or '/price' in url:
                page_type = 'pricing'
            elif '/about' in url or '/company' in url:
                page_type = 'about'
            elif '/blog' in url or '/news' in url:
                page_type = 'content'
            elif '/contact' in url:
                page_type = 'contact'
            elif '/service' in url or '/solution' in url:
                page_type = 'service'
            else:
                page_type = 'other'
            
            page_types[page_type] = page_types.get(page_type, 0) + 1
        
        return page_types 