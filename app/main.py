from fastapi import FastAPI
from app.routers import health, events, risk

app = FastAPI(
    title="SoroWatch API",
    description="Coordinates the AI scoring agent and the on-chain risk registry.",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(risk.router, prefix="/risk", tags=["risk"])
