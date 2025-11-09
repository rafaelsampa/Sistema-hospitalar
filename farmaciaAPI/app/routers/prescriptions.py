# app/routers/prescriptions.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/prescriptions",
    tags=["prescriptions"],
)


@router.post(
    "/",
    response_model=schemas.PrescriptionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_prescription(
    prescription_in: schemas.PrescriptionCreate,
    db: Session = Depends(get_db),
):
    # cria o cabeçalho
    db_prescription = models.Prescription(
        patient_id=prescription_in.patient_id,
        prescriber_id=prescription_in.prescriber_id,
        status=prescription_in.status or "DRAFT",
        notes=prescription_in.notes,
    )
    db.add(db_prescription)
    db.flush()  # garante que db_prescription.id existe

    # cria os itens
    items_db = []
    for item in prescription_in.items:
        # opcionalmente aqui você poderia validar se o medication_id existe:
        # med = db.query(models.Medication).get(item.medication_id)

        db_item = models.PrescriptionItem(
            prescription_id=db_prescription.id,
            medication_id=item.medication_id,
            dose=item.dose,
            frequency=item.frequency,
            route=item.route,
            duration=item.duration,
            instructions=item.instructions,
        )
        db.add(db_item)
        items_db.append(db_item)

    db.commit()
    db.refresh(db_prescription)

    return db_prescription


@router.get("/", response_model=List[schemas.PrescriptionRead])
def list_prescriptions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    prescriptions = (
        db.query(models.Prescription)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return prescriptions


@router.get("/{prescription_id}", response_model=schemas.PrescriptionRead)
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
):
    prescription = (
        db.query(models.Prescription)
        .filter(models.Prescription.id == prescription_id)
        .first()
    )
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )
    return prescription


@router.patch("/{prescription_id}/status", response_model=schemas.PrescriptionRead)
def update_prescription_status(
    prescription_id: int,
    status_value: str,
    db: Session = Depends(get_db),
):
    prescription = (
        db.query(models.Prescription)
        .filter(models.Prescription.id == prescription_id)
        .first()
    )
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )

    prescription.status = status_value
    db.commit()
    db.refresh(prescription)
    return prescription
