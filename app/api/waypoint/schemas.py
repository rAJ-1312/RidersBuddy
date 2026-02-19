from pydantic import BaseModel, Field
from datetime import datetime


class WaypointCreate(BaseModel):
    name: str
    grid_x: int = Field(ge=0, le=99)
    grid_y: int = Field(ge=0, le=99)
    lat: float
    lng: float
    type: str


class WaypointRead(BaseModel):
    id: int
    name: str
    grid_x: int
    grid_y: int
    lat: float
    lng: float
    type: str
    created_at: datetime

    class Config:
        from_attributes = True
