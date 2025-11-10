# app/main.py
from fastapi import FastAPI

from .database import Base, engine
from .routers import medications, prescriptions, dispensations
from . import es_client # NOVO: Importa o cliente ES para forçar a inicialização

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Farmácia & Prescrição Service",
    version="0.1.0",
    description="Microserviço responsável por catálogo de fármacos, prescrição e dispensação.",
)


@app.get("/", tags=["root"])
def root():
    """Endpoint raiz com informações básicas do serviço"""
    return {
        "service": "Farmácia & Prescrição",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "medications": "/medications",
            "prescriptions": "/prescriptions",
            "dispensations": "/dispensations"
        }
    }


@app.get("/health", tags=["health"])
def health_check():
    # NOVO: Verifica também a saúde do ES
    es_status = "ok" if es_client.es and es_client.es.ping() else "error"
    return {"status": "ok", "database": "ok", "elasticsearch": es_status}


app.include_router(medications.router)
app.include_router(prescriptions.router)
app.include_router(dispensations.router)