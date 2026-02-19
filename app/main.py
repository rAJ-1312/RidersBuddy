from contextlib import asynccontextmanager
from .db.database import engine, close_neo4j_driver, close_postgres_engine
from .db import postgres_models as models
from fastapi import FastAPI
from app.api.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_postgres_engine()
    close_neo4j_driver()


app = FastAPI(lifespan=lifespan, title="RidersBuddy", version="1.0.0")

models.Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Welcome to RidersBuddy API"}