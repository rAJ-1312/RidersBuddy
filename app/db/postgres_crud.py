from sqlalchemy.orm import Session
from . import postgres_models as models


def create_rider(
    db: Session,
    name: str,
    experience_level: str,
) -> models.Rider:
    rider = models.Rider(
        name=name,
        experience_level=experience_level,
    )
    db.add(rider)
    db.flush()
    db.refresh(rider)
    return rider


def get_riders(db: Session) -> list[models.Rider]:
    return db.query(models.Rider).all()


def get_rider_by_id(db: Session, rider_id: int) -> models.Rider | None:
    return db.query(models.Rider).filter(models.Rider.id == rider_id).first()


def create_bike(
    db: Session,
    owner_id: int,
    brand: str,
    model: str,
    year: int,
    engine_cc: int,
) -> models.Bike:
    bike = models.Bike(
        owner_id=owner_id,
        brand=brand,
        model=model,
        year=year,
        engine_cc=engine_cc,
    )
    db.add(bike)
    db.flush()
    db.refresh(bike)
    return bike


def get_bikes(db: Session) -> list[models.Bike]:
    return db.query(models.Bike).all()


def get_bike_by_id(db: Session, bike_id: int) -> models.Bike | None:
    return db.query(models.Bike).filter(models.Bike.id == bike_id).first()


def get_bikes_by_owner(db: Session, owner_id: int) -> list[models.Bike]:
    return db.query(models.Bike).filter(models.Bike.owner_id == owner_id).all()


def delete_rider(db: Session, rider_id: int) -> bool:
    rider = get_rider_by_id(db, rider_id)
    if not rider:
        return False
    db.delete(rider)
    return True


def delete_bike(db: Session, bike_id: int) -> bool:
    bike = get_bike_by_id(db, bike_id)
    if not bike:
        return False
    db.delete(bike)
    return True


def create_route(
    db: Session,
    name: str,
    start_location: str,
    end_location: str,
    distance_km: float,
    difficulty: str,
    route_type: str = "scenic",
    description: str | None = None,
    # Scenic fields
    scenic_points: list | None = None,
    best_season: str | None = None,
    photography_spots: int | None = None,
    # Highway fields
    speed_limit: int | None = None,
    toll_cost: float | None = None,
    rest_stops: list | None = None,
    lanes: int | None = None,
    # Offroad fields
    terrain_type: str | None = None,
    min_bike_cc: int | None = None,
    technical_difficulty: int | None = None,
    requires_experience: bool | None = None,
    # Mountain fields
    elevation_gain: float | None = None,
    max_altitude: float | None = None,
    hairpin_turns: int | None = None,
    oxygen_required: bool | None = None,
    # Coastal fields
    beach_stops: list | None = None,
    lighthouse_count: int | None = None,
    seafood_spots: list | None = None,
    ocean_view_percentage: int | None = None,
) -> models.Route:
    route = models.Route(
        name=name,
        route_type=route_type,
        start_location=start_location,
        end_location=end_location,
        distance_km=distance_km,
        difficulty=difficulty,
        description=description,
        # Scenic
        scenic_points=scenic_points,
        best_season=best_season,
        photography_spots=photography_spots,
        # Highway
        speed_limit=speed_limit,
        toll_cost=toll_cost,
        rest_stops=rest_stops,
        lanes=lanes,
        # Offroad
        terrain_type=terrain_type,
        min_bike_cc=min_bike_cc,
        technical_difficulty=technical_difficulty,
        requires_experience=requires_experience,
        # Mountain
        elevation_gain=elevation_gain,
        max_altitude=max_altitude,
        hairpin_turns=hairpin_turns,
        oxygen_required=oxygen_required,
        # Coastal
        beach_stops=beach_stops,
        lighthouse_count=lighthouse_count,
        seafood_spots=seafood_spots,
        ocean_view_percentage=ocean_view_percentage,
    )
    db.add(route)
    db.flush()
    db.refresh(route)
    return route


def get_routes(
    db: Session, 
    difficulty: str | None = None, 
    min_distance: float | None = None, 
    max_distance: float | None = None,
    route_type: str | None = None,
) -> list[models.Route]:
    query = db.query(models.Route)
    if difficulty:
        query = query.filter(models.Route.difficulty == difficulty)
    if min_distance is not None:
        query = query.filter(models.Route.distance_km >= min_distance)
    if max_distance is not None:
        query = query.filter(models.Route.distance_km <= max_distance)
    if route_type:
        query = query.filter(models.Route.route_type == route_type)
    return query.all()


def get_route_by_id(db: Session, route_id: int) -> models.Route | None:
    return db.query(models.Route).filter(models.Route.id == route_id).first()


def create_ride(
    db: Session,
    rider_id: int,
    route_id: int,
    bike_id: int,
    duration_minutes: int | None = None,
    notes: str | None = None,
) -> models.Ride:
    ride = models.Ride(
        rider_id=rider_id,
        route_id=route_id,
        bike_id=bike_id,
        duration_minutes=duration_minutes,
        notes=notes,
    )
    db.add(ride)
    db.flush()
    db.refresh(ride)
    return ride


def get_rides_by_rider(db: Session, rider_id: int) -> list[models.Ride]:
    return db.query(models.Ride).filter(models.Ride.rider_id == rider_id).all()


def get_ride_by_id(db: Session, ride_id: int) -> models.Ride | None:
    return db.query(models.Ride).filter(models.Ride.id == ride_id).first()


def delete_ride(db: Session, ride_id: int) -> bool:
    ride = get_ride_by_id(db, ride_id)
    if not ride:
        return False
    db.delete(ride)
    return True
