# Microserviço: Farmácia & Prescrição

## Visão Geral do Projeto

Este repositório contém o desenvolvimento do microserviço de **Farmácia & Prescrição**, componente do sistema de gestão hospitalar proposto para a disciplina de **Arquitetura de Sistemas**.

O objetivo deste serviço é gerenciar de forma autônoma e resiliente todo o ciclo de vida de medicamentos dentro do hospital, desde o seu cadastro no catálogo até a sua dispensação para o paciente, garantindo a integridade e a segurança dos dados clínicos.

## Responsabilidades do Serviço

O serviço foi projetado para cobrir quatro áreas de responsabilidade principais:

<details>
<summary><strong>1. Gerenciamento do Catálogo de Fármacos</strong></summary>

* Manter um repositório centralizado e atualizado de todos os medicamentos disponíveis.
* Prover operações de CRUD (Create, Read, Update, Delete) para os fármacos.
* Implementar um mecanismo de busca de alta performance, com funcionalidades de autocompletar e busca por princípio ativo, utilizando o **Elasticsearch**.

</details>

<details>
<summary><strong>2. Gestão de Prescrições Eletrônicas</strong></summary>

* Permitir que profissionais de saúde autorizados criem prescrições eletrônicas para pacientes.
* Armazenar de forma segura e estruturada os dados da prescrição, incluindo paciente, médico, medicamento, posologia e duração do tratamento.
* Garantir a integridade referencial e a consistência das prescrições no banco de dados transacional.

</details>

<details>
<summary><strong>3. Controle de Dispensação de Medicamentos</strong></summary>

* Registrar a entrega (dispensação) de um medicamento associado a uma prescrição válida.
* Manter o status da prescrição atualizado (ex: "Pendente", "Dispensada", "Cancelada").
* Gerar um histórico de dispensações para fins de auditoria e faturamento.

</details>

<details>
<summary><strong>4. Validação de Regras Clínicas e Interações</strong></summary>

* Implementar lógicas de negócio para auxiliar na segurança do paciente.
* Validar prescrições contra possíveis interações medicamentosas conhecidas.
* Integrar-se (via eventos ou API) com o serviço de **Pacientes & Prontuário** para verificar alergias antes de validar uma nova prescrição.

</details>


___________________________________________________

## Arquitetura e Stack de Tecnologias

A arquitetura deste microserviço segue os princípios de *Domain-Driven Design (DDD)* e *Event-Driven Architecture (EDA)*.



### Endpoints da API

O serviço expõe os seguintes recursos através de sua API:

  * `/medications`: Interação com o catálogo de fármacos.
  * `/prescriptions`: Criação e consulta de prescrições médicas.
  * `/dispensations`: Registro da dispensação de medicamentos.

### Eventos

Para comunicação assíncrona e desacoplada com outros microserviços, este serviço publica os seguintes eventos:

  * `MedicationPrescribed`: Emitido quando uma nova prescrição é criada com sucesso.
  * `MedicationDispensed`: Emitido quando um medicamento é entregue ao paciente.

___________________________________________________

## Deploy

Este projeto oferece duas opções de deploy:

### Deploy Local (Docker Compose)
**Ideal para:** Desenvolvimento, testes, projetos acadêmicos
- ✅ Gratuito
- ✅ Setup em 5 minutos
- ✅ Perfeito para demonstrações

```bash
chmod +x deploy.sh
./deploy.sh
```

