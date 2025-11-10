
import os
from elasticsearch import Elasticsearch, helpers

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "http://localhost:9200") 
ELASTIC_USER = os.getenv("ELASTIC_USER", "elastic")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "vl60PBF8o1qbViYLeAHe")
ELASTIC_VERIFY_CERTS = os.getenv("ELASTIC_VERIFY_CERTS", "false").lower() == "true"
INDEX_NAME = os.getenv("ELASTIC_INDEX", "farmacoteste")

def get_es_client():
    try:
        print(f"[ELASTIC] 🔍 Tentando conectar em {ELASTIC_HOST}...")
        print(f"[ELASTIC] 🔍 Usuário: {ELASTIC_USER}")
        
        # conexao com https + autenticação 
        es = Elasticsearch(
            [ELASTIC_HOST],
            basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
            verify_certs=False,  
            ssl_show_warn=False  
        )
        
        print(f"[ELASTIC]  Cliente criado: {es}")
        print(f"[ELASTIC]  Executando ping...")
        
        ping_result = es.ping()
        print(f"[ELASTIC]  Resultado do ping: {ping_result}")
        
        if ping_result:
            print("[ELASTIC] ✅ conectou com Elasticsearch ")
            return es
        else:
            print("[ELASTIC] ❌ Ping retornou False")
            # Tenta info() para ver se é problema do ping()
            try:
                info = es.info()
                print(f"[ELASTIC] ✅ AEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE! Cluster: {info['cluster_name']}")
                print("[ELASTIC] ⚠️  Ping falhou mas info() funcionou - usando conexão mesmo assim")
                return es
            except Exception as info_err:
                print(f"[ELASTIC] ❌ Info também falhou: {info_err}")
                raise ConnectionError("conectou nao essa coisa")
        
    except Exception as e:
        print(f"[ELASTIC] Erro ao conectar: {type(e).__name__}: {e}")
        print(f"[ELASTIC]  ta rodando?:{ELASTIC_HOST}")
        print(f"[ELASTIC] Teste: curl -k {ELASTIC_HOST} -u {ELASTIC_USER}:***")
        import traceback
        traceback.print_exc()
        return None

es = get_es_client()

# Garante que o índice existe (com mapeamento básico)
def ensure_index():
    if es is None:
        print("[ELASTIC] ⚠️  Não foi possível garantir o índice: conexão ausente.")
        return
    try:
        if not es.indices.exists(index=INDEX_NAME):
            print(f"[ELASTIC] 📝 Índice '{INDEX_NAME}' não existe. Criando...")
            mappings = {
                "properties": {
                    "nome": {"type": "text"},
                    "descricao": {"type": "text"},
                    "forma_dosagem": {"type": "text"},
                    "forca": {"type": "text"},
                    "rota": {"type": "text"},
                    "codigo_atc": {"type": "keyword"},
                    "ativo": {"type": "boolean"}
                }
            }
            es.indices.create(index=INDEX_NAME, mappings=mappings)
            print(f"[ELASTIC] ✅ Índice '{INDEX_NAME}' criado com sucesso.")
        else:
            print(f"[ELASTIC] ✅ Índice '{INDEX_NAME}' já existe e pronto para uso.")
    except Exception as e:
        print(f"[ELASTIC] ❌ Erro ao garantir/criar índice: {e}")

ensure_index()

# ID do Postgres como ID do Elastic para manter a sincronia
def index_medication(medication_model: dict, medication_id: int):
    if es is None:
        print("⚠️  WARN: Conexão com ES não disponível. Ignorando indexação.")
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
            id=medication_id,
            document=document
        )
        print(f"[ELASTIC] ✅ Medicamento #{medication_id} indexado/atualizado.")
    except Exception as e:
        print(f"[ELASTIC] ❌ Erro ao indexar medicamento {medication_id}: {e}")

def remove_medication_from_index(medication_id: int):
    if es is None:
        print("⚠️  WARN: Conexão com ES não disponível. Ignorando remoção do índice.")
        return
    try:
        es.delete(index=INDEX_NAME, id=medication_id)
        print(f"[ELASTIC] ✅ Medicamento #{medication_id} removido do índice.")
    except Exception as e:
        print(f"[ELASTIC] ❌ Erro ao remover medicamento {medication_id} do ES: {e}")