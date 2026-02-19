from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from app.api.route.schemas import (
    RouteDiscoverRequest,
    RouteDiscoverResponse,
    WaypointInRoute,
    RouteCreate,
    RouteRead,
)
from app.db.database import get_postgres_session, get_neo4j_session
from app.db.postgres_models import Route, RouteWaypoint, Waypoint

route_router = APIRouter()


@route_router.post("/discover", response_model=RouteDiscoverResponse)
def discover_route(
    request: RouteDiscoverRequest,
    neo4j_db: Neo4jSession = Depends(get_neo4j_session),
):
    result = neo4j_db.run(
        """
        MATCH (start:Waypoint {grid_x: $start_x, grid_y: $start_y})
        MATCH (end:Waypoint {grid_x: $end_x, grid_y: $end_y})
        MATCH path = shortestPath(
            (start)-[:GRID_ADJACENT*1..$max_hops]->(end)
        )
        WITH nodes(path) as waypoints, 
             relationships(path) as rels
        RETURN waypoints,
               reduce(dist = 0, r IN rels | dist + r.distance_km) as total_distance
        LIMIT 1
        """,
        start_x=request.start_grid[0],
        start_y=request.start_grid[1],
        end_x=request.end_grid[0],
        end_y=request.end_grid[1],
        max_hops=request.max_waypoints,
    )

    record = result.single()
    if not record:
        raise HTTPException(status_code=404, detail="No path found")

    waypoints = []
    for node in record["waypoints"]:
        waypoints.append(
            WaypointInRoute(
                id=node["pg_id"],
                name=node["name"],
                grid=[node["grid_x"], node["grid_y"]],
                lat=node["lat"],
                lng=node["lng"],
            )
        )

    return RouteDiscoverResponse(
        waypoints=waypoints,
        total_distance_km=round(record["total_distance"], 2),
    )


@route_router.post("", response_model=RouteRead)
def create_route(
    route: RouteCreate,
    pg_db: Session = Depends(get_postgres_session),
    neo4j_db: Neo4jSession = Depends(get_neo4j_session),
):
    if len(route.waypoint_ids) < 2:
        raise HTTPException(status_code=400, detail="Route must have at least 2 waypoints")

    waypoints = pg_db.query(Waypoint).filter(Waypoint.id.in_(route.waypoint_ids)).all()
    if len(waypoints) != len(route.waypoint_ids):
        raise HTTPException(status_code=404, detail="One or more waypoints not found")

    waypoint_map = {w.id: w for w in waypoints}
    ordered_waypoints = [waypoint_map[wid] for wid in route.waypoint_ids]

    total_distance = 0.0
    for i in range(len(ordered_waypoints) - 1):
        w1, w2 = ordered_waypoints[i], ordered_waypoints[i + 1]
        from app.spatial.grid import calculate_distance
        total_distance += calculate_distance(
            float(w1.lat), float(w1.lng),
            float(w2.lat), float(w2.lng)
        )

    db_route = Route(
        name=route.name,
        difficulty=route.difficulty,
        distance_km=round(total_distance, 2),
        start_waypoint_id=route.waypoint_ids[0],
        end_waypoint_id=route.waypoint_ids[-1],
    )
    pg_db.add(db_route)
    pg_db.flush()

    for seq, waypoint_id in enumerate(route.waypoint_ids):
        route_waypoint = RouteWaypoint(
            route_id=db_route.id,
            waypoint_id=waypoint_id,
            sequence_order=seq,
        )
        pg_db.add(route_waypoint)

    neo4j_db.run(
        """
        CREATE (r:Route {
            pg_id: $pg_id,
            name: $name,
            difficulty: $difficulty,
            distance_km: $distance_km
        })
        """,
        pg_id=db_route.id,
        name=db_route.name,
        difficulty=db_route.difficulty,
        distance_km=db_route.distance_km,
    )

    neo4j_db.run(
        """
        MATCH (r:Route {pg_id: $route_id})
        MATCH (start:Waypoint {pg_id: $start_id})
        MATCH (end:Waypoint {pg_id: $end_id})
        CREATE (r)-[:STARTS_AT]->(start)
        CREATE (r)-[:ENDS_AT]->(end)
        """,
        route_id=db_route.id,
        start_id=route.waypoint_ids[0],
        end_id=route.waypoint_ids[-1],
    )

    for seq, waypoint_id in enumerate(route.waypoint_ids):
        neo4j_db.run(
            """
            MATCH (r:Route {pg_id: $route_id})
            MATCH (w:Waypoint {pg_id: $waypoint_id})
            CREATE (r)-[:PASSES_THROUGH {sequence: $sequence}]->(w)
            """,
            route_id=db_route.id,
            waypoint_id=waypoint_id,
            sequence=seq,
        )

    pg_db.commit()
    return db_route


@route_router.get("", response_model=list[RouteRead])
def list_routes(pg_db: Session = Depends(get_postgres_session)):
    return pg_db.query(Route).all()


@route_router.get("/{route_id}", response_model=RouteRead)
def get_route(route_id: int, pg_db: Session = Depends(get_postgres_session)):
    route = pg_db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route
