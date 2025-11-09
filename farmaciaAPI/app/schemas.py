# app/schemas.py
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# --------- MEDICATIONS ---------
class MedicationBase(BaseModel):
    name: str
    description: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    route: Optional[str] = None
    atc_code: Optional[str] = None
    is_active: bool = True


class MedicationCreate(MedicationBase):
    pass


class MedicationRead(MedicationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --------- PRESCRIPTIONS ---------
class PrescriptionItemCreate(BaseModel):
    medication_id: int
    dose: str
    frequency: str
    route: Optional[str] = None
    duration: Optional[str] = None
    instructions: Optional[str] = None


class PrescriptionItemRead(PrescriptionItemCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PrescriptionCreate(BaseModel):
    patient_id: str
    prescriber_id: str
    status: Optional[str] = "DRAFT"
    notes: Optional[str] = None
    items: List[PrescriptionItemCreate]


class PrescriptionRead(BaseModel):
    id: int
    patient_id: str
    prescriber_id: str
    status: str
    notes: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    items: List[PrescriptionItemRead] = []

    model_config = ConfigDict(from_attributes=True)


# --------- DISPENSATIONS ---------
class DispensationItemCreate(BaseModel):
    prescription_item_id: Optional[int] = None
    medication_id: int
    quantity_dispensed: int
    notes: Optional[str] = None


class DispensationItemRead(DispensationItemCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DispensationCreate(BaseModel):
    prescription_id: int
    dispensed_by: str
    status: Optional[str] = "COMPLETED"
    notes: Optional[str] = None
    items: List[DispensationItemCreate]


class DispensationRead(BaseModel):
    id: int
    prescription_id: int
    dispensed_by: str
    status: str
    notes: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    items: List[DispensationItemRead] = []

    model_config = ConfigDict(from_attributes=True)
