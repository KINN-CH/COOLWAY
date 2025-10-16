import folium
import geopandas as gpd

def plot_route_and_shadow(route_coords, buildings_gdf, shadow_gdf, map_center=None, zoom_start=17, save_path=None,
                          start_lat=None, start_lon=None, end_lat=None, end_lon=None):
    """
    folium을 이용해 지도 위에 경로, 건물, 그림자 영역을 시각화합니다.
    출발지/도착지 마커를 추가로 표시합니다.
    :param route_coords: [(lon, lat), ...] 형태의 경로 좌표 리스트
    :param buildings_gdf: 건물 GeoDataFrame
    :param shadow_gdf: 그림자 GeoDataFrame
    :param map_center: (lat, lon) 지도 중심 (없으면 경로 중간값)
    :param zoom_start: 초기 지도 확대 레벨
    :param save_path: 저장 경로 (없으면 저장하지 않음)
    :param start_lat, start_lon, end_lat, end_lon: 출발/도착 위경도 (없으면 route_coords에서 추출)
    :return: folium.Map 객체
    """
    # 지도 중심 자동 설정
    if map_center is None:
        mid_idx = len(route_coords) // 2
        map_center = (route_coords[mid_idx][1], route_coords[mid_idx][0])  # (lat, lon)

    m = folium.Map(location=map_center, zoom_start=zoom_start)

    # 건물 폴리곤(회색)
    folium.GeoJson(
        buildings_gdf,
        name="Buildings",
        style_function=lambda x: {"color": "gray", "weight": 1, "fillOpacity": 0.3}
    ).add_to(m)

    # 그림자 영역(파란색)
    folium.GeoJson(
        shadow_gdf,
        name="Shadows",
        style_function=lambda x: {"color": "blue", "weight": 0, "fillOpacity": 0.4}
    ).add_to(m)

    # 도보 경로(빨간색)
    folium.PolyLine(
        locations=[(lat, lon) for lon, lat in route_coords],
        color="red",
        weight=5,
        opacity=0.8,
        tooltip="도보 경로"
    ).add_to(m)

    # --- 출발지/도착지 마커 추가 ---
    # 좌표 직접 전달이 없으면 route_coords에서 추출
    if start_lat is None or start_lon is None:
        start_lon, start_lat = route_coords[0]
    if end_lat is None or end_lon is None:
        end_lon, end_lat = route_coords[-1]

    folium.Marker(
        location=[start_lat, start_lon],
        popup="출발지",
        tooltip="출발지",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

    folium.Marker(
        location=[end_lat, end_lon],
        popup="도착지",
        tooltip="도착지",
        icon=folium.Icon(color="red", icon="flag")
    ).add_to(m)

    folium.LayerControl().add_to(m)

    if save_path:
        m.save(save_path)
    return m
