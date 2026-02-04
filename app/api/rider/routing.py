from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.api.rider.schemas import RiderCreate, RiderRead, BikeCreate, BikeRead, RideRead
from app.db.database import get_postgres_session
from app.exceptions import DuplicateResourceError, ResourceNotFoundError
import app.db.postgres_crud as pg_crud
import app.db.neo4j_crud as neo_crud

rider_router = APIRouter()


@rider_router.post("", response_model=RiderRead)
def create_rider(
    rider: RiderCreate,
    db: Session = Depends(get_postgres_session),
):
    """Create a new rider profile."""
    try:
        db_rider = pg_crud.create_rider(
            db,
            name=rider.name,
            experience_level=rider.experience_level.value,
        )
        neo_crud.create_rider_node(db_rider)
        return db_rider
    except IntegrityError:
        raise DuplicateResourceError(resource="Rider", detail=f"Rider with name '{rider.name}' already exists")


@rider_router.get("", response_model=list[RiderRead])
def list_riders(db: Session = Depends(get_postgres_session)):
    """Get all riders."""
    return pg_crud.get_riders(db)


@rider_router.get("/{rider_id}", response_model=RiderRead)
def get_rider(rider_id: int, db: Session = Depends(get_postgres_session)):
    """Get a specific rider by ID."""
    rider = pg_crud.get_rider_by_id(db, rider_id)
    if not rider:
        raise ResourceNotFoundError(resource="Rider", identifier=rider_id)
    return rider


@rider_router.get("/{rider_id}/rides", response_model=list[RideRead])
def view_ride_history(rider_id: int, db: Session = Depends(get_postgres_session)):
    rider = pg_crud.get_rider_by_id(db, rider_id)
    if not rider:
        raise ResourceNotFoundError(resource="Rider", identifier=rider_id)
    return pg_crud.get_rides_by_rider(db, rider_id)


@rider_router.post("/{rider_id}/bikes", response_model=BikeRead)
def add_bike_to_garage(
    rider_id: int,
    bike: BikeCreate,
    db: Session = Depends(get_postgres_session),
):
    """Add bike to rider's garage."""
    rider = pg_crud.get_rider_by_id(db, rider_id)
    if not rider:
        raise ResourceNotFoundError(resource="Rider", identifier=rider_id)
    
    db_bike = pg_crud.create_bike(
        db,
        owner_id=rider_id,
        brand=bike.brand,
        model=bike.model,
        year=bike.year,
        engine_cc=bike.engine_cc,
    )
    neo_crud.create_bike_node(db_bike)
    neo_crud.connect_bike_to_rider(rider_id, db_bike.id)
    return db_bike


@rider_router.get("/{rider_id}/bikes", response_model=list[BikeRead])
def view_garage(rider_id: int, db: Session = Depends(get_postgres_session)):
    """View rider's garage (all bikes)."""
    rider = pg_crud.get_rider_by_id(db, rider_id)
    if not rider:
        raise ResourceNotFoundError(resource="Rider", identifier=rider_id)
    return pg_crud.get_bikes_by_owner(db, rider_id)


@rider_router.get("/{rider_id}/bikes/{bike_id}", response_model=BikeRead)
def view_bike(
    rider_id: int,
    bike_id: int,
    db: Session = Depends(get_postgres_session)
):
    """View a specific bike in rider's garage."""
    rider = pg_crud.get_rider_by_id(db, rider_id)
    if not rider:
        raise ResourceNotFoundError(resource="Rider", identifier=rider_id)
    
    bike = pg_crud.get_bike_by_id(db, bike_id)
    if not bike:
        raise ResourceNotFoundError(resource="Bike", identifier=bike_id)
    
    if bike.owner_id != rider_id:
        raise ResourceNotFoundError(resource="Bike", identifier=bike_id, detail=f"Bike {bike_id} does not belong to rider {rider_id}")
    
    return bike


@rider_router.delete("/{rider_id}")
def delete_rider(rider_id: int, db: Session = Depends(get_postgres_session)):
    """Delete a rider and all their bikes."""
    if not pg_crud.delete_rider(db, rider_id):
        raise ResourceNotFoundError(resource="Rider", identifier=rider_id)
    neo_crud.delete_rider_node(rider_id)
    return {"message": f"Rider {rider_id} deleted successfully"}


@rider_router.delete("/{rider_id}/bikes/{bike_id}")
def delete_bike(
    rider_id: int,
    bike_id: int,
    db: Session = Depends(get_postgres_session)
):
    """Remove a bike from rider's garage."""
    rider = pg_crud.get_rider_by_id(db, rider_id)
    if not rider:
        raise ResourceNotFoundError(resource="Rider", identifier=rider_id)
    
    bike = pg_crud.get_bike_by_id(db, bike_id)
    if not bike:
        raise ResourceNotFoundError(resource="Bike", identifier=bike_id)
    
    if bike.owner_id != rider_id:
        raise ResourceNotFoundError(resource="Bike", identifier=bike_id, detail=f"Bike {bike_id} does not belong to rider {rider_id}")
    
    pg_crud.delete_bike(db, bike_id)
    neo_crud.delete_bike_node(bike_id)
    return {"message": f"Bike {bike_id} removed from rider {rider_id}'s garage"}
