from .osm_buildings import fetch_building_polygons
from .osmnx_route import get_k_shortest_routes
from .sun_position import get_sun_position
from .shadow_calc import project_shadow
from .shadow_analysis import calculate_shadow_coverage
from .visualization import plot_route_and_shadow
from .utils import print_progress
from .input_handler import get_coords

from datetime import datetime
import pytz
import webbrowser
import os
from shapely.geometry import LineString, MultiLineString

def main():
    print("=== CoolWay1.3 - 그림자 경로 추천 ===")
    start_input = input("출발지(예: 부산 하단역 or 35.106217, 128.9667238): ")
    end_input = input("도착지(예: 동아대학교 승학캠퍼스 or 35.113752, 128.965672): ")

    start_lat, start_lon = get_coords(start_input)
    end_lat, end_lon = get_coords(end_input)
    if None in (start_lat, start_lon, end_lat, end_lon):
        print("출발지 또는 도착지의 위치를 찾을 수 없습니다.")
        return

    print_progress("최단경로 후보 10개 생성 중...")
    routes = get_k_shortest_routes(start_lat, start_lon, end_lat, end_lon, dist=10000, k=10)
    if not routes:
        print("경로를 찾을 수 없습니다.")
        return

    all_lines = [LineString(route) for route in routes]
    multi_line = MultiLineString(all_lines)
    buffer_dist = 0.001
    route_buffer = multi_line.buffer(buffer_dist)

    print_progress("OSM 건물 데이터 다운로드 중...")
    minx, miny, maxx, maxy = route_buffer.bounds
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2
    bbox_dist = max(maxx - minx, maxy - miny) * 111000 / 2
    buildings_gdf = fetch_building_polygons(center_lat, center_lon, dist=bbox_dist)
    if buildings_gdf.empty:
        print("건물 데이터가 없습니다.")
        return
    buildings_gdf = buildings_gdf[buildings_gdf.geometry.intersects(route_buffer)].copy()
    if buildings_gdf.empty:
        print("경로 주변에 건물이 없습니다.")
        return

    now = datetime.now(pytz.timezone('Asia/Seoul'))
    print_progress(f"태양 위치 계산 중... ({now})")
    sun_altitude, sun_azimuth = get_sun_position(center_lat, center_lon, now)
    print(f"태양 고도: {sun_altitude:.2f}°, 방위각: {sun_azimuth:.2f}°")

    print_progress("그림자 영역 계산 중...")
    shadow_gdf = project_shadow(buildings_gdf, sun_altitude, sun_azimuth)

    best_idx = 0
    best_ratio = -1
    results = []
    for i, route_coords in enumerate(routes):
        total_len, shadow_len, shadow_ratio = calculate_shadow_coverage(route_coords, shadow_gdf)
        results.append((total_len, shadow_len, shadow_ratio))
        print(f"경로 {i+1} - 전체: {total_len:.1f}m, 그림자: {shadow_len:.1f}m, 비율: {shadow_ratio:.1%}")
        if shadow_ratio > best_ratio:
            best_idx = i
            best_ratio = shadow_ratio

    print_progress("결과 시각화 중...")
    m = plot_route_and_shadow(routes[best_idx], buildings_gdf, shadow_gdf,
                             start_lat=start_lat, start_lon=start_lon, end_lat=end_lat, end_lon=end_lon)
    html_path = "result_map.html"
    m.save(html_path)
    abs_path = os.path.abspath(html_path)
    webbrowser.open_new_tab('file://' + abs_path)
    print(f"브라우저에서 result_map.html이 자동으로 열렸습니다. (추천: 경로 {best_idx+1})")
def run_from_web(start_input, end_input):
    start_lat, start_lon = get_coords(start_input)
    end_lat, end_lon = get_coords(end_input)
    if None in (start_lat, start_lon, end_lat, end_lon):
        print("출발지 또는 도착지의 위치를 찾을 수 없습니다.")
        return

    print_progress("최단경로 후보 10개 생성 중...")
    routes = get_k_shortest_routes(start_lat, start_lon, end_lat, end_lon, dist=10000, k=10)
    if not routes:
        print("경로를 찾을 수 없습니다.")
        return

    all_lines = [LineString(route) for route in routes]
    multi_line = MultiLineString(all_lines)
    buffer_dist = 0.001
    route_buffer = multi_line.buffer(buffer_dist)

    print_progress("OSM 건물 데이터 다운로드 중...")
    minx, miny, maxx, maxy = route_buffer.bounds
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2
    bbox_dist = max(maxx - minx, maxy - miny) * 111000 / 2
    buildings_gdf = fetch_building_polygons(center_lat, center_lon, dist=bbox_dist)
    if buildings_gdf.empty:
        print("건물 데이터가 없습니다.")
        return
    buildings_gdf = buildings_gdf[buildings_gdf.geometry.intersects(route_buffer)].copy()
    if buildings_gdf.empty:
        print("경로 주변에 건물이 없습니다.")
        return

    now = datetime.now(pytz.timezone('Asia/Seoul'))
    print_progress(f"태양 위치 계산 중... ({now})")
    sun_altitude, sun_azimuth = get_sun_position(center_lat, center_lon, now)
    print(f"태양 고도: {sun_altitude:.2f}°, 방위각: {sun_azimuth:.2f}°")

    print_progress("그림자 영역 계산 중...")
    shadow_gdf = project_shadow(buildings_gdf, sun_altitude, sun_azimuth)

    best_idx = 0
    best_ratio = -1
    results = []
    for i, route_coords in enumerate(routes):
        total_len, shadow_len, shadow_ratio = calculate_shadow_coverage(route_coords, shadow_gdf)
        results.append((total_len, shadow_len, shadow_ratio))
        print(f"경로 {i+1} - 전체: {total_len:.1f}m, 그림자: {shadow_len:.1f}m, 비율: {shadow_ratio:.1%}")
        if shadow_ratio > best_ratio:
            best_idx = i
            best_ratio = shadow_ratio

    print_progress("결과 시각화 중...")
    m = plot_route_and_shadow(
        routes[best_idx],
        buildings_gdf,
        shadow_gdf,
        start_lat=start_lat,
        start_lon=start_lon,
        end_lat=end_lat,
        end_lon=end_lon
    )
    # **여기만 웹용으로 경로 변경!**
    html_path = os.path.join("static", "result_map.html")
    m.save(html_path)
