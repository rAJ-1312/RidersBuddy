from math import sqrt


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate approximate distance between two coordinates in kilometers."""
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    return sqrt(dlat**2 + dlng**2) * 111


def connect_waypoint_to_grid(neo4j_session, waypoint_id: int, grid_x: int, grid_y: int):
    adjacent_cells = [
        (grid_x - 1, grid_y), (grid_x + 1, grid_y),
        (grid_x, grid_y - 1), (grid_x, grid_y + 1),
        (grid_x - 1, grid_y - 1), (grid_x + 1, grid_y + 1),
        (grid_x - 1, grid_y + 1), (grid_x + 1, grid_y - 1),
    ]

    for adj_x, adj_y in adjacent_cells:
        if 0 <= adj_x < 100 and 0 <= adj_y < 100:
            neo4j_session.run(
                """
                MATCH (w1:Waypoint {pg_id: $waypoint_id})
                MATCH (w2:Waypoint)
                WHERE w2.grid_x = $adj_x AND w2.grid_y = $adj_y
                WITH w1, w2
                CREATE (w1)-[:GRID_ADJACENT {
                    distance_km: point.distance(
                        point({latitude: w1.lat, longitude: w1.lng}),
                        point({latitude: w2.lat, longitude: w2.lng})
                    ) / 1000
                }]->(w2)
                CREATE (w2)-[:GRID_ADJACENT {
                    distance_km: point.distance(
                        point({latitude: w2.lat, longitude: w2.lng}),
                        point({latitude: w1.lat, longitude: w1.lng})
                    ) / 1000
                }]->(w1)
                """,
                waypoint_id=waypoint_id,
                adj_x=adj_x,
                adj_y=adj_y,
            )
