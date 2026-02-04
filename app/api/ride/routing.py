from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.rider.schemas import RideCreate, RideRead
from app.db.database import get_postgres_session
from app.exceptions import ResourceNotFoundError
import app.db.postgres_crud as pg_crud
import app.db.neo4j_crud as neo_crud

ride_router = APIRouter()


@ride_router.post("", response_model=RideRead, tags=["Rides"])
def log_ride(
    ride: RideCreate,
    db: Session = Depends(get_postgres_session),
):
    route = pg_crud.get_route_by_id(db, ride.route_id)
    if not route:
        raise ResourceNotFoundError(resource="Route", identifier=ride.route_id)
    
    bike = pg_crud.get_bike_by_id(db, ride.bike_id)
    if not bike:
        raise ResourceNotFoundError(resource="Bike", identifier=ride.bike_id)
    
    rider_id = bike.owner_id
    
    db_ride = pg_crud.create_ride(
        db,
        rider_id=rider_id,
        route_id=ride.route_id,
        bike_id=ride.bike_id,
        duration_minutes=ride.duration_minutes,
        notes=ride.notes,
    )
    
    ride_node = neo_crud.create_ride_node(db_ride)
    neo_crud.connect_ride_to_rider(rider_id, db_ride.id)
    neo_crud.connect_ride_to_route(db_ride.id, ride.route_id)
    neo_crud.connect_ride_to_bike(db_ride.id, ride.bike_id)
    
    return db_ride


@ride_router.delete("/{ride_id}", tags=["Rides"])
def delete_ride(
    ride_id: int,
    db: Session = Depends(get_postgres_session),
):
    """Delete a logged ride (e.g., if added by mistake)"""
    ride = pg_crud.get_ride_by_id(db, ride_id)
    if not ride:
        raise ResourceNotFoundError(resource="Ride", identifier=ride_id)
    
    # Delete from Neo4j first
    neo_crud.delete_ride_node(ride_id)
    
    # Delete from PostgreSQL
    success = pg_crud.delete_ride(db, ride_id)
    if not success:
        raise ResourceNotFoundError(resource="Ride", identifier=ride_id)
    
    return {"message": f"Ride {ride_id} deleted successfully"}
