# app/main.py
from fastapi import FastAPI

from .database import Base, engine
from .routers import medications, prescriptions, dispensations

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Farmácia & Prescrição Service",
    version="0.1.0",
    description="Microserviço responsável por catálogo de fármacos, prescrição e dispensação.",
)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(medications.router)
app.include_router(prescriptions.router)
app.include_router(dispensations.router)
