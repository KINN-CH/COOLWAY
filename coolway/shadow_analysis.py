# coolway/shadow_analysis.py
"""
도보 경로와 그림자 영역의 겹침 분석 모듈
"""

from shapely.geometry import LineString
import geopandas as gpd

def calculate_shadow_coverage(route_coords, shadow_gdf):
    """
    도보 경로와 그림자 영역이 얼마나 겹치는지 계산합니다.
    :param route_coords: [(lon, lat), ...] 형태의 경로 좌표 리스트
    :param shadow_gdf: 그림자 영역 GeoDatoaFrame
    :return: (전체 경로 길이, 그림자 구간 길이, 그림자 비율)
    """
    route_line = LineString(route_coords)
    route_gdf = gpd.GeoDataFrame(geometry=[route_line], crs=shadow_gdf.crs)

    # 그림자 영역과 경로의 교차 구간 추출
    shadow_union = shadow_gdf.unary_union
    shadow_section = route_line.intersection(shadow_union)

    # 전체 경로 길이
    total_length = route_line.length
    # 그림자 구간 길이
    shadow_length = 0.0
    if shadow_section.is_empty:
        shadow_length = 0.0
    elif shadow_section.geom_type == "LineString":
        shadow_length = shadow_section.length
    elif shadow_section.geom_type == "MultiLineString":
        shadow_length = sum(line.length for line in shadow_section.geoms)

    # 그림자 비율
    shadow_ratio = shadow_length / total_length if total_length > 0 else 0.0

    return total_length, shadow_length, shadow_ratio
