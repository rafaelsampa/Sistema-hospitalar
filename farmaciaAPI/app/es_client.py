# farmaciaAPI/app/es_client.py
# NOVO ARQUIVO: Lógica de conexão do teste.py

from elasticsearch import Elasticsearch, helpers

# Dados de conexão extraídos do teste.py
ELASTIC_PASSWORD = 'vl60PBF8o1qbViYLeAHe'
CERT_FINGERPRINT = 'b068992808ddea6d4b1c084bcff5142eb52565cf393084b5519bec14b07c66bc'
INDEX_NAME = "farmacoteste" #

# Instância principal do cliente Elasticsearch
try:
    es = Elasticsearch(
            ['https://localhost:9200/'],
            basic_auth=('elastic', ELASTIC_PASSWORD),
            ssl_assert_fingerprint=CERT_FINGERPRINT, 
            verify_certs=True  
        )
    if not es.ping():
        raise ConnectionError("Falha ao conectar com o Elasticsearch.")
    print("Conectado ao Elasticsearch com sucesso.")

    # Verifica se o índice existe, como no teste.py
    if not es.indices.exists(index=INDEX_NAME):
        print(f"Índice '{INDEX_NAME}' não existe. Criando...")
        # Você pode definir mappings aqui se precisar
        es.indices.create(index=INDEX_NAME)
    else:
        print(f"Índice '{INDEX_NAME}' já existe.")

except Exception as e:
    print(f"Erro ao inicializar conexão com Elasticsearch: {e}")
    es = None # Define como None se a conexão falhar

# Função auxiliar para re-indexar um medicamento
# Usaremos o ID do Postgres como ID do Elastic para manter a sincronia
def index_medication(medication_model: dict, medication_id: int):
    if es is None:
        print("WARN: Conexão com ES não disponível. Ignorando indexação.")
        return

    document = {
        "nome": medication_model.get("name"),
        "descricao": medication_model.get("description"),
        "forma_dosagem": medication_model.get("dosage_form"),
        "forca": medication_model.get("strength"),
        "rota": medication_model.get("route"),
        "codigo_atc": medication_model.get("atc_code"),
        "ativo": medication_model.get("is_active")
    }
    
    try:
        es.index(
            index=INDEX_NAME, 
            id=medication_id, # Usando o ID do Postgres no Elastic
            document=document
        )
    except Exception as e:
        print(f"Erro ao indexar medicamento {medication_id} no ES: {e}")

def remove_medication_from_index(medication_id: int):
    if es is None:
        print("WARN: Conexão com ES não disponível. Ignorando remoção do índice.")
        return
    try:
        es.delete(index=INDEX_NAME, id=medication_id)
    except Exception as e:
        print(f"Erro ao remover medicamento {medication_id} do ES: {e}")