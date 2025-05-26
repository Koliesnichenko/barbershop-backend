from fastapi import FastAPI
from src.app.routers import appointments
from src.app.auth.router import router as auth_router

app = FastAPI()

app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(auth_router.router, prefix="/api/auth", tags=["Auth"])


@app.get("/")
def root():
    return {"message": "Barbershop backend is working"}