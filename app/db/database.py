import os
from contextlib import contextmanager
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from neo4j import GraphDatabase
from neomodel import config as neomodel_config

load_dotenv()

# PostgreSQL Configuration
POSTGRES_DATABASE_URL = os.environ["POSTGRES_DATABASE_URL"]

engine = create_engine(
    POSTGRES_DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_postgres_session():
    """Dependency for FastAPI to get a PostgreSQL session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Neo4j Configuration
NEO4J_URI = os.environ.get("NEO4J_DATABASE_URL")
NEO4J_USER = os.environ.get("NEO4J_USER")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

# Configure neomodel
NEO4J_URL = f"bolt://{NEO4J_USER}:{NEO4J_PASSWORD}@{NEO4J_URI.replace('bolt://', '')}"
neomodel_config.DATABASE_URL = NEO4J_URL

neo4j_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


def get_neo4j_session():
    """Dependency for FastAPI to get a Neo4j session."""
    with neo4j_driver.session() as session:
        yield session


@contextmanager
def neo4j_session_context():
    """Context manager for Neo4j session (for use outside FastAPI dependencies)."""
    session = neo4j_driver.session()
    try:
        yield session
    finally:
        session.close()


def close_postgres_engine():
    """Close the PostgreSQL engine connection pool (call on app shutdown)."""
    engine.dispose()


def close_neo4j_driver():
    """Close the Neo4j driver connection (call on app shutdown)."""
    neo4j_driver.close()
