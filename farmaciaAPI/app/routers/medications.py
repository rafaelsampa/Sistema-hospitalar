# app/routers/medications.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from elasticsearch import helpers # NOVO

from .. import models, schemas
from ..database import get_db

# NOVO: Importar o cliente 'es' e funções auxiliares do es_client
from .. import es_client 

router = APIRouter(
    prefix="/medications",
    tags=["medications"],
)

@router.post("/", response_model=schemas.MedicationRead, status_code=status.HTTP_201_CREATED)
def create_medication(
    medication_in: schemas.MedicationCreate,
    db: Session = Depends(get_db),
):
    # 1. Salva no PostgreSQL (Fonte da Verdade)
    db_med = models.Medication(**medication_in.dict())
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    
    # 2. NOVO: Indexa no Elasticsearch
    es_client.index_medication(medication_in.dict(), db_med.id)
    
    return db_med

# NOVO: Endpoint de Busca (lógica do 'pesquisa()' do teste.py)
@router.get("/search", response_model=List[schemas.MedicationRead])
def search_medications(q: str):
    if es_client.es is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de busca (Elasticsearch) está indisponível."
        )

    query = {
        "query": {
            "wildcard": {
                "nome": {
                    "value": f"*{q}*",
                    "case_sensitive": True,
                    "boost": 1.0,
                    "rewrite": "constant_score"
                }
            }
        }
    }
    
    results = []
    try:
        for doc in helpers.scan(es_client.es, query=query, index=es_client.INDEX_NAME):
            # Recria o schema de resposta a partir do ES
            # Nota: O ID é pego do ES, que é o mesmo do Postgres
            source = doc['_source']
            results.append(schemas.MedicationRead(
                id=int(doc['_id']),
                name=source.get('nome'),
                description=source.get('descricao'),
                dosage_form=source.get('forma_dosagem'),
                strength=source.get('forca'),
                route=source.get('rota'),
                atc_code=source.get('codigo_atc'),
                is_active=source.get('ativo', True)
            ))
    except Exception as e:
        print(f"Erro na busca do Elasticsearch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar no Elasticsearch: {e}"
        )
    
    return results


@router.get("/", response_model=List[schemas.MedicationRead])
def list_medications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    # Este endpoint continua pegando do PostgreSQL (para paginação simples)
    # Se preferir, pode alterar para usar o 'mostrarTodos' do teste.py
    meds = db.query(models.Medication).offset(skip).limit(limit).all()
    return meds


@router.get("/{medication_id}", response_model=schemas.MedicationRead)
def get_medication(
    medication_id: int,
    db: Session = Depends(get_db),
):
    # Pega da "fonte da verdade" (Postgres)
    med = db.query(models.Medication).filter(models.Medication.id == medication_id).first()
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    return med


@router.put("/{medication_id}", response_model=schemas.MedicationRead)
def update_medication(
    medication_id: int,
    medication_in: schemas.MedicationCreate,
    db: Session = Depends(get_db),
):
    # 1. Atualiza no PostgreSQL
    med = db.query(models.Medication).filter(models.Medication.id == medication_id).first()
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")

    for field, value in medication_in.dict().items():
        setattr(med, field, value)

    db.commit()
    db.refresh(med)
    
    # 2. NOVO: Re-indexa no Elasticsearch
    es_client.index_medication(medication_in.dict(), medication_id)
    
    return med


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db),
):
    # 1. Deleta do PostgreSQL
    med = db.query(models.Medication).filter(models.Medication.id == medication_id).first()
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")

    db.delete(med)
    db.commit()
    
    # 2. NOVO: Remove do índice do Elasticsearch
    es_client.remove_medication_from_index(medication_id)
    
    return None