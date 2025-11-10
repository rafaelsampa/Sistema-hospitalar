# app/routers/prescriptions.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..kafka_producer import kafka_producer
from ..clinical_rules import ClinicalValidator

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
    # 1. VALIDAÇÃO: Verifica se todos os medicamentos existem
    medication_ids = [item.medication_id for item in prescription_in.items]
    
    for med_id in medication_ids:
        med = db.query(models.Medication).filter(
            models.Medication.id == med_id
        ).first()
        if not med:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medication with id {med_id} not found"
            )
    
    # 2. VALIDAÇÃO CLÍNICA: Verifica interações e regras clínicas
    validation_result = ClinicalValidator.validate_prescription(
        medication_ids=medication_ids,
        patient_id=prescription_in.patient_id,
        db=db
    )
    
    if not validation_result["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Prescription validation failed",
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"]
            }
        )
    
    # 3. Cria o cabeçalho da prescrição
    db_prescription = models.Prescription(
        patient_id=prescription_in.patient_id,
        prescriber_id=prescription_in.prescriber_id,
        status=prescription_in.status or "DRAFT",
        notes=prescription_in.notes,
    )
    db.add(db_prescription)
    db.flush()  # garante que db_prescription.id existe

    # 4. Cria os itens da prescrição
    items_db = []
    for item in prescription_in.items:
        db_item = models.PrescriptionItem(
            prescription_id=db_prescription.id,
            medication_id=item.medication_id,
            dose=item.dose,
            frequency=item.frequency,  # CORRIGIDO: era hardcoded "1234567"
            route=item.route,
            duration=item.duration,
            instructions=item.instructions,
        )
        db.add(db_item)
        items_db.append(db_item)

    db.commit()
    db.refresh(db_prescription)
    
    # 5. EVENTO KAFKA: Publica evento MedicationPrescribed
    kafka_producer.publish_medication_prescribed({
        'id': db_prescription.id,
        'patient_id': db_prescription.patient_id,
        'prescriber_id': db_prescription.prescriber_id,
        'status': db_prescription.status,
        'items': [
            {
                'medication_id': item.medication_id,
                'dose': item.dose,
                'frequency': item.frequency,
                'route': item.route
            }
            for item in db_prescription.items
        ]
    })
    
    # Log de avisos se houver
    if validation_result["warnings"]:
        print(f"[CLINICAL WARNINGS] Prescription {db_prescription.id}:")
        for warning in validation_result["warnings"]:
            print(f"  - {warning['type']}: {warning['message']}")

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