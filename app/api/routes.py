"""API router."""

from fastapi import APIRouter

from app.api.rider.routing import rider_router
from app.api.route.routing import route_router
from app.api.ride.routing import ride_router


api_router = APIRouter()
api_router.include_router(rider_router, prefix="/riders", tags=["Riders"])
api_router.include_router(route_router, prefix="/routes", tags=["Routes"])
api_router.include_router(ride_router, prefix="/rides", tags=["Rides"])
