# app/routers/medications.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/medications",
    tags=["medications"],
)


@router.post("/", response_model=schemas.MedicationRead, status_code=status.HTTP_201_CREATED)
def create_medication(
    medication_in: schemas.MedicationCreate,
    db: Session = Depends(get_db),
):
    db_med = models.Medication(**medication_in.dict())
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return db_med


@router.get("/", response_model=List[schemas.MedicationRead])
def list_medications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    meds = db.query(models.Medication).offset(skip).limit(limit).all()
    return meds


@router.get("/{medication_id}", response_model=schemas.MedicationRead)
def get_medication(
    medication_id: int,
    db: Session = Depends(get_db),
):
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
    med = db.query(models.Medication).filter(models.Medication.id == medication_id).first()
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")

    for field, value in medication_in.dict().items():
        setattr(med, field, value)

    db.commit()
    db.refresh(med)
    return med


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db),
):
    med = db.query(models.Medication).filter(models.Medication.id == medication_id).first()
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")

    db.delete(med)
    db.commit()
    return None
