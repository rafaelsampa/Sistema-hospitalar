

import json
import uuid
from typing import Dict, Any
from datetime import datetime
# from confluent_kafka import Producer

class KafkaEventProducer:
    """
    
    Formato do Evento:
    {
        "eventId": "UUID único",
        "eventType": "Tipo do evento (MedicationPrescribed, MedicationDispensed)",
        "timestamp": "ISO 8601 timestamp",
        "source": "medication-service",
        "resourceType": "MedicationRequest | MedicationDispense",
        "data": { objeto com dados do recurso }
    }
    """
    
    TOPIC_MEDICATION_EVENTS = "medication.events"
    SOURCE_SERVICE = "medication-service"
    
    def __init__(self):
        # TODO: config kafka
        # self.producer = Producer({
        #     'bootstrap.servers': 'kafka:9092',
        #     'client.id': 'medication-service'
        # })
        self.producer = None
        print(f"[KAFKA] KafkaEventProducer iniciado em modo STUB")
        print(f"[KAFKA] Topic padrão: {self.TOPIC_MEDICATION_EVENTS}")
        print(f"[KAFKA] Source: {self.SOURCE_SERVICE}")
    
    def _create_standard_event(
        self, 
        event_type: str, 
        resource_type: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cria um evento no formato padrão de comunicação inter-microserviços.
        
        Args:
            event_type: Tipo do evento (MedicationPrescribed, MedicationDispensed)
            resource_type: Tipo do recurso FHIR (MedicationRequest, MedicationDispense)
            data: Dados do recurso
            
        Returns:
            Evento formatado segundo o padrão
        """
        return {
            "eventId": str(uuid.uuid4()),
            "eventType": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": self.SOURCE_SERVICE,
            "resourceType": resource_type,
            "data": data
        }
    
    def publish_event(self, topic: str, event: Dict[str, Any]):
        """
        Publica um evento no tópico Kafka especificado.
        
        Args:
            topic: Nome do tópico Kafka
            event: Evento já formatado no padrão
        """
        if self.producer is None:
            # Modo stub - apenas loga o evento
            print(f"\n{'='*80}")
            print(f"[KAFKA EVENT PUBLISHED]")
            print(f"Topic: {topic}")
            print(f"Event ID: {event.get('eventId')}")
            print(f"Event Type: {event.get('eventType')}")
            print(f"Timestamp: {event.get('timestamp')}")
            print(f"Source: {event.get('source')}")
            print(f"Resource Type: {event.get('resourceType')}")
            print(f"Data: {json.dumps(event.get('data'), indent=2)}")
            print(f"{'='*80}\n")
            return
        
        # TODO: implementação real do kafka
        # self.producer.produce(
        #     topic,
        #     key=event['eventId'],
        #     value=json.dumps(event),
        #     callback=self._delivery_callback
        # )
        # self.producer.flush()
       
    def _delivery_callback(self, err, msg):
        """Callback de confirmação de entrega"""
        if err:
            print(f"[KAFKA] Erro ao entregar mensagem: {err}")
        else:
            print(f"[KAFKA] Mensagem entregue ao tópico {msg.topic()}")
    
    def publish_medication_prescribed(self, prescription_data: Dict[str, Any]):
        """
        publica o enevto (prescrição criada).
        
        Args:
            prescription_data: Dados completos da prescrição
            
        Exemplo de prescription_data esperado:
        {
            "id": 1,
            "patient_id": "PAT123",
            "prescriber_id": "DOC456",
            "status": "active",
            "prescribed_at": "2025-01-15T10:30:00",
            "items": [
                {
                    "medication_id": 1,
                    "medication_name": "Paracetamol",
                    "dosage": "500mg",
                    "frequency": "8/8h",
                    "duration_days": 7
                }
            ]
        }
        """
        # mapeia os dados 
        data = {
            "id": prescription_data.get("id"),
            "patientId": prescription_data.get("patient_id"),
            "prescriberId": prescription_data.get("prescriber_id"),
            "medication": [
                {
                    "medicationId": item.get("medication_id"),
                    "medicationName": item.get("medication_name"),
                    "dosage": item.get("dosage"),
                    "frequency": item.get("frequency"),
                    "durationDays": item.get("duration_days")
                }
                for item in prescription_data.get("items", [])
            ],
            "status": prescription_data.get("status"),
            "prescribedAt": prescription_data.get("prescribed_at")
        }
        
        event = self._create_standard_event(
            event_type="MedicationPrescribed",
            resource_type="MedicationRequest",
            data=data
        )
        
        self.publish_event(self.TOPIC_MEDICATION_EVENTS, event)
    
    def publish_medication_dispensed(self, dispensation_data: Dict[str, Any]):
        """
        Publica evento MedicationDispensed (medicamento dispensado).
        
        Args:
            dispensation_data: Dados completos da dispensação
            
        Exemplo de dispensation_data esperado:
        {
            "id": 1,
            "prescription_id": 1,
            "dispensed_by": "PHA789",
            "dispensed_at": "2025-01-15T11:00:00",
            "status": "completed",
            "items": [
                {
                    "medication_id": 1,
                    "medication_name": "Paracetamol",
                    "quantity_dispensed": 14
                }
            ]
        }
        """
        # Mapeia dados da dispensação para o formato padrão
        data = {
            "id": dispensation_data.get("id"),
            "prescriptionId": dispensation_data.get("prescription_id"),
            "dispensedBy": dispensation_data.get("dispensed_by"),
            "dispensedAt": dispensation_data.get("dispensed_at"),
            "medication": [
                {
                    "medicationId": item.get("medication_id"),
                    "medicationName": item.get("medication_name"),
                    "quantityDispensed": item.get("quantity_dispensed")
                }
                for item in dispensation_data.get("items", [])
            ],
            "status": dispensation_data.get("status")
        }
        
        event = self._create_standard_event(
            event_type="MedicationDispensed",
            resource_type="MedicationDispense",
            data=data
        )
        
        self.publish_event(self.TOPIC_MEDICATION_EVENTS, event)

kafka_producer = KafkaEventProducer()
