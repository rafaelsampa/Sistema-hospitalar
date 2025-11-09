# /Sistema-hospitalar/application.py (CORRIGIDO v2)
import os
import json
import time
import random
import threading
from flask import Flask, jsonify, request
from kafka import KafkaProducer, KafkaConsumer
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, UUID
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid

# --- Configuração ---
application = Flask(__name__)
DB_URL = os.getenv("DATABASE_URL")
BROKER_URL = os.getenv("BROKER_URL") 
ELASTIC_URL = os.getenv("ELASTIC_URL")
KAFKA_TOPIC = "medication.events" 

# --- CONFIGURAÇÃO DO BANCO ---
engine = create_engine(DB_URL)
SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))
Base = declarative_base()

# --- Kafka Producer ---
try:
    producer = KafkaProducer(
        bootstrap_servers=BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("✅ Conectado ao Kafka Producer")
except Exception as e:
    print(f"❌ Erro ao conectar ao Kafka Producer: {e}")
    producer = None

def generate_event_id():
    return f"evt-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"

# --- DEFINIÇÃO DAS TABELAS (Modelos) ---
class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_comercial = Column(String(255), nullable=False)
    principio_ativo = Column(String(255), nullable=False)
    prescriptions = relationship("Prescription", back_populates="medication")

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(String(100), nullable=False)
    prescriber_id = Column(String(100), nullable=False)
    
    medication_id = Column(Integer, ForeignKey("medications.id"))
    medication = relationship("Medication", back_populates="prescriptions")
    
    # *** A CORREÇÃO ESTÁ AQUI ***
    # Este campo estava faltando no modelo
    medication_name_free = Column(String(255), nullable=False) 
    
    dosage = Column(String(255))
    frequency = Column(String(255))
    duration = Column(String(255))
    status = Column(String(50), default="active")
    prescribed_at = Column(String(100))

def init_db():
    print("Inicializando banco de dados PostgreSQL...")
    retries = 10
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Tabelas criadas com sucesso.")
            return
        except Exception as e:
            print(f"❌ Erro ao inicializar o banco: {e}. Tentando novamente em 3s...")
            retries -= 1
            time.sleep(3)
    print("❌ Falha ao inicializar o banco de dados após várias tentativas.")

# --- Kafka Consumer (Ouvinte) ---
def consume_events():
    print("Iniciando 'ouvinte' (consumer) do Kafka...")
    while True:
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=BROKER_URL,
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            print(f"✅ 'Ouvinte' conectado ao tópico '{KAFKA_TOPIC}'")
            for message in consumer:
                print("\n--- 📩 EVENTO RECEBIDO (Kafka Consumer) ---")
                print(json.dumps(message.value, indent=2))
                print("-----------------------------------------\n")
        except Exception as e:
            print(f"❌ Erro no 'ouvinte' Kafka: {e}. Tentando reconectar em 5s...")
            time.sleep(5)

# --- Endpoints da API ---
@application.route("/health")
def health():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected"
        
    return jsonify({
        "ok": True,
        "broker_status": "connected" if producer else "disconnected",
        "db_status": db_status
    }), 200

@application.route("/medications", methods=["GET", "POST"])
def medications_handler():
    return jsonify({"message": "TODO: /medications"}), 501

@application.route("/prescriptions", methods=["POST"])
def prescriptions_handler():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Corpo da requisição vazio"}), 400

    db = SessionLocal()
    try:
        # Este código agora vai funcionar
        new_prescription = Prescription(
            patient_id=data.get("patientId", "P-TESTE"),
            prescriber_id=data.get("prescriberId", "DR-TESTE"),
            medication_name_free=data.get("medication", "Paracetamol 500mg"),
            dosage=data.get("dosage", "1 comprimido"),
            frequency=data.get("frequency", "a cada 8 horas"),
            duration=data.get("duration", "5 dias"),
            status="active",
            prescribed_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        db.add(new_prescription)
        db.commit()
        db.refresh(new_prescription)
        prescription_id = str(new_prescription.id)
    except Exception as e:
        db.rollback()
        # Este é o erro que você está vendo
        return jsonify({"error": f"Erro de banco de dados: {str(e)}"}), 500
    finally:
        db.close()

    # --- Publicando no Kafka ---
    event_data = {
        "id": prescription_id,
        "patientId": new_prescription.patient_id,
        "prescriberId": new_prescription.prescriber_id,
        "medication": new_prescription.medication_name_free,
        "dosage": new_prescription.dosage,
        "frequency": new_prescription.frequency,
        "duration": new_prescription.duration,
        "status": new_prescription.status,
        "prescribedAt": new_prescription.prescribed_at
    }
    event_payload = {
        "eventId": generate_event_id(),
        "eventType": "MedicationPrescribed", 
        "timestamp": new_prescription.prescribed_at,
        "source": "medication-service", 
        "resourceType": "MedicationRequest", 
        "data": event_data
    }
    try:
        if producer:
            producer.send(KAFKA_TOPIC, value=event_payload)
            producer.flush() 
        else:
            return jsonify({"error": "Kafka producer não está disponível"}), 500
        return jsonify({"status": "prescrição criada", "id": prescription_id, "event_published": True}), 201
    except Exception as e:
        return jsonify({"error": f"Erro no Kafka: {str(e)}"}), 500

@application.route("/dispensations", methods=["POST"])
def dispensations_handler():
    return jsonify({"message": "TODO: /dispensations"}), 501

# --- Inicialização Global ---
init_db() 
consumer_thread = threading.Thread(target=consume_events, daemon=True)
consumer_thread.start()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=8000, debug=False)