from pydantic import BaseModel
from datetime import datetime


class RiderCreate(BaseModel):
    name: str
    experience_level: str


class RiderRead(BaseModel):
    id: int
    name: str
    experience_level: str
    created_at: datetime

    class Config:
        from_attributes = True


class RideRead(BaseModel):
    id: int
    rider_id: int
    route_id: int
    bike_id: int
    completed_at: datetime
    duration_minutes: int | None
    notes: str | None

    class Config:
        from_attributes = True
