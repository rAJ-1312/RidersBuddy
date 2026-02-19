from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from app.api.ride.schemas import RideCreate, RideRead
from app.db.database import get_postgres_session, get_neo4j_session
from app.db.postgres_models import Ride, Rider, Route

ride_router = APIRouter()


@ride_router.post("", response_model=RideRead)
def create_ride(
    ride: RideCreate,
    pg_db: Session = Depends(get_postgres_session),
    neo4j_db: Neo4jSession = Depends(get_neo4j_session),
):
    rider = pg_db.query(Rider).filter(Rider.id == ride.rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")

    route = pg_db.query(Route).filter(Route.id == ride.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    db_ride = Ride(
        rider_id=ride.rider_id,
        route_id=ride.route_id,
        rating=ride.rating,
    )
    pg_db.add(db_ride)
    pg_db.flush()

    neo4j_db.run(
        """
        MATCH (rider:Rider {pg_id: $rider_id})
        MATCH (route:Route {pg_id: $route_id})
        CREATE (rider)-[:COMPLETED {
            completed_at: datetime(),
            rating: $rating
        }]->(route)
        """,
        rider_id=ride.rider_id,
        route_id=ride.route_id,
        rating=ride.rating,
    )

    pg_db.commit()
    return db_ride


@ride_router.get("", response_model=list[RideRead])
def list_rides(
    rider_id: int | None = None,
    pg_db: Session = Depends(get_postgres_session),
):
    query = pg_db.query(Ride)
    if rider_id:
        query = query.filter(Ride.rider_id == rider_id)
    return query.all()