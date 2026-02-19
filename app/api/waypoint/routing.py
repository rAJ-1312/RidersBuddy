from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from app.api.waypoint.schemas import WaypointCreate, WaypointRead
from app.db.database import get_postgres_session, get_neo4j_session
from app.db.postgres_models import Waypoint
from app.db.neo4j_models import WaypointNode
from app.spatial.grid import connect_waypoint_to_grid
from math import radians, sin, cos, sqrt, atan2

waypoint_router = APIRouter()


@waypoint_router.post("", response_model=WaypointRead)
def create_waypoint(
    waypoint: WaypointCreate,
    pg_db: Session = Depends(get_postgres_session),
    neo4j_db: Neo4jSession = Depends(get_neo4j_session),
):
    db_waypoint = Waypoint(
        name=waypoint.name,
        grid_x=waypoint.grid_x,
        grid_y=waypoint.grid_y,
        lat=waypoint.lat,
        lng=waypoint.lng,
        type=waypoint.type,
    )
    pg_db.add(db_waypoint)
    pg_db.flush()
    pg_db.refresh(db_waypoint)

    neo4j_db.run(
        """
        CREATE (w:Waypoint {
            pg_id: $pg_id,
            name: $name,
            grid_x: $grid_x,
            grid_y: $grid_y,
            lat: $lat,
            lng: $lng,
            type: $type
        })
        """,
        pg_id=db_waypoint.id,
        name=db_waypoint.name,
        grid_x=db_waypoint.grid_x,
        grid_y=db_waypoint.grid_y,
        lat=float(db_waypoint.lat),
        lng=float(db_waypoint.lng),
        type=db_waypoint.type,
    )

    connect_waypoint_to_grid(neo4j_db, db_waypoint.id, waypoint.grid_x, waypoint.grid_y)

    pg_db.commit()
    return db_waypoint


@waypoint_router.get("", response_model=list[WaypointRead])
def list_waypoints(
    grid_x: int | None = Query(None, ge=0, le=99),
    grid_y: int | None = Query(None, ge=0, le=99),
    pg_db: Session = Depends(get_postgres_session),
):
    query = pg_db.query(Waypoint)
    if grid_x is not None:
        query = query.filter(Waypoint.grid_x == grid_x)
    if grid_y is not None:
        query = query.filter(Waypoint.grid_y == grid_y)
    return query.all()


@waypoint_router.get("/{waypoint_id}", response_model=WaypointRead)
def get_waypoint(
    waypoint_id: int,
    pg_db: Session = Depends(get_postgres_session),
):
    waypoint = pg_db.query(Waypoint).filter(Waypoint.id == waypoint_id).first()
    if not waypoint:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Waypoint not found")
    return waypoint
