from fastapi import FastAPI

from app.database import create_tables
from app.routers.health import router as health_router
from app.routers.services import router as services_router
from app.routers.teams import router as teams_router

app = FastAPI(title="Service Ownership API")

app.include_router(health_router)
app.include_router(teams_router)
app.include_router(services_router)


@app.on_event("startup")
def startup():
    create_tables()
