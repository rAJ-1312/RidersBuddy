from pydantic import BaseModel, Field
from datetime import datetime


class RideCreate(BaseModel):
    rider_id: int
    route_id: int
    rating: int = Field(ge=1, le=5)


class RideRead(BaseModel):
    id: int
    rider_id: int
    route_id: int
    completed_at: datetime
    rating: int

    class Config:
        from_attributes = True
