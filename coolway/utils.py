"""
공통적으로 자주 쓰이는 유틸리티 함수 모음
"""

from pyproj import Transformer
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import osmnx as ox

def wgs84_to_utm(lon, lat):
    """
    WGS84 좌표(경도, 위도)를 UTM 좌표(x, y)로 변환
    """
    transformer = Transformer.from_crs("epsg:4326", "epsg:32652", always_xy=True)  # 예시: UTM-K(대한민국 중부)
    x, y = transformer.transform(lon, lat)
    return x, y

def utm_to_wgs84(x, y):
    """
    UTM 좌표(x, y)를 WGS84(경도, 위도)로 변환
    """
    transformer = Transformer.from_crs("epsg:32652", "epsg:4326", always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lon, lat

def geocode_place(place_name, max_retries=3):
    """
    장소명(한글 가능)을 위도, 경도로 변환 (Nominatim 사용, timeout 및 재시도 지원)
    """
    geolocator = Nominatim(user_agent="coolway_geocoder", timeout=10)  # timeout=10초로 충분히 늘림
    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(place_name)
            if location:
                return location.latitude, location.longitude
            else:
                print(f"[지오코딩 실패] '{place_name}'을(를) 찾을 수 없습니다.")
                return None, None
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"[지오코딩 타임아웃] {place_name} (재시도 {attempt+1}/{max_retries})")
    print(f"[지오코딩 실패] '{place_name}'을(를) 최종적으로 찾을 수 없습니다.")
    return None, None

def print_progress(message):
    """
    진행 상황을 깔끔하게 출력하는 함수
    """
    print(f"[CoolWay] {message}")

def map_point_to_nearest_node(G, lat, lon, max_dist=500):
    """
    위경도 좌표(lat, lon)를 그래프 G의 가장 가까운 노드로 맵핑.
    max_dist(m) 이상 떨어져 있으면 None 반환.
    """
    node, dist = ox.nearest_nodes(G, X=lon, Y=lat, return_dist=True)
    if dist > max_dist:
        print(f"[경고] 입력 좌표에서 도로 네트워크까지 거리가 {dist:.1f}m로 너무 멉니다.")
        return None
    return node
