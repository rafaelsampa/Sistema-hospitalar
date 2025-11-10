# app/clinical_rules.py
"""
Módulo de validação de regras clínicas e interações medicamentosas.
Este é um exemplo básico - em produção, integrar com base de dados especializada.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from . import models

# Base de dados simplificada de interações conhecidas
# Em produção, usar banco especializado como DrugBank, FDA, etc.
KNOWN_INTERACTIONS = {
    # Formato: (medication_id_1, medication_id_2): {"severity": "HIGH/MEDIUM/LOW", "description": "..."}
    # Exemplo: Warfarina + AAS
    # ("warfarin", "aspirin"): {
    #     "severity": "HIGH",
    #     "description": "Risco aumentado de sangramento"
    # }
}


class ClinicalValidator:
    """
    Validador de regras clínicas para prescrições.
    """
    
    @staticmethod
    def check_medication_interactions(
        medication_ids: List[int],
        db: Session
    ) -> List[Dict]:
        """
        Verifica interações medicamentosas entre os medicamentos prescritos.
        
        Args:
            medication_ids: Lista de IDs dos medicamentos a serem verificados
            db: Sessão do banco de dados
            
        Returns:
            Lista de interações encontradas (vazia se não houver)
        """
        interactions = []
        
        # Busca os medicamentos no banco
        medications = db.query(models.Medication).filter(
            models.Medication.id.in_(medication_ids)
        ).all()
        
        # Verifica interações par a par
        for i, med1 in enumerate(medications):
            for med2 in medications[i+1:]:
                # Verifica se existe interação conhecida
                interaction_key = tuple(sorted([med1.name.lower(), med2.name.lower()]))
                
                if interaction_key in KNOWN_INTERACTIONS:
                    interaction = KNOWN_INTERACTIONS[interaction_key]
                    interactions.append({
                        "medication_1": {
                            "id": med1.id,
                            "name": med1.name
                        },
                        "medication_2": {
                            "id": med2.id,
                            "name": med2.name
                        },
                        "severity": interaction["severity"],
                        "description": interaction["description"]
                    })
        
        return interactions
    
    @staticmethod
    def validate_prescription(
        medication_ids: List[int],
        patient_id: str,
        db: Session
    ) -> Dict:
        """
        Valida uma prescrição completa verificando interações e regras clínicas.
        
        Args:
            medication_ids: Lista de IDs dos medicamentos prescritos
            patient_id: ID do paciente
            db: Sessão do banco de dados
            
        Returns:
            Dicionário com resultado da validação
        """
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        # 1. Verifica se todos os medicamentos existem e estão ativos
        medications = db.query(models.Medication).filter(
            models.Medication.id.in_(medication_ids)
        ).all()
        
        if len(medications) != len(medication_ids):
            found_ids = {med.id for med in medications}
            missing_ids = set(medication_ids) - found_ids
            validation_result["is_valid"] = False
            validation_result["errors"].append({
                "type": "MEDICATION_NOT_FOUND",
                "message": f"Medicamentos não encontrados: {missing_ids}"
            })
            return validation_result
        
        # Verifica medicamentos inativos
        inactive_meds = [med for med in medications if not med.is_active]
        if inactive_meds:
            validation_result["warnings"].append({
                "type": "INACTIVE_MEDICATION",
                "message": f"Medicamentos inativos na prescrição: {[m.name for m in inactive_meds]}"
            })
        
        # 2. Verifica interações medicamentosas
        interactions = ClinicalValidator.check_medication_interactions(
            medication_ids, db
        )
        
        if interactions:
            for interaction in interactions:
                if interaction["severity"] == "HIGH":
                    validation_result["errors"].append({
                        "type": "HIGH_SEVERITY_INTERACTION",
                        "message": f"Interação de alta gravidade entre {interaction['medication_1']['name']} e {interaction['medication_2']['name']}: {interaction['description']}"
                    })
                    validation_result["is_valid"] = False
                elif interaction["severity"] == "MEDIUM":
                    validation_result["warnings"].append({
                        "type": "MEDIUM_SEVERITY_INTERACTION",
                        "message": f"Interação de média gravidade entre {interaction['medication_1']['name']} e {interaction['medication_2']['name']}: {interaction['description']}"
                    })
        
        # 3. TODO: Integrar com serviço de Pacientes & Prontuário
        # para verificar alergias do paciente
        # alergies = get_patient_allergies(patient_id)
        # for med in medications:
        #     if med.id in alergies:
        #         validation_result["is_valid"] = False
        #         validation_result["errors"].append({
        #             "type": "ALLERGY_ALERT",
        #             "message": f"Paciente possui alergia ao medicamento {med.name}"
        #         })
        
        return validation_result


# Função auxiliar para adicionar interações conhecidas
def add_known_interaction(
    med_name_1: str,
    med_name_2: str,
    severity: str,
    description: str
):
    """
    Adiciona uma interação medicamentosa conhecida à base de dados.
    """
    key = tuple(sorted([med_name_1.lower(), med_name_2.lower()]))
    KNOWN_INTERACTIONS[key] = {
        "severity": severity,
        "description": description
    }


# Exemplos de interações comuns (podem ser carregadas de arquivo/BD)
add_known_interaction(
    "warfarina", "ácido acetilsalicílico",
    "HIGH",
    "Risco aumentado de sangramento. Monitorar INR de perto."
)

add_known_interaction(
    "varfarina", "dipirona",
    "MEDIUM",
    "Possível potencialização do efeito anticoagulante."
)
