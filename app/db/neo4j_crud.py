from loguru import logger
from neomodel.exceptions import DoesNotExist
from . import postgres_models as models
from .neo4j_models import RiderNode, BikeNode, RouteNode, RideNode


def create_rider_node(rider: models.Rider) -> RiderNode:
    return RiderNode(
        postgres_id=rider.id,
        name=rider.name,
        experience_level=rider.experience_level,
        joined_at=rider.joined_at,
    ).save()


def create_bike_node(bike: models.Bike) -> BikeNode:
    return BikeNode(
        postgres_id=bike.id,
        brand=bike.brand,
        model=bike.model,
        year=bike.year,
        engine_cc=bike.engine_cc,
    ).save()


def connect_bike_to_rider(owner_id: int, bike_id: int) -> None:
    rider_node = RiderNode.nodes.get(postgres_id=owner_id)
    bike_node = BikeNode.nodes.get(postgres_id=bike_id)
    rider_node.bikes.connect(bike_node)


def delete_rider_node(rider_id: int) -> None:
    try:
        rider_node = RiderNode.nodes.get(postgres_id=rider_id)
        rider_node.delete()
    except DoesNotExist:
        logger.warning(f"Rider node with postgres_id={rider_id} not found in Neo4j")


def delete_bike_node(bike_id: int) -> None:
    try:
        bike_node = BikeNode.nodes.get(postgres_id=bike_id)
        bike_node.delete()
    except DoesNotExist:
        logger.warning(f"Bike node with postgres_id={bike_id} not found in Neo4j")


def create_route_node(route: models.Route) -> RouteNode:
    return RouteNode(
        postgres_id=route.id,
        name=route.name,
        start_location=route.start_location,
        end_location=route.end_location,
        distance_km=route.distance_km,
        difficulty=route.difficulty,
        created_at=route.created_at,
    ).save()


def create_ride_node(ride: models.Ride) -> RideNode:
    return RideNode(
        postgres_id=ride.id,
        completed_at=ride.completed_at,
        duration_minutes=ride.duration_minutes,
    ).save()


def connect_ride_to_rider(rider_id: int, ride_id: int) -> None:
    rider_node = RiderNode.nodes.get(postgres_id=rider_id)
    ride_node = RideNode.nodes.get(postgres_id=ride_id)
    rider_node.rides.connect(ride_node)


def connect_ride_to_route(ride_id: int, route_id: int) -> None:
    ride_node = RideNode.nodes.get(postgres_id=ride_id)
    route_node = RouteNode.nodes.get(postgres_id=route_id)
    ride_node.route.connect(route_node)


def connect_ride_to_bike(ride_id: int, bike_id: int) -> None:
    ride_node = RideNode.nodes.get(postgres_id=ride_id)
    bike_node = BikeNode.nodes.get(postgres_id=bike_id)
    ride_node.bike.connect(bike_node)


def delete_ride_node(ride_id: int) -> None:
    try:
        ride_node = RideNode.nodes.get(postgres_id=ride_id)
        ride_node.delete()
    except DoesNotExist:
        logger.warning(f"Ride node with postgres_id={ride_id} not found in Neo4j")
