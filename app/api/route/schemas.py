from datetime import datetime
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class Difficulty(str, Enum):
    EASY = "EASY"
    MODERATE = "MODERATE"
    HARD = "HARD"
    EXTREME = "EXTREME"


class RouteType(str, Enum):
    SCENIC = "scenic"
    HIGHWAY = "highway"
    OFFROAD = "offroad"
    MOUNTAIN = "mountain"
    COASTAL = "coastal"


# Base Route Schema
class RouteBase(BaseModel):
    name: str
    start_location: str
    end_location: str
    distance_km: float = Field(..., gt=0)
    difficulty: Difficulty
    description: str | None = None


class ScenicRouteCreate(RouteBase):
    route_type: Literal[RouteType.SCENIC] = RouteType.SCENIC
    scenic_points: list[str] = Field(default_factory=list, description="List of scenic viewpoints")
    best_season: str | None = Field(None, description="Best season to ride this route")
    photography_spots: int = Field(0, ge=0, description="Number of recommended photography spots")

    def get_route_info(self) -> str:
        """Returns information specific to scenic routes"""
        points = ", ".join(self.scenic_points) if self.scenic_points else "No specific points"
        return f"Scenic Route with {len(self.scenic_points)} viewpoints: {points}"


class HighwayRouteCreate(RouteBase):
    route_type: Literal[RouteType.HIGHWAY] = RouteType.HIGHWAY
    speed_limit: int = Field(..., gt=0, le=300, description="Speed limit in km/h")
    toll_cost: float = Field(0, ge=0, description="Total toll cost")
    rest_stops: list[str] = Field(default_factory=list, description="Available rest stops")
    lanes: int = Field(2, ge=1, le=8, description="Number of lanes")

    def get_route_info(self) -> str:
        """Returns information specific to highway routes"""
        return f"Highway Route: {self.lanes} lanes, {self.speed_limit}km/h, Toll: ${self.toll_cost}"
    
    def calculate_estimated_time(self) -> float:
        """Calculate estimated time based on speed limit"""
        return (self.distance_km / self.speed_limit) * 60


class OffroadRouteCreate(RouteBase):
    route_type: Literal[RouteType.OFFROAD] = RouteType.OFFROAD
    terrain_type: str = Field(..., description="Type of terrain: mud, sand, gravel, rocks, mixed")
    min_bike_cc: int = Field(250, gt=0, description="Minimum recommended engine CC")
    technical_difficulty: int = Field(..., ge=1, le=10, description="Technical difficulty rating (1-10)")
    requires_experience: bool = Field(True, description="Whether experience is required")

    @field_validator('terrain_type')
    @classmethod
    def validate_terrain(cls, v: str) -> str:
        valid_terrains = ['mud', 'sand', 'gravel', 'rocks', 'mixed', 'forest', 'desert']
        if v.lower() not in valid_terrains:
            raise ValueError(f"Terrain must be one of: {', '.join(valid_terrains)}")
        return v.lower()

    def get_route_info(self) -> str:
        """Returns information specific to offroad routes"""
        exp = "Experience required" if self.requires_experience else "Beginner friendly"
        return f"Offroad Route: {self.terrain_type.title()} terrain, Min {self.min_bike_cc}CC, {exp}"
    
    def is_suitable_for_bike(self, bike_cc: int) -> bool:
        """Check if a bike is suitable for this route"""
        return bike_cc >= self.min_bike_cc


class MountainRouteCreate(RouteBase):
    route_type: Literal[RouteType.MOUNTAIN] = RouteType.MOUNTAIN
    elevation_gain: float = Field(..., ge=0, description="Total elevation gain in meters")
    max_altitude: float = Field(..., ge=0, description="Maximum altitude in meters")
    hairpin_turns: int = Field(0, ge=0, description="Number of hairpin turns")
    oxygen_required: bool = Field(False, description="Whether supplemental oxygen might be needed")

    def get_route_info(self) -> str:
        """Returns information specific to mountain routes"""
        return f"Mountain Route: {self.elevation_gain}m gain, {self.max_altitude}m altitude, {self.hairpin_turns} hairpins"
    
    def get_difficulty_score(self) -> float:
        """Calculate difficulty score based on elevation and turns"""
        return (self.elevation_gain / 100) + (self.hairpin_turns * 2) + (self.max_altitude / 500)


class CoastalRouteCreate(RouteBase):
    route_type: Literal[RouteType.COASTAL] = RouteType.COASTAL
    beach_stops: list[str] = Field(default_factory=list, description="Beach stops along the route")
    lighthouse_count: int = Field(0, ge=0, description="Number of lighthouses on route")
    seafood_spots: list[str] = Field(default_factory=list, description="Recommended seafood restaurants")
    ocean_view_percentage: int = Field(50, ge=0, le=100, description="Percentage of route with ocean view")

    def get_route_info(self) -> str:
        """Returns information specific to coastal routes"""
        return f"Coastal Route: {len(self.beach_stops)} beaches, {self.ocean_view_percentage}% ocean view"


# Read Schemas (for responses)
class RouteRead(BaseModel):
    id: int
    name: str
    route_type: str
    start_location: str
    end_location: str
    distance_km: float
    difficulty: str
    description: str | None
    created_at: datetime
    
    # Scenic
    scenic_points: list[str] | None = None
    best_season: str | None = None
    photography_spots: int | None = None
    # Highway
    speed_limit: int | None = None
    toll_cost: float | None = None
    rest_stops: list[str] | None = None
    lanes: int | None = None
    # Offroad
    terrain_type: str | None = None
    min_bike_cc: int | None = None
    technical_difficulty: int | None = None
    requires_experience: bool | None = None
    # Mountain
    elevation_gain: float | None = None
    max_altitude: float | None = None
    hairpin_turns: int | None = None
    oxygen_required: bool | None = None
    # Coastal
    beach_stops: list[str] | None = None
    lighthouse_count: int | None = None
    seafood_spots: list[str] | None = None
    ocean_view_percentage: int | None = None

    class Config:
        from_attributes = True


def create_route_schema(route_type: RouteType, **kwargs):
    """Factory function to create appropriate route schema based on type"""
    route_classes = {
        RouteType.SCENIC: ScenicRouteCreate,
        RouteType.HIGHWAY: HighwayRouteCreate,
        RouteType.OFFROAD: OffroadRouteCreate,
        RouteType.MOUNTAIN: MountainRouteCreate,
        RouteType.COASTAL: CoastalRouteCreate,
    }
    
    route_class = route_classes.get(route_type)
    if not route_class:
        raise ValueError(f"Unknown route type: {route_type}")
    
    return route_class(**kwargs)
