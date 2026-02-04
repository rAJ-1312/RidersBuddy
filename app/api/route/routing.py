from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Union, Annotated
from app.api.route.schemas import (
    ScenicRouteCreate, HighwayRouteCreate, OffroadRouteCreate,
    MountainRouteCreate, CoastalRouteCreate, RouteRead
)
from app.api.route.examples import ALL_ROUTE_EXAMPLES
from app.db.database import get_postgres_session
from app.exceptions import DuplicateResourceError
import app.db.postgres_crud as pg_crud
import app.db.neo4j_crud as neo_crud

route_router = APIRouter()


@route_router.post("", response_model=RouteRead, tags=["Routes"])
def create_route(
    route: Annotated[
        Union[ScenicRouteCreate, HighwayRouteCreate, OffroadRouteCreate, MountainRouteCreate, CoastalRouteCreate],
        Body(
            openapi_examples={
                "scenic_route": {
                    "summary": "Scenic Route Example",
                    "description": "Create a scenic route with viewpoints and photography spots",
                    "value": ALL_ROUTE_EXAMPLES["scenic_route"]
                },
                "highway_route": {
                    "summary": "Highway Route Example",
                    "description": "Create a highway route with speed limits and tolls",
                    "value": ALL_ROUTE_EXAMPLES["highway_route"]
                },
                "offroad_route": {
                    "summary": "Offroad Route Example",
                    "description": "Create an offroad route with terrain and technical difficulty",
                    "value": ALL_ROUTE_EXAMPLES["offroad_route"]
                },
                "mountain_route": {
                    "summary": "Mountain Route Example",
                    "description": "Create a mountain route with elevation and hairpin turns",
                    "value": ALL_ROUTE_EXAMPLES["mountain_route"]
                },
                "coastal_route": {
                    "summary": "Coastal Route Example",
                    "description": "Create a coastal route with beach stops and ocean views",
                    "value": ALL_ROUTE_EXAMPLES["coastal_route"]
                }
            }
        )
    ],
    db: Session = Depends(get_postgres_session),
):
    """Create a new route of various types"""
    try:
        # Extract common fields
        route_data = {
            "name": route.name,
            "start_location": route.start_location,
            "end_location": route.end_location,
            "distance_km": route.distance_km,
            "difficulty": route.difficulty.value,
            "description": route.description,
            "route_type": route.route_type.value,
        }
        
        # Add type-specific fields based on route type
        if isinstance(route, ScenicRouteCreate):
            route_data.update({
                "scenic_points": route.scenic_points,
                "best_season": route.best_season,
                "photography_spots": route.photography_spots,
            })
        elif isinstance(route, HighwayRouteCreate):
            route_data.update({
                "speed_limit": route.speed_limit,
                "toll_cost": route.toll_cost,
                "rest_stops": route.rest_stops,
                "lanes": route.lanes,
            })
        elif isinstance(route, OffroadRouteCreate):
            route_data.update({
                "terrain_type": route.terrain_type,
                "min_bike_cc": route.min_bike_cc,
                "technical_difficulty": route.technical_difficulty,
                "requires_experience": route.requires_experience,
            })
        elif isinstance(route, MountainRouteCreate):
            route_data.update({
                "elevation_gain": route.elevation_gain,
                "max_altitude": route.max_altitude,
                "hairpin_turns": route.hairpin_turns,
                "oxygen_required": route.oxygen_required,
            })
        elif isinstance(route, CoastalRouteCreate):
            route_data.update({
                "beach_stops": route.beach_stops,
                "lighthouse_count": route.lighthouse_count,
                "seafood_spots": route.seafood_spots,
                "ocean_view_percentage": route.ocean_view_percentage,
            })
        
        db_route = pg_crud.create_route(db, **route_data)
        neo_crud.create_route_node(db_route)
        return db_route
    except IntegrityError:
        raise DuplicateResourceError(resource="Route", detail=f"Route with name '{route.name}' already exists")


@route_router.get("", response_model=list[RouteRead], tags=["Routes"])
def list_routes(
    difficulty: str | None = Query(None),
    min_distance: float | None = Query(None),
    max_distance: float | None = Query(None),
    route_type: str | None = Query(None, description="Filter by route type: scenic, highway, offroad, mountain, coastal"),
    db: Session = Depends(get_postgres_session),
):
    """List all routes with optional filters"""
    return pg_crud.get_routes(
        db, 
        difficulty=difficulty, 
        min_distance=min_distance, 
        max_distance=max_distance,
        route_type=route_type
    )
