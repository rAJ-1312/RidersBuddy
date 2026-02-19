from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, ForeignKey, DateTime, Float, Integer, Numeric
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


class Rider(Base):
    __tablename__ = "riders"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True, unique=True)
    experience_level: Mapped[str] = mapped_column(
        String(20), default=ExperienceLevel.BEGINNER.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    rides: Mapped[list["Ride"]] = relationship(
        back_populates="rider",
        cascade="all, delete-orphan",
    )


class Waypoint(Base):
    __tablename__ = "waypoints"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    grid_x: Mapped[int] = mapped_column(Integer, index=True)
    grid_y: Mapped[int] = mapped_column(Integer, index=True)
    lat: Mapped[float] = mapped_column(Numeric(10, 7))
    lng: Mapped[float] = mapped_column(Numeric(10, 7))
    type: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    route_waypoints: Mapped[list["RouteWaypoint"]] = relationship(
        back_populates="waypoint",
        cascade="all, delete-orphan",
    )


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    difficulty: Mapped[str] = mapped_column(String(20), index=True)
    distance_km: Mapped[float] = mapped_column(Float)
    start_waypoint_id: Mapped[int] = mapped_column(ForeignKey("waypoints.id"))
    end_waypoint_id: Mapped[int] = mapped_column(ForeignKey("waypoints.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    start_waypoint: Mapped["Waypoint"] = relationship(foreign_keys=[start_waypoint_id])
    end_waypoint: Mapped["Waypoint"] = relationship(foreign_keys=[end_waypoint_id])
    waypoints: Mapped[list["RouteWaypoint"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="RouteWaypoint.sequence_order",
    )
    rides: Mapped[list["Ride"]] = relationship(
        back_populates="route",
        cascade="all, delete-orphan",
    )


class RouteWaypoint(Base):
    __tablename__ = "route_waypoints"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), index=True)
    waypoint_id: Mapped[int] = mapped_column(ForeignKey("waypoints.id"), index=True)
    sequence_order: Mapped[int] = mapped_column(Integer)

    route: Mapped["Route"] = relationship(back_populates="waypoints")
    waypoint: Mapped["Waypoint"] = relationship(back_populates="route_waypoints")


class Ride(Base):
    __tablename__ = "rides"

    id: Mapped[int] = mapped_column(primary_key=True)
    rider_id: Mapped[int] = mapped_column(ForeignKey("riders.id"))
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    completed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    rating: Mapped[int] = mapped_column(Integer)

    rider: Mapped["Rider"] = relationship(back_populates="rides")
    route: Mapped["Route"] = relationship(back_populates="rides")
