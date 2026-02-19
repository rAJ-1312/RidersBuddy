from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from neo4j import Session as Neo4jSession
from app.api.rider.schemas import RiderCreate, RiderRead
from app.db.database import get_postgres_session, get_neo4j_session
from app.db.postgres_models import Rider

rider_router = APIRouter()


@rider_router.post("", response_model=RiderRead)
def create_rider(
    rider: RiderCreate,
    pg_db: Session = Depends(get_postgres_session),
    neo4j_db: Neo4jSession = Depends(get_neo4j_session),
):
    try:
        db_rider = Rider(
            name=rider.name,
            experience_level=rider.experience_level,
        )
        pg_db.add(db_rider)
        pg_db.flush()

        neo4j_db.run(
            """
            CREATE (r:Rider {
                pg_id: $pg_id,
                name: $name,
                experience_level: $experience_level
            })
            """,
            pg_id=db_rider.id,
            name=db_rider.name,
            experience_level=db_rider.experience_level,
        )

        pg_db.commit()
        return db_rider
    except IntegrityError:
        raise HTTPException(status_code=400, detail=f"Rider with name '{rider.name}' already exists")


@rider_router.get("", response_model=list[RiderRead])
def list_riders(pg_db: Session = Depends(get_postgres_session)):
    return pg_db.query(Rider).all()


@rider_router.get("/{rider_id}", response_model=RiderRead)
def get_rider(rider_id: int, pg_db: Session = Depends(get_postgres_session)):
    rider = pg_db.query(Rider).filter(Rider.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    return rider
