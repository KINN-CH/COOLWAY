# coolway/osm_buildings.py
"""
OSM에서 건물 폴리곤(외곽선) 데이터를 다운로드 및 파싱하는 모듈
"""

import osmnx as ox
import geopandas as gpd
from .config import OSM_DATA_PATH, DEFAULT_BUILDING_HEIGHT

def fetch_building_polygons(center_lat, center_lon, dist=500):
    """
    OSM에서 중심좌표 기준 반경(dist, m) 내 건물 폴리곤 데이터를 가져옵니다.
    """
    gdf = ox.features_from_point(
        (center_lat, center_lon),
        tags={"building": True},
        dist=dist
    )
    buildings = gdf[gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])].copy()
    buildings['height'] = DEFAULT_BUILDING_HEIGHT
    return buildings

def save_buildings_to_file(buildings_gdf, path=OSM_DATA_PATH):
    """
    건물 폴리곤 GeoDataFrame을 파일로 저장(GeoJSON 등)
    """
    buildings_gdf.to_file(path, driver="GeoJSON")

def load_buildings_from_file(path=OSM_DATA_PATH):
    """
    저장된 건물 폴리곤 데이터를 불러오기
    """
    return gpd.read_file(path)
