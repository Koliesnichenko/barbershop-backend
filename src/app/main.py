from fastapi import FastAPI
from src.app.routers import appointments

app = FastAPI()

app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])


@app.get("/")
def root():
    return {"message": "Barbershop backend is working"}