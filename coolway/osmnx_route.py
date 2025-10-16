import osmnx as ox
import networkx as nx

def map_point_to_nearest_node(G, lat, lon, max_dist=500):
    node, dist = ox.nearest_nodes(G, X=lon, Y=lat, return_dist=True)
    if dist > max_dist:
        print(f"[경고] 입력 좌표에서 도로 네트워크까지 거리가 {dist:.1f}m로 너무 멉니다.")
        return None
    return node

def get_k_shortest_routes(start_lat, start_lon, end_lat, end_lon, dist=1500, k=10):
    """
    OSMnx 기반 도보 네트워크에서 최단 경로 후보 k개를 반환
    :return: [ [(lon, lat), ...], ... ]  # 경로별 좌표 리스트
    """
    G_multi = ox.graph_from_point((start_lat, start_lon), dist=dist, network_type='walk', simplify=True)
    # MultiDiGraph → DiGraph 변환 (가장 짧은 엣지만 남김)
    G = nx.DiGraph()
    for u, v, data in G_multi.edges(data=True):
        if G.has_edge(u, v):
            if data.get('length', float('inf')) < G[u][v].get('length', float('inf')):
                G[u][v].update(data)
        else:
            G.add_edge(u, v, **data)
    for n, d in G_multi.nodes(data=True):
        G.add_node(n, **d)
    G.graph.update(G_multi.graph)
    # 출발/도착 노드 맵핑
    orig = map_point_to_nearest_node(G, start_lat, start_lon, max_dist=500)
    dest = map_point_to_nearest_node(G, end_lat, end_lon, max_dist=500)
    if orig is None or dest is None:
        print("[오류] 출발지 또는 도착지가 도보 네트워크와 너무 멉니다.")
        return []
    # k개 최단경로 후보 생성
    routes = []
    try:
        k_routes = nx.shortest_simple_paths(G, orig, dest, weight='length')
        for i, route in enumerate(k_routes):
            if i >= k:
                break
            coords = [(G.nodes[n]['x'], G.nodes[n]['y']) for n in route]
            if coords and len(coords) > 1:
                routes.append(coords)
    except Exception as e:
        print(f"[OSMnx 경로 오류] {e}")
    return routes
