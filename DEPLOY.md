# 🚀 Guia de Deploy - Microserviço Farmácia & Prescrição

## 📋 Escolha seu ambiente de deploy

- **[Deploy Local com Docker Compose](#deploy-local)** - Para desenvolvimento e testes locais
- **[Deploy na AWS](#deploy-aws)** - Para produção com ECS, RDS e OpenSearch

---

# 🏠 Deploy Local

## Pré-requisitos

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Portas disponíveis:** 5432, 8000, 9200, 9300

---

## 🏗️ Arquitetura do Deploy

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ PostgreSQL   │  │ Elasticsearch│  │   FastAPI    │  │
│  │   :5432      │  │   :9200      │  │    :8000     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │          │
│    ┌────┴──────────────────┴──────────────────┴────┐   │
│    │         Volumes (persistência)                 │   │
│    │  • postgres_data                               │   │
│    │  • elasticsearch_data                          │   │
│    │  • elasticsearch_certs                         │   │
│    └────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Deploy Rápido

### Opção 1: Script automatizado (Linux/Mac)

```bash
# Dar permissão de execução
chmod +x deploy.sh

# Executar deploy
./deploy.sh
```

### Opção 2: Manual (Windows/Linux/Mac)

```bash
# 1. Build das imagens
docker-compose build

# 2. Iniciar todos os serviços
docker-compose up -d

# 3. Verificar status
docker-compose ps

# 4. Ver logs
docker-compose logs -f api
```

---

## ✅ Verificação do Deploy

### 1. Health Check da API
```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "database": "ok",
  "elasticsearch": "ok"
}
```

### 2. Acessar Documentação
Abra no navegador: http://localhost:8000/docs

### 3. Testar Endpoint
```bash
# Criar um medicamento
curl -X POST http://localhost:8000/medications/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dipirona",
    "description": "Analgésico e antipirético",
    "dosage_form": "Comprimido",
    "strength": "500mg",
    "route": "VO",
    "atc_code": "N02BB02",
    "is_active": true
  }'
```

---

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

Edite `docker-compose.yml` para ajustar:

```yaml
environment:
  # Database
  DATABASE_URL: postgresql+psycopg2://user:pass@host:5432/db
  
  # Elasticsearch
  ELASTIC_HOST: https://elasticsearch:9200
  ELASTIC_USER: elastic
  ELASTIC_PASSWORD: sua_senha_aqui
  
  # Kafka (quando fornecido)
  KAFKA_BOOTSTRAP_SERVERS: kafka:9092
```

### Escalabilidade

Para aumentar o número de workers da API:

```yaml
api:
  environment:
    WORKERS: 8  # Ajuste conforme necessário
```

---

## 🐛 Troubleshooting

### API não conecta ao Elasticsearch

```bash
# Ver logs do Elasticsearch
docker-compose logs elasticsearch

# Verificar se está rodando
docker-compose exec elasticsearch curl -k -u elastic:senha https://localhost:9200
```

### API não conecta ao PostgreSQL

```bash
# Ver logs do PostgreSQL
docker-compose logs postgres

# Verificar se está rodando
docker-compose exec postgres pg_isready -U farmacia_user
```

### API não inicializa

```bash
# Ver logs detalhados
docker-compose logs api

# Reiniciar apenas a API
docker-compose restart api
```

---

## 📦 Comandos Úteis

```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f api

# Reiniciar serviços
docker-compose restart

# Parar serviços
docker-compose stop

# Parar e remover containers
docker-compose down

# Parar, remover containers E volumes (CUIDADO: apaga dados!)
docker-compose down -v

# Entrar no container da API
docker-compose exec api bash

# Executar comando no PostgreSQL
docker-compose exec postgres psql -U farmacia_user -d farmacia_prescricao

# Ver status dos containers
docker-compose ps

# Ver uso de recursos
docker stats
```

---

## 🔐 Segurança em Produção

### ⚠️ IMPORTANTE: Antes de deploy em produção

1. **Alterar senhas padrão** em `docker-compose.yml`:
   - `POSTGRES_PASSWORD`
   - `ELASTIC_PASSWORD`

2. **Usar variáveis de ambiente** ao invés de hardcoded:
   ```bash
   # Criar arquivo .env
   cat > .env << EOF
   POSTGRES_PASSWORD=senha_segura_aqui
   ELASTIC_PASSWORD=outra_senha_segura
   EOF
   
   # Referenciar no docker-compose.yml
   environment:
     POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
   ```

3. **Habilitar SSL/TLS** para Elasticsearch em produção

4. **Configurar firewall** para limitar acesso às portas

5. **Usar volumes externos** para backup:
   ```yaml
   volumes:
     postgres_data:
       external: true
       name: farmacia_postgres_prod
   ```

---

## 🔄 Atualizações

### Atualizar código da API

```bash
# 1. Pull do código atualizado
git pull origin main

# 2. Rebuild da imagem
docker-compose build api

# 3. Reiniciar apenas a API (zero downtime com múltiplos workers)
docker-compose up -d api
```

### Backup do Banco de Dados

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U farmacia_user farmacia_prescricao > backup.sql

# Restore PostgreSQL
docker-compose exec -T postgres psql -U farmacia_user farmacia_prescricao < backup.sql
```

### Backup do Elasticsearch

```bash
# Criar snapshot (configurar repositório antes)
curl -X PUT "http://localhost:9200/_snapshot/my_backup/snapshot_1?wait_for_completion=true"
```

---

## 🎯 Próximos Passos

### Integração com Kafka

Quando o Kafka for fornecido por terceiros:

1. **Descomentar** seção Kafka no `docker-compose.yml`
2. **Atualizar** `KAFKA_BOOTSTRAP_SERVERS` com o endereço real
3. **Editar** `farmaciaAPI/app/kafka_producer.py`:
   - Descomentar import do Producer
   - Descomentar código de produção real
   - Remover modo stub

4. **Reiniciar API**:
   ```bash
   docker-compose restart api
   ```

---

## 📊 Monitoramento

### Logs estruturados

```bash
# Logs com filtro
docker-compose logs api | grep ERROR
docker-compose logs api | grep ELASTIC
docker-compose logs api | grep KAFKA
```

### Métricas de performance

```bash
# Ver uso de CPU/RAM
docker stats farmacia-api farmacia-postgres farmacia-elasticsearch
```

---

## 📞 Suporte

- **Logs da API**: `docker-compose logs api`
- **Status dos serviços**: `docker-compose ps`
- **Health check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

---

## 📝 Checklist de Deploy

- [ ] Docker e Docker Compose instalados
- [ ] Portas 5432, 8000, 9200 disponíveis
- [ ] Senhas alteradas no docker-compose.yml
- [ ] Build das imagens concluído
- [ ] Serviços iniciados com `docker-compose up -d`
- [ ] Health check retorna `status: "ok"`
- [ ] API Docs acessível em /docs
- [ ] Teste de criação de medicamento bem-sucedido
- [ ] Logs não mostram erros críticos
- [ ] Backup configurado (produção)
- [ ] Monitoramento configurado (produção)

---

**Status**: ✅ Pronto para deploy  
**Versão**: 1.0.0  
**Data**: Novembro 2025

---

# ☁️ Deploy AWS

## 🏗️ Arquitetura AWS

```
┌─────────────────────────────────────────────────────────────────┐
│                          Internet                                │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Application Load       │
                    │  Balancer (ALB)         │
                    │  Port 80/443            │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
    ┌────▼────┐            ┌────▼────┐            ┌────▼────┐
    │ ECS     │            │ ECS     │            │ ECS     │
    │ Task 1  │            │ Task 2  │            │ Task N  │
    │ (API)   │            │ (API)   │            │ (API)   │
    └────┬────┘            └────┬────┘            └────┬────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
    ┌────▼────────┐      ┌──────▼───────┐      ┌──────▼───────┐
    │ RDS         │      │ OpenSearch   │      │ ECR          │
    │ PostgreSQL  │      │ (Elasticsearch)│    │ (Docker      │
    │ :5432       │      │ :443         │      │  Registry)   │
    └─────────────┘      └──────────────┘      └──────────────┘
```

## 📦 Recursos AWS Provisionados

- **VPC** com subnets públicas e privadas em 2 AZs
- **RDS PostgreSQL 16** (db.t3.micro, 20GB)
- **OpenSearch 2.11** (t3.small.search, 10GB)
- **ECS Fargate** (2 tasks, 512 CPU, 1GB RAM cada)
- **Application Load Balancer** com health checks
- **ECR** para armazenamento de imagens Docker
- **CloudWatch Logs** para logs da aplicação
- **Security Groups** configurados para comunicação segura

## 🚀 Deploy Automático

### Pré-requisitos AWS

1. **AWS CLI** instalado e configurado:
```bash
# Instalar AWS CLI
# Windows: https://aws.amazon.com/cli/
# Linux: sudo apt install awscli
# Mac: brew install awscli

# Configurar credenciais
aws configure
# AWS Access Key ID: [sua key]
# AWS Secret Access Key: [seu secret]
# Default region: us-east-1
# Default output format: json
```

2. **Permissões IAM** necessárias:
   - CloudFormation (criar/atualizar/deletar stacks)
   - ECS (criar clusters, services, tasks)
   - ECR (criar repositórios, push de imagens)
   - RDS (criar instâncias)
   - OpenSearch (criar domains)
   - EC2 (criar VPCs, Security Groups, Load Balancers)
   - IAM (criar roles para ECS)
   - CloudWatch Logs

### Script de Deploy

```bash
# 1. Dar permissão de execução
chmod +x deploy-aws.sh

# 2. Executar deploy
./deploy-aws.sh
```

O script irá:
1. ✅ Verificar pré-requisitos (AWS CLI, Docker, credenciais)
2. ✅ Solicitar senhas para PostgreSQL e OpenSearch
3. ✅ Criar toda infraestrutura via CloudFormation (~15-20 min)
4. ✅ Construir imagem Docker da API
5. ✅ Fazer push da imagem para ECR
6. ✅ Atualizar serviço ECS com nova imagem
7. ✅ Aguardar deploy estabilizar
8. ✅ Verificar health check da API

### Deploy Manual (Passo a Passo)

```bash
# 1. Definir variáveis
export AWS_REGION="us-east-1"
export STACK_NAME="farmacia-prescricao"
export DB_PASSWORD="SenhaSuperSegura123!"
export OPENSEARCH_PASSWORD="OutraSenhaSegura456!"

# 2. Criar infraestrutura
aws cloudformation deploy \
  --template-file aws-deploy.yml \
  --stack-name $STACK_NAME \
  --region $AWS_REGION \
  --parameter-overrides \
    Environment=production \
    DBPassword=$DB_PASSWORD \
    OpenSearchPassword=$OPENSEARCH_PASSWORD \
  --capabilities CAPABILITY_IAM

# 3. Obter URI do ECR
ECR_URI=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $AWS_REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryUri`].OutputValue' \
  --output text)

# 4. Construir imagem
cd farmaciaAPI
docker build -t farmacia-api:latest .

# 5. Login no ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_URI

# 6. Tag e Push
docker tag farmacia-api:latest $ECR_URI:latest
docker push $ECR_URI:latest

# 7. Obter nome do cluster
ECS_CLUSTER=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $AWS_REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' \
  --output text)

# 8. Atualizar serviço
aws ecs update-service \
  --cluster $ECS_CLUSTER \
  --service $STACK_NAME-service \
  --force-new-deployment \
  --region $AWS_REGION

# 9. Aguardar estabilização
aws ecs wait services-stable \
  --cluster $ECS_CLUSTER \
  --services $STACK_NAME-service \
  --region $AWS_REGION
```

## ✅ Verificação do Deploy AWS

### 1. Obter URL do Load Balancer
```bash
aws cloudformation describe-stacks \
  --stack-name farmacia-prescricao \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
  --output text
```

### 2. Health Check
```bash
# Substituir <ALB_URL> pela URL obtida acima
curl http://<ALB_URL>/health

# Resposta esperada:
# {"status":"ok","database":"ok","elasticsearch":"ok"}
```

### 3. Acessar Documentação
```bash
# Abrir no navegador
http://<ALB_URL>/docs
```

### 4. Ver Logs da API
```bash
aws logs tail /ecs/farmacia-prescricao --follow --region us-east-1
```

### 5. Ver Status dos Containers
```bash
aws ecs describe-services \
  --cluster farmacia-prescricao-cluster \
  --services farmacia-prescricao-service \
  --region us-east-1
```

## 🔧 Configurações Avançadas AWS

### Alterar Número de Tasks (Escalabilidade)

Edite `aws-deploy.yml`:
```yaml
Parameters:
  DesiredCount:
    Type: Number
    Default: 4  # Altere de 2 para 4
```

Depois faça redeploy:
```bash
./deploy-aws.sh
```

### Alterar Tamanho dos Recursos

No `aws-deploy.yml`:

```yaml
# Para RDS (mais performance)
DBInstanceClass: db.t3.small  # ou db.t3.medium

# Para OpenSearch (mais capacidade)
InstanceType: t3.medium.search

# Para ECS Tasks (mais CPU/RAM)
Parameters:
  ContainerCpu: 1024    # ao invés de 512
  ContainerMemory: 2048 # ao invés de 1024
```

### Habilitar HTTPS (SSL/TLS)

1. **Obter certificado** no AWS Certificate Manager:
```bash
aws acm request-certificate \
  --domain-name api.seudominio.com \
  --validation-method DNS \
  --region us-east-1
```

2. **Adicionar listener HTTPS** no `aws-deploy.yml`:
```yaml
ALBListenerHTTPS:
  Type: AWS::ElasticLoadBalancingV2::Listener
  Properties:
    LoadBalancerArn: !Ref ApplicationLoadBalancer
    Port: 443
    Protocol: HTTPS
    Certificates:
      - CertificateArn: arn:aws:acm:us-east-1:123456:certificate/abc123
    DefaultActions:
      - Type: forward
        TargetGroupArn: !Ref TargetGroup
```

### Configurar Auto Scaling

Adicione ao `aws-deploy.yml`:

```yaml
AutoScalingTarget:
  Type: AWS::ApplicationAutoScaling::ScalableTarget
  Properties:
    MaxCapacity: 10
    MinCapacity: 2
    ResourceId: !Sub service/${ECSCluster}/${ECSService.Name}
    RoleARN: !GetAtt AutoScalingRole.Arn
    ScalableDimension: ecs:service:DesiredCount
    ServiceNamespace: ecs

AutoScalingPolicy:
  Type: AWS::ApplicationAutoScaling::ScalingPolicy
  Properties:
    PolicyName: cpu-auto-scaling
    PolicyType: TargetTrackingScaling
    ScalingTargetId: !Ref AutoScalingTarget
    TargetTrackingScalingPolicyConfiguration:
      PredefinedMetricSpecification:
        PredefinedMetricType: ECSServiceAverageCPUUtilization
      TargetValue: 70.0
```

## 🐛 Troubleshooting AWS

### Stack CloudFormation falha

```bash
# Ver eventos do stack
aws cloudformation describe-stack-events \
  --stack-name farmacia-prescricao \
  --region us-east-1 \
  --max-items 20

# Ver motivo da falha
aws cloudformation describe-stack-events \
  --stack-name farmacia-prescricao \
  --region us-east-1 \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'
```

### Tasks ECS não iniciam

```bash
# Ver logs do ECS
aws logs tail /ecs/farmacia-prescricao --follow

# Ver detalhes da task
aws ecs describe-tasks \
  --cluster farmacia-prescricao-cluster \
  --tasks $(aws ecs list-tasks \
    --cluster farmacia-prescricao-cluster \
    --service-name farmacia-prescricao-service \
    --query 'taskArns[0]' \
    --output text)
```

### API não conecta ao RDS

```bash
# Verificar Security Group
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=*rds*" \
  --region us-east-1

# Verificar se RDS está disponível
aws rds describe-db-instances \
  --db-instance-identifier farmacia-prescricao-postgres \
  --region us-east-1 \
  --query 'DBInstances[0].DBInstanceStatus'
```

### API não conecta ao OpenSearch

```bash
# Verificar status do domain
aws opensearch describe-domain \
  --domain-name farmacia-prescricao-search \
  --region us-east-1

# Testar conexão manualmente (de dentro do container)
aws ecs execute-command \
  --cluster farmacia-prescricao-cluster \
  --task <TASK_ID> \
  --container api \
  --interactive \
  --command "/bin/bash"

# Dentro do container:
curl -k -u elastic:senha https://opensearch-endpoint:443
```

## 💰 Custos AWS (Estimativa Mensal)

### Ambiente de Produção
```
ECS Fargate (2 tasks, 0.5 vCPU, 1GB):  ~$30/mês
RDS PostgreSQL (db.t3.micro):          ~$15/mês
OpenSearch (t3.small.search):          ~$45/mês
Application Load Balancer:             ~$20/mês
Data Transfer (estimado):              ~$5/mês
CloudWatch Logs:                       ~$5/mês
----------------------------------------
TOTAL:                                 ~$120/mês
```

### Ambiente de Desenvolvimento (Reduzido)
```yaml
# Alterações no aws-deploy.yml:
DesiredCount: 1              # Apenas 1 task
DBInstanceClass: db.t3.micro # Já é o menor
InstanceType: t3.micro.search # OpenSearch menor
```
**Custo reduzido: ~$80/mês**

### Free Tier (Primeiro Ano AWS)
- 750 horas/mês de db.t3.micro (RDS) - GRÁTIS
- 750 horas/mês de Load Balancer - GRÁTIS
- 5GB CloudWatch Logs - GRÁTIS

**Custo com Free Tier: ~$45/mês** (apenas Fargate + OpenSearch)

## 📦 Comandos Úteis AWS

```bash
# Ver todos os recursos criados
aws cloudformation describe-stack-resources \
  --stack-name farmacia-prescricao

# Ver outputs do stack
aws cloudformation describe-stacks \
  --stack-name farmacia-prescricao \
  --query 'Stacks[0].Outputs'

# Ver logs em tempo real
aws logs tail /ecs/farmacia-prescricao --follow

# Redeploy (após alterações no código)
./deploy-aws.sh

# Escalar manualmente
aws ecs update-service \
  --cluster farmacia-prescricao-cluster \
  --service farmacia-prescricao-service \
  --desired-count 5

# Parar temporariamente (manter infraestrutura)
aws ecs update-service \
  --cluster farmacia-prescricao-cluster \
  --service farmacia-prescricao-service \
  --desired-count 0

# Deletar TUDO (CUIDADO!)
aws cloudformation delete-stack \
  --stack-name farmacia-prescricao \
  --region us-east-1

# Monitorar deleção
aws cloudformation wait stack-delete-complete \
  --stack-name farmacia-prescricao
```

## 🔄 CI/CD com GitHub Actions

Crie `.github/workflows/deploy-aws.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: farmacia-prescricao-api
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd farmaciaAPI
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster farmacia-prescricao-cluster \
            --service farmacia-prescricao-service \
            --force-new-deployment
```

## 🔐 Segurança em Produção AWS

### 1. Secrets Manager para Senhas

```bash
# Armazenar senhas no Secrets Manager
aws secretsmanager create-secret \
  --name farmacia/db-password \
  --secret-string "senha_super_segura"

aws secretsmanager create-secret \
  --name farmacia/opensearch-password \
  --secret-string "outra_senha_segura"
```

No `aws-deploy.yml`, referencie:
```yaml
Environment:
  - Name: DATABASE_PASSWORD
    ValueFrom: arn:aws:secretsmanager:us-east-1:123456:secret:farmacia/db-password
```

### 2. Habilitar Encryption

Já configurado no template:
- ✅ RDS com encryption at rest
- ✅ OpenSearch com encryption at rest e in-transit
- ✅ ECS tasks em subnets privadas (opcional)

### 3. WAF (Web Application Firewall)

```bash
# Criar Web ACL
aws wafv2 create-web-acl \
  --name farmacia-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --region us-east-1

# Associar ao ALB
aws wafv2 associate-web-acl \
  --web-acl-arn <WEB_ACL_ARN> \
  --resource-arn <ALB_ARN>
```

## 📊 Monitoramento e Alertas

### CloudWatch Alarms

```bash
# Alarme para CPU alta
aws cloudwatch put-metric-alarm \
  --alarm-name farmacia-high-cpu \
  --alarm-description "CPU acima de 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# Alarme para erros 5xx
aws cloudwatch put-metric-alarm \
  --alarm-name farmacia-5xx-errors \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 60 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

### CloudWatch Dashboard

Acesse: https://console.aws.amazon.com/cloudwatch/

Métricas importantes:
- ECS CPU/Memory Utilization
- ALB Request Count
- ALB Target Response Time
- RDS CPU/Connections
- OpenSearch Cluster Status

---

**Status**: ✅ Pronto para deploy AWS  
**Versão**: 1.0.0  
**Data**: Novembro 2025
