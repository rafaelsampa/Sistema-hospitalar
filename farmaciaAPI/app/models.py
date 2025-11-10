# app/models.py
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .database import Base


# --------- MEDICATION ---------
class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    dosage_form = Column(String(100), nullable=True)  # comprimido, solução, etc.
    strength = Column(String(100), nullable=True)     # 500 mg, 5 mg/mL etc.
    route = Column(String(50), nullable=True)         # VO, IV, IM, etc.
    atc_code = Column(String(50), nullable=True)      
    is_active = Column(Boolean, nullable=False, default=True)

    # relacionamento com itens de prescrição
    prescription_items = relationship(
        "PrescriptionItem",
        back_populates="medication",
    )

    # relacionamento com itens de dispensação
    dispensation_items = relationship(
        "DispensationItem",
        back_populates="medication",
    )


# --------- PRESCRIPTION (cabeçalho) ---------
class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(String(100), nullable=False)
    prescriber_id = Column(String(100), nullable=False)  # médico
    status = Column(String(50), nullable=False, default="DRAFT")  #cancelado, finalizado
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # itens associados
    items = relationship(
        "PrescriptionItem",
        back_populates="prescription",
        cascade="all, delete-orphan",
    )

    # dispensações associadas
    dispensations = relationship(
        "Dispensation",
        back_populates="prescription",
        cascade="all, delete-orphan",
    )


# --------- PRESCRIPTION ITEM (linhas da receita) ---------
class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, index=True)

    prescription_id = Column(
        Integer,
        ForeignKey("prescriptions.id", ondelete="CASCADE"),
        nullable=False,
    )
    medication_id = Column(
        Integer,
        ForeignKey("medications.id"),
        nullable=False,
    )

    dose = Column(String(100), nullable=False)       # "500 mg", "1 comprimido"
    frequency = Column(String(100), nullable=False)  # "8/8h", "12/12h"
    route = Column(String(50), nullable=True)        # VO, IV, IM
    duration = Column(String(100), nullable=True)    # "5 dias", "10 dias"
    instructions = Column(Text, nullable=True)       # "Tomar após as refeições"

    prescription = relationship("Prescription", back_populates="items")
    medication = relationship("Medication", back_populates="prescription_items")


# --------- DISPENSATION (cabeçalho) ---------
class Dispensation(Base):
    __tablename__ = "dispensations"

    id = Column(Integer, primary_key=True, index=True)

    prescription_id = Column(
        Integer,
        ForeignKey("prescriptions.id"),
        nullable=False,
    )
    dispensed_by = Column(String(100), nullable=False)  # id do profissional que dispensou
    status = Column(String(50), nullable=False, default="PENDING")  
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    prescription = relationship("Prescription", back_populates="dispensations")

    items = relationship(
        "DispensationItem",
        back_populates="dispensation",
        cascade="all, delete-orphan",
    )


# --------- DISPENSATION ITEM (linhas da dispensação) ---------
class DispensationItem(Base):
    __tablename__ = "dispensation_items"

    id = Column(Integer, primary_key=True, index=True)

    dispensation_id = Column(
        Integer,
        ForeignKey("dispensations.id", ondelete="CASCADE"),
        nullable=False,
    )

    prescription_item_id = Column(
        Integer,
        ForeignKey("prescription_items.id"),
        nullable=True,
    )

    medication_id = Column(
        Integer,
        ForeignKey("medications.id"),
        nullable=False,
    )

    quantity_dispensed = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)

    dispensation = relationship("Dispensation", back_populates="items")
    prescription_item = relationship("PrescriptionItem")
    medication = relationship("Medication", back_populates="dispensation_items")
