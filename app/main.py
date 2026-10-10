
from fastapi import FastAPI

from .database import Base, engine
from . import models
from .routes import router as jobs_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Certificate Generator")

app.include_router(jobs_router)


@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }