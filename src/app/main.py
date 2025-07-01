import os
from dotenv import load_dotenv
from starlette.concurrency import run_in_threadpool

load_dotenv()
print("DEBUG from main.py: DATABASE_URL =", os.getenv("DATABASE_URL"))

from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from src.app.core.config import settings

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.app.core.redis_client import get_redis_client, close_redis_connection_pool

from src.app.routers import barbers, services, appointments, addons, timeslots
from src.app.auth.router import router as auth_router

import logging
import sys


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logging.getLogger("src.app.services.email_service").propagate = False
logging.getLogger("src.app.auth.router").propagate = False

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Barbershop API",
    version="1.0.0",
    default_response_class=ORJSONResponse
)


@app.on_event("startup")
def startup_event():
    logger.debug("Application startup event triggered.")
    get_redis_client()
    logger.debug("Redis client initialized.")


@app.on_event("shutdown")
def shutdown_event():
    logger.info("DEBUG: Application shutdown event triggered.")
    close_redis_connection_pool()
    logger.info("DEBUG: Redis client connection closed.")


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://192.168.10.188:3000/",
    "http://172.31.48.1:3000/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(barbers.router, prefix="/api/barbers", tags=["Barbers"])
app.include_router(addons.router, prefix="/api/addons", tags=["Addons"])
app.include_router(timeslots.router, prefix="/api/timeslots", tags=["Timeslots"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Barbershop API",
        version="1.0.0",
        description="API for Barbershop",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    public_paths = {
        "/": ["get"],
        "/api/auth/login": ["post"],
        "/api/auth/register": ["post"],
    }

    for path, path_item in openapi_schema["paths"].items():
        for method, method_item in path_item.items():
            if method in public_paths.get(path, []):
                method_item["security"] = []
            else:
                method_item.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
def root():
    return {"message": "Barbershop backend is working"}
