from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, ForeignKey, DateTime, Float, Text, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Difficulty(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    EXTREME = "extreme"


class RouteType(str, Enum):
    SCENIC = "scenic"
    HIGHWAY = "highway"
    OFFROAD = "offroad"
    MOUNTAIN = "mountain"
    COASTAL = "coastal"


class Rider(Base):
    __tablename__ = "riders"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True, unique=True)
    experience_level: Mapped[str] = mapped_column(
        String(20), default=ExperienceLevel.BEGINNER.value
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    bikes: Mapped[list["Bike"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    rides: Mapped[list["Ride"]] = relationship(
        back_populates="rider",
        cascade="all, delete-orphan",
    )


class Bike(Base):
    __tablename__ = "bikes"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("riders.id"))
    brand: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column()
    engine_cc: Mapped[int] = mapped_column()

    owner: Mapped["Rider"] = relationship(back_populates="bikes")


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    route_type: Mapped[str] = mapped_column(String(20), default=RouteType.SCENIC.value, index=True)
    start_location: Mapped[str] = mapped_column(String(200))
    end_location: Mapped[str] = mapped_column(String(200))
    distance_km: Mapped[float] = mapped_column(Float)
    difficulty: Mapped[str] = mapped_column(String(20), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Scenic route fields
    scenic_points: Mapped[list | None] = mapped_column(JSON, nullable=True)
    best_season: Mapped[str | None] = mapped_column(String(50), nullable=True)
    photography_spots: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Highway route fields
    speed_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    toll_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    rest_stops: Mapped[list | None] = mapped_column(JSON, nullable=True)
    lanes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Offroad route fields
    terrain_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    min_bike_cc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    technical_difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requires_experience: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    
    # Mountain route fields
    elevation_gain: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_altitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    hairpin_turns: Mapped[int | None] = mapped_column(Integer, nullable=True)
    oxygen_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    
    # Coastal route fields
    beach_stops: Mapped[list | None] = mapped_column(JSON, nullable=True)
    lighthouse_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seafood_spots: Mapped[list | None] = mapped_column(JSON, nullable=True)
    ocean_view_percentage: Mapped[int | None] = mapped_column(Integer, nullable=True)

    rides: Mapped[list["Ride"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
    )


class Ride(Base):
    __tablename__ = "rides"

    id: Mapped[int] = mapped_column(primary_key=True)
    rider_id: Mapped[int] = mapped_column(ForeignKey("riders.id"))
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    bike_id: Mapped[int] = mapped_column(ForeignKey("bikes.id"))
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    duration_minutes: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    rider: Mapped["Rider"] = relationship(back_populates="rides")
    route: Mapped["Route"] = relationship(back_populates="rides")
