from pydantic import BaseModel
from datetime import datetime


class RouteDiscoverRequest(BaseModel):
    start_grid: list[int]
    end_grid: list[int]
    max_waypoints: int = 15


class WaypointInRoute(BaseModel):
    id: int
    name: str
    grid: list[int]
    lat: float
    lng: float


class RouteDiscoverResponse(BaseModel):
    waypoints: list[WaypointInRoute]
    total_distance_km: float


class RouteCreate(BaseModel):
    name: str
    waypoint_ids: list[int]
    difficulty: str


class RouteRead(BaseModel):
    id: int
    name: str
    difficulty: str
    distance_km: float
    created_at: datetime

    class Config:
        from_attributes = True

    def get_route_info(self) -> str:
        """Returns information specific to highway routes"""
        return f"Highway Route: {self.lanes} lanes, {self.speed_limit}km/h, Toll: ${self.toll_cost}"
    
    def calculate_estimated_time(self) -> float:
        """Calculate estimated time based on speed limit"""
        return (self.distance_km / self.speed_limit) * 60


class RouteCreate(BaseModel):
    name: str
    waypoint_ids: list[int]
    difficulty: str


class RouteRead(BaseModel):
    id: int
    name: str
    difficulty: str
    distance_km: float
    created_at: datetime

    class Config:
        from_attributes = True
