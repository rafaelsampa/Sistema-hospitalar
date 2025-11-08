from elasticsearch import Elasticsearch
from elasticsearch import helpers

ELASTIC_PASSWORD = '<sua senha>'
CERT_FINGERPRINT = '<seu certificadot>'

### CONECTAR COM ELASTIC ###
es = Elasticsearch(
        ['https://localhost:9200/'],
        basic_auth=('elastic', ELASTIC_PASSWORD),
        ssl_assert_fingerprint=CERT_FINGERPRINT, 
        verify_certs=True  
    )

if es.ping():
    print("Connected to secured Elasticsearch.")
else:
    print("Failed to connect to secured Elasticsearch.")


index_name = "farmacoteste"

### VERIFICAR SE INDEX EXISTE ###
if es.indices.exists(index=index_name):
    print(f"Index '{index_name}' exists.")
else:
    print(f"Index '{index_name}' does not exist.")

### CRIAR INDEX ### 
#mappings = {
#        "properties": {
#            "nome": {"type": "text"},
#            "quantidade": {"type": "integer"}
#        }
#    }
#try:
#    response = es.indices.create(index=index_name, mappings=mappings)
#    print(f"Index '{index_name}' created successfully: {response}")
#except Exception as e:
#       print(f"Error creating index '{index_name}': {e}") 


### INSERIR ### 
#document = {
 #   "nome": "Tylenol",
#    "quantidade": "10"
#}

#try:
#    response = es.index(index=index_name, document=document)
 #   print(f"Document indexed successfully. {response}")
#except Exception as e:
#    print(f"Error indexing document: {e}")


### ATUALIZAR ###
#es.update(
#    index=index_name,
#    id='RRy7X5oB8xepPfAaZ9Tl',
#    body={
#        "doc": {
#            "quantidade": "1311",
#       }
#    }
#)

### printar todos ###
def mostrarTodos():
    query = {
    "query": { ### query pode ser substituido com um body que include o query e um filtro pra pegar apenas especificos
        "match_all": {}
    }
    }

    contador = 1
    print("-" * 30)
    try:
        for doc in helpers.scan(es, query=query, index=index_name):
            print(contador,":")
            print(f"ID: {doc['_id']}")
            print(doc['_source']['nome'])
            print(doc['_source']['quantidade'])
            print("-" * 30)
            contador += 1

    except Exception as e:
        print(f"An error occurred: {e}")
    return

mostrarTodos()
