import random
from sqlalchemy.orm import Session
from neo4j import Session as Neo4jSession
from app.db.postgres_models import Rider, Waypoint
from app.spatial.grid import connect_waypoint_to_grid


class GridFactory:
    def __init__(self, pg_db: Session, neo4j_db: Neo4jSession):
        self.pg_db = pg_db
        self.neo4j_db = neo4j_db

    def grid_to_coordinates(self, grid_x: int, grid_y: int) -> tuple[float, float]:
        lat = 32.5 + (grid_y / 100.0) * 9.5
        lng = -124.5 + (grid_x / 100.0) * 10.5
        return lat, lng

    def populate_grid(self, count: int = 500) -> list[Waypoint]:
        waypoints = []
        for i in range(count):
            grid_x = random.randint(0, 99)
            grid_y = random.randint(0, 99)
            lat, lng = self.grid_to_coordinates(grid_x, grid_y)

            waypoint = Waypoint(
                name=f"Waypoint_{grid_x}_{grid_y}_{i}",
                grid_x=grid_x,
                grid_y=grid_y,
                lat=lat,
                lng=lng,
                type=random.choice(["viewpoint", "cafe", "rest_area", "fuel_station"]),
            )
            self.pg_db.add(waypoint)
            self.pg_db.flush()

            self.neo4j_db.run(
                """
                CREATE (w:Waypoint {
                    pg_id: $pg_id,
                    name: $name,
                    grid_x: $grid_x,
                    grid_y: $grid_y,
                    lat: $lat,
                    lng: $lng,
                    type: $type
                })
                """,
                pg_id=waypoint.id,
                name=waypoint.name,
                grid_x=waypoint.grid_x,
                grid_y=waypoint.grid_y,
                lat=float(waypoint.lat),
                lng=float(waypoint.lng),
                type=waypoint.type,
            )

            connect_waypoint_to_grid(self.neo4j_db, waypoint.id, grid_x, grid_y)
            waypoints.append(waypoint)

        self.pg_db.commit()
        return waypoints


class RiderFactory:
    def __init__(self, pg_db: Session, neo4j_db: Neo4jSession):
        self.pg_db = pg_db
        self.neo4j_db = neo4j_db

    def create_riders(self, count: int = 20) -> list[Rider]:
        riders = []
        for i in range(count):
            rider = Rider(
                name=f"Rider_{i}",
                experience_level=random.choice(["beginner", "intermediate", "advanced", "expert"]),
            )
            self.pg_db.add(rider)
            self.pg_db.flush()

            self.neo4j_db.run(
                """
                CREATE (r:Rider {
                    pg_id: $pg_id,
                    name: $name,
                    experience_level: $experience_level
                })
                """,
                pg_id=rider.id,
                name=rider.name,
                experience_level=rider.experience_level,
            )
            riders.append(rider)

        self.pg_db.commit()
        return riders
