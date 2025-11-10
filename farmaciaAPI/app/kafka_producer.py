# app/kafka_producer.py
"""
Producer Kafka para publicação de eventos do microserviço.
Este módulo será integrado com o Kafka fornecido por terceiros.
"""

import json
from typing import Dict, Any
from datetime import datetime

# NOTA: Quando o Kafka for fornecido, descomente e configure:
# from confluent_kafka import Producer

class KafkaEventProducer:
    """
    Producer de eventos para Kafka.
    Modo stub - vai ser conectado ao Kafka real
    """
    
    def __init__(self):
        # TODO: Configurar quando o Kafka for fornecido
        # self.producer = Producer({
        #     'bootstrap.servers': 'kafka:9092',
        #     'client.id': 'farmacia-service'
        # })
        self.producer = None
        print("[KAFKA] KafkaEventProducer iniciado em modo STUB (aguardando integração)")
    
    def publish_event(self, topic: str, event_data: Dict[str, Any]):
        """
        Publica um evento no tópico Kafka especificado.
        
        Args:
            topic: Nome do tópico Kafka
            event_data: Dados do evento a serem publicados
        """
        # Adiciona timestamp ao evento
        event_data['timestamp'] = datetime.utcnow().isoformat()
        
        if self.producer is None:
            # Modo stub - apenas loga o evento
            print(f"[KAFKA EVENT] Topic: {topic}")
            print(f"[KAFKA EVENT] Data: {json.dumps(event_data, indent=2)}")
            return
        
        # TODO: implementacao do kafka
       
    def _delivery_callback(self, err, msg):
        """Callback de confirmação de entrega"""
        if err:
            print(f"[KAFKA] Erro ao entregar mensagem: {err}")
        else:
            print(f"[KAFKA] Mensagem entregue ao tópico {msg.topic()}")
    
    def publish_medication_prescribed(self, prescription_data: Dict[str, Any]):
        """
        Publica evento MedicationPrescribed.
        
        Args:
            prescription_data: Dados da prescrição criada
        """
        event = {
            'event_type': 'MedicationPrescribed',
            'prescription_id': prescription_data.get('id'),
            'patient_id': prescription_data.get('patient_id'),
            'prescriber_id': prescription_data.get('prescriber_id'),
            'status': prescription_data.get('status'),
            'items_count': len(prescription_data.get('items', [])),
            'items': prescription_data.get('items', [])
        }
        self.publish_event('medication-prescribed', event)
    
    def publish_medication_dispensed(self, dispensation_data: Dict[str, Any]):
        """
        Publica evento MedicationDispensed.
        
        Args:
            dispensation_data: Dados da dispensação realizada
        """
        event = {
            'event_type': 'MedicationDispensed',
            'dispensation_id': dispensation_data.get('id'),
            'prescription_id': dispensation_data.get('prescription_id'),
            'dispensed_by': dispensation_data.get('dispensed_by'),
            'status': dispensation_data.get('status'),
            'items_count': len(dispensation_data.get('items', [])),
            'items': dispensation_data.get('items', [])
        }
        self.publish_event('medication-dispensed', event)


# Instância global do producer
kafka_producer = KafkaEventProducer()
