# app/routers/dispensations.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/dispensations",
    tags=["dispensations"],
)


@router.post(
    "/",
    response_model=schemas.DispensationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_dispensation(
    dispensation_in: schemas.DispensationCreate,
    db: Session = Depends(get_db),
):
    # Verifica se a prescrição existe
    prescription = (
        db.query(models.Prescription)
        .filter(models.Prescription.id == dispensation_in.prescription_id)
        .first()
    )
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found",
        )

    # Cria o cabeçalho da dispensação
    db_disp = models.Dispensation(
        prescription_id=dispensation_in.prescription_id,
        dispensed_by=dispensation_in.dispensed_by,
        status=dispensation_in.status or "COMPLETED",
        notes=dispensation_in.notes,
    )
    db.add(db_disp)
    db.flush()  # garante que db_disp.id existe

    # Cria os itens
    for item in dispensation_in.items:
        # valida se o medicamento existe
        med = (
            db.query(models.Medication)
            .filter(models.Medication.id == item.medication_id)
            .first()
        )
        if not med:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Medication {item.medication_id} not found",
            )

        # se prescription_item_id foi informado, podemos validar que ele pertence à mesma prescrição
        prescription_item_id = item.prescription_item_id
        if prescription_item_id is not None:
            pi = (
                db.query(models.PrescriptionItem)
                .filter(models.PrescriptionItem.id == prescription_item_id)
                .first()
            )
            if not pi or pi.prescription_id != dispensation_in.prescription_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"PrescriptionItem {prescription_item_id} does not belong to Prescription {dispensation_in.prescription_id}",
                )

        db_item = models.DispensationItem(
            dispensation_id=db_disp.id,
            prescription_item_id=prescription_item_id,
            medication_id=item.medication_id,
            quantity_dispensed=item.quantity_dispensed,
            notes=item.notes,
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_disp)

    # Aqui seria o ponto de publicar o evento MedicationDispensed
    print(
        f"[EVENT] MedicationDispensed -> dispensation_id={db_disp.id}, "
        f"prescription_id={db_disp.prescription_id}, items={len(db_disp.items)}"
    )

    return db_disp


@router.get("/", response_model=List[schemas.DispensationRead])
def list_dispensations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    disp = (
        db.query(models.Dispensation)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return disp


@router.get("/{dispensation_id}", response_model=schemas.DispensationRead)
def get_dispensation(
    dispensation_id: int,
    db: Session = Depends(get_db),
):
    disp = (
        db.query(models.Dispensation)
        .filter(models.Dispensation.id == dispensation_id)
        .first()
    )
    if not disp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispensation not found",
        )
    return disp


@router.patch("/{dispensation_id}/status", response_model=schemas.DispensationRead)
def update_dispensation_status(
    dispensation_id: int,
    status_value: str,
    db: Session = Depends(get_db),
):
    disp = (
        db.query(models.Dispensation)
        .filter(models.Dispensation.id == dispensation_id)
        .first()
    )
    if not disp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispensation not found",
        )

    disp.status = status_value
    db.commit()
    db.refresh(disp)
    return disp
