from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ExperienceLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class RiderCreate(BaseModel):
    name: str
    experience_level: ExperienceLevel = ExperienceLevel.BEGINNER


class RiderRead(BaseModel):
    id: int
    name: str
    experience_level: str
    joined_at: datetime

    class Config:
        from_attributes = True

class BikeCreate(BaseModel):
    model: str
    brand: str
    year: int = Field(..., gt=1900, le=2100)
    engine_cc: int = Field(..., gt=0)


class BikeRead(BaseModel):
    id: int
    owner_id: int
    model: str
    brand: str
    year: int
    engine_cc: int

    class Config:
        from_attributes = True


class RideCreate(BaseModel):
    route_id: int
    bike_id: int
    duration_minutes: int | None = None
    notes: str | None = None


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
