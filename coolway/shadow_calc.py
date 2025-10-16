import numpy as np
from shapely.geometry import Polygon, MultiPolygon
import geopandas as gpd
from .utils import wgs84_to_utm, utm_to_wgs84

# Shapely 2.x 이상에서만 import
try:
    from shapely import make_valid
    HAS_MAKE_VALID = True
except ImportError:
    HAS_MAKE_VALID = False

def project_shadow(building_gdf, sun_altitude, sun_azimuth):
    """
    건물 GeoDataFrame, 태양 고도/방위각을 받아 그림자 폴리곤 GeoDataFrame을 반환합니다.
    :param building_gdf: 건물 폴리곤 GeoDataFrame (height 컬럼 필요)
    :param sun_altitude: 태양 고도(도)
    :param sun_azimuth: 태양 방위각(도, 북쪽=0, 시계방향)
    :return: 그림자 폴리곤 GeoDataFrame
    """
    shadow_polys = []
    for idx, row in building_gdf.iterrows():
        geom = row.geometry
        height = row.height if 'height' in row else 10
        if sun_altitude <= 0:
            continue
        # 그림자 길이(m)
        shadow_len = height / np.tan(np.radians(sun_altitude))
        # 그림자 방향(라디안, 북=0, 시계방향 → 수학적 각도로 변환)
        angle_rad = np.radians(90 - sun_azimuth)
        dx = shadow_len * np.cos(angle_rad)
        dy = shadow_len * np.sin(angle_rad)
        # --- 좌표계 변환: 위경도 → UTM ---
        if geom.geom_type == 'Polygon':
            shadow = _shadow_polygon_utm(geom, dx, dy)
            shadow = _make_valid_if_needed(shadow)
            shadow_polys.append(shadow)
        elif geom.geom_type == 'MultiPolygon':
            for poly in geom.geoms:
                shadow = _shadow_polygon_utm(poly, dx, dy)
                shadow = _make_valid_if_needed(shadow)
                shadow_polys.append(shadow)
    # None, 빈 geometry 제거
    shadow_polys = [p for p in shadow_polys if p is not None and not p.is_empty]
    shadow_gdf = gpd.GeoDataFrame(geometry=shadow_polys, crs=building_gdf.crs)
    return shadow_gdf


def _shadow_polygon_utm(polygon, dx, dy):
    try:
        # 건물 외곽선 좌표 가져오기
        coords = list(polygon.exterior.coords)
        if len(coords) < 3:
            return None  # 삼각형도 안 되면 스킵

        # UTM으로 변환
        utm_coords = [wgs84_to_utm(lon, lat) for lon, lat in coords]

        # 그림자 꼭짓점 계산
        shadow_coords = [(x + dx, y + dy) for x, y in utm_coords]

        # 완전한 쐐기형 폴리곤 만들기 (건물 → 그림자 → 역순으로 건물)
        full_utm_coords = utm_coords + shadow_coords[::-1]

        # 다시 위경도로 변환
        full_wgs_coords = [utm_to_wgs84(x, y) for x, y in full_utm_coords]

        # 폐곡선 Polygon 생성
        return Polygon(full_wgs_coords)
    except Exception:
        return None

def _make_valid_if_needed(geom):
    """
    Shapely geometry가 invalid하면 make_valid 또는 buffer(0)로 유효화
    """
    if geom is None:
        return None
    if geom.is_valid:
        return geom
    if HAS_MAKE_VALID:
        return make_valid(geom)
    else:
        # Shapely 1.x fallback
        return geom.buffer(0)