📖 **[Guia completo de Deploy Local](DEPLOY.md#deploy-local)**

### Deploy AWS (Production)
**Ideal para:** Produção, alta disponibilidade, escalabilidade
- ✅ Infraestrutura completa (ECS, RDS, OpenSearch)
- ✅ Auto-scaling e monitoramento
- ✅ ~$ (Free Tier disponível)

```bash
# Configure AWS CLI
aws configure

# Execute deploy
chmod +x deploy-aws.sh
./deploy-aws.sh
```

 **[Guia completo AWS](AWS_QUICKSTART.md)** | **[Comparação Local vs AWS](DEPLOY_COMPARISON.md)**

###  Documentação de Deploy

- **[DEPLOY.md](DEPLOY.md)** - Guia completo com deploy local e AWS
- **[AWS_QUICKSTART.md](AWS_QUICKSTART.md)** - Quick start para AWS
- **[DEPLOY_COMPARISON.md](DEPLOY_COMPARISON.md)** - Comparação entre opções
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Integração com outros serviços
- **[RESUMO_IMPLEMENTACAO.md](RESUMO_IMPLEMENTACAO.md)** - Resumo da implementação

###  Arquivos de Deploy

- `docker-compose.yml` - Configuração Docker Compose (local)
- `farmaciaAPI/Dockerfile` - Imagem Docker da API
- `deploy.sh` - Script de deploy local
- `aws-deploy.yml` - CloudFormation template (AWS)
- `deploy-aws.sh` - Script de deploy AWS

___________________________________________________

## Desenvolvimento Local

### Pré-requisitos
- Python 3.11+
- PostgreSQL 16 (via Docker)
- Elasticsearch 8.13.4 (via Docker)

### Setup Rápido

```bash
# 1. Ativar ambiente virtual
./env/Scripts/Activate.ps1  # Windows PowerShell
# ou
source env/bin/activate     # Linux/Mac

# 2. Instalar dependências
cd farmaciaAPI
pip install -r requirements.txt

# 3. Iniciar serviços de infraestrutura
docker-compose up -d postgres elasticsearch

# 4. Iniciar API
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs

___________________________________________________

##  Arquitetura AWS

```
┌─────────────────────────────────────────────────────┐
│                    Internet                          │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  Application Load       │
        │  Balancer (ALB)         │
        └────────────┬────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐
│ ECS     │    │ ECS     │    │ ECS     │
│ Task 1  │    │ Task 2  │    │ Task N  │
└────┬────┘    └────┬────┘    └────┬────┘
     │              │              │
     └──────────────┼──────────────┘
                    │
     ┌──────────────┼──────────────┐
     │              │              │
┌────▼───────┐ ┌───▼────────┐ ┌───▼────┐
│ RDS        │ │ OpenSearch │ │ ECR    │
│ PostgreSQL │ │ (ES)       │ │ Images │
└────────────┘ └────────────┘ └────────┘
```

___________________________________________________

##  Testing

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=app

# Health check
curl http://localhost:8000/health
```

___________________________________________________

##  API Endpoints

### Medications (Catálogo)
- `POST /medications/` - Criar medicamento
- `GET /medications/` - Listar medicamentos
- `GET /medications/{id}` - Obter medicamento
- `PUT /medications/{id}` - Atualizar medicamento
- `DELETE /medications/{id}` - Deletar medicamento
- `GET /medications/search?q=` - Buscar medicamentos (Elasticsearch)

### Prescriptions (Prescrições)
- `POST /prescriptions/` - Criar prescrição
- `GET /prescriptions/` - Listar prescrições
- `GET /prescriptions/{id}` - Obter prescrição
- `PATCH /prescriptions/{id}/status` - Atualizar status

### Dispensations (Dispensação)
- `POST /dispensations/` - Criar dispensação
- `GET /dispensations/` - Listar dispensações
- `GET /dispensations/{id}` - Obter dispensação
- `PATCH /dispensations/{id}/status` - Atualizar status

**Documentação interativa:** http://localhost:8000/docs

___________________________________________________

##  Eventos Kafka

### Publicados

**MedicationPrescribed**
```json
{
  "event_type": "MedicationPrescribed",
  "prescription_id": 123,
  "patient_id": 456,
  "prescriber_id": 789,
  "medications": [
    {"medication_id": 1, "name": "Dipirona"}
  ],
  "timestamp": "2025-11-09T12:00:00Z"
}
```

**MedicationDispensed**
```json
{
  "event_type": "MedicationDispensed",
  "dispensation_id": 321,
  "prescription_id": 123,
  "medications": [
    {"medication_id": 1, "quantity": 30}
  ],
  "timestamp": "2025-11-09T13:00:00Z"
}
```

> **Nota:** Implementação atual em modo stub (logs). Para integração real com Kafka, descomentar código em `kafka_producer.py` e configurar `KAFKA_BOOTSTRAP_SERVERS`.

___________________________________________________

##  Segurança

### Variáveis de Ambiente Sensíveis

Nunca commite senhas! Use variáveis de ambiente:

```bash
# .env (não commitado)
DATABASE_URL=postgresql://user:pass@host:5432/db
ELASTIC_PASSWORD=senha_segura
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

### Boas Práticas Implementadas
- ✅ Conexões HTTPS com Elasticsearch
- ✅ Validação de entrada com Pydantic
- ✅ Clinical rules para validação de prescrições
- ✅ Security Groups configurados (AWS)
- ✅ Encryption at rest (RDS + OpenSearch)
- ✅ IAM Roles com least privilege (AWS)

___________________________________________________

##  Monitoramento

### Local (Docker)
```bash
# Logs da API
docker-compose logs -f api

# Métricas
docker stats
```

### AWS
```bash
# CloudWatch Logs
aws logs tail /ecs/farmacia-prescricao --follow

# Métricas no console
# https://console.aws.amazon.com/cloudwatch/
```

___________________________________________________

##  CI/CD

Para configurar deploy automático via GitHub Actions, veja exemplo em `DEPLOY.md`.

___________________________________________________

##  Licença

Este projeto foi desenvolvido para fins acadêmicos como parte da disciplina de **Arquitetura de Sistemas**.

___________________________________________________

##  Membros do Grupo

  * Matheus Veríssimo
  * Gabriel Martins
  * Rafael Angelim
  * Rafael Sampaio

___________________________________________________

