#!/bin/bash
# ========================================
# Script de Deploy AWS - Farmácia & Prescrição
# ========================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logs
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Configurações
STACK_NAME="farmacia-prescricao"
AWS_REGION="us-east-1"  # Altere conforme necessário
DOCKER_IMAGE_PATH="./farmaciaAPI"

echo "=========================================="
echo " Deploy AWS - Microserviço Farmácia"
echo "=========================================="
echo ""

# ========================================
# Verificações
# ========================================

log_step "1/8 Verificando pré-requisitos..."

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI não está instalado. Instale: https://aws.amazon.com/cli/"
    exit 1
fi
log_info "AWS CLI encontrado ✓"

# Verificar Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker não está instalado. Instale: https://docker.com"
    exit 1
fi
log_info "Docker encontrado ✓"

# Verificar credenciais AWS
if ! aws sts get-caller-identity &> /dev/null; then
    log_error "Credenciais AWS não configuradas. Execute: aws configure"
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
log_info "AWS Account ID: $AWS_ACCOUNT_ID ✓"

# Verificar CloudFormation template
if [ ! -f "aws-deploy.yml" ]; then
    log_error "Arquivo aws-deploy.yml não encontrado!"
    exit 1
fi
log_info "Template CloudFormation encontrado ✓"

echo ""

# ========================================
# Solicitar parâmetros
# ========================================

log_step "2/8 Configurando parâmetros..."

read -p "Região AWS [us-east-1]: " input_region
AWS_REGION=${input_region:-us-east-1}

read -p "Environment [production]: " input_env
ENVIRONMENT=${input_env:-production}

read -sp "Senha PostgreSQL (mínimo 8 caracteres): " DB_PASSWORD
echo ""
if [ ${#DB_PASSWORD} -lt 8 ]; then
    log_error "Senha do PostgreSQL deve ter no mínimo 8 caracteres"
    exit 1
fi

read -sp "Senha OpenSearch (mínimo 8 caracteres): " OPENSEARCH_PASSWORD
echo ""
if [ ${#OPENSEARCH_PASSWORD} -lt 8 ]; then
    log_error "Senha do OpenSearch deve ter no mínimo 8 caracteres"
    exit 1
fi

log_info "Parâmetros configurados ✓"
echo ""

# ========================================
# Deploy CloudFormation Stack
# ========================================

log_step "3/8 Criando infraestrutura AWS (CloudFormation)..."
log_warn "Isso pode levar 15-20 minutos..."

aws cloudformation deploy \
    --template-file aws-deploy.yml \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --parameter-overrides \
        Environment=$ENVIRONMENT \
        DBPassword=$DB_PASSWORD \
        OpenSearchPassword=$OPENSEARCH_PASSWORD \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset

if [ $? -ne 0 ]; then
    log_error "Falha ao criar stack CloudFormation"
    exit 1
fi

log_info "Stack CloudFormation criada ✓"
echo ""

# ========================================
# Obter outputs da stack
# ========================================

log_step "4/8 Obtendo informações da infraestrutura..."

ECR_URI=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryUri`].OutputValue' \
    --output text)

ALB_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
    --output text)

ECS_CLUSTER=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' \
    --output text)

log_info "ECR Repository: $ECR_URI"
log_info "Load Balancer: $ALB_URL"
log_info "ECS Cluster: $ECS_CLUSTER"
echo ""

# ========================================
# Build e Push da imagem Docker
# ========================================

log_step "5/8 Construindo imagem Docker..."

cd $DOCKER_IMAGE_PATH

docker build -t $STACK_NAME:latest .

if [ $? -ne 0 ]; then
    log_error "Falha ao construir imagem Docker"
    exit 1
fi

log_info "Imagem construída ✓"

cd ..
echo ""

# ========================================
# Login no ECR
# ========================================

log_step "6/8 Fazendo login no ECR..."

aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_URI

if [ $? -ne 0 ]; then
    log_error "Falha ao fazer login no ECR"
    exit 1
fi

log_info "Login no ECR realizado ✓"
echo ""

# ========================================
# Tag e Push da imagem
# ========================================

log_step "7/8 Enviando imagem para ECR..."

docker tag $STACK_NAME:latest $ECR_URI:latest
docker push $ECR_URI:latest

if [ $? -ne 0 ]; then
    log_error "Falha ao enviar imagem para ECR"
    exit 1
fi

log_info "Imagem enviada para ECR ✓"
echo ""

# ========================================
# Atualizar ECS Service
# ========================================

log_step "8/8 Atualizando serviço ECS..."

aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $STACK_NAME-service \
    --force-new-deployment \
    --region $AWS_REGION \
    > /dev/null

if [ $? -ne 0 ]; then
    log_error "Falha ao atualizar serviço ECS"
    exit 1
fi

log_info "Serviço ECS atualizado ✓"

log_warn "Aguardando deploy do serviço (pode levar 3-5 minutos)..."
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER \
    --services $STACK_NAME-service \
    --region $AWS_REGION

log_info "Serviço ECS estável ✓"
echo ""

# ========================================
# Verificar health check
# ========================================

echo "Verificando health check da API..."
sleep 10

HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $ALB_URL/health)

if [ "$HEALTH_STATUS" == "200" ]; then
    log_info "API está saudável ✓"
else
    log_warn "API ainda não está respondendo (HTTP $HEALTH_STATUS)"
    log_warn "Verifique os logs: aws logs tail /ecs/$STACK_NAME --follow"
fi

echo ""
echo "=========================================="
log_info "Deploy AWS concluído com sucesso!"
echo "=========================================="
echo ""
echo " 🚀 Recursos provisionados:"
echo "   • Load Balancer:  $ALB_URL"
echo "   • API Docs:       $ALB_URL/docs"
echo "   • Health Check:   $ALB_URL/health"
echo "   • ECS Cluster:    $ECS_CLUSTER"
echo "   • ECR Repository: $ECR_URI"
echo ""
echo " 📊 Comandos úteis:"
echo ""
echo "   # Ver logs da API"
echo "   aws logs tail /ecs/$STACK_NAME --follow --region $AWS_REGION"
echo ""
echo "   # Ver status dos serviços ECS"
echo "   aws ecs describe-services --cluster $ECS_CLUSTER --services $STACK_NAME-service --region $AWS_REGION"
echo ""
echo "   # Redeploy (após mudanças no código)"
echo "   ./deploy-aws.sh"
echo ""
echo "   # Deletar toda infraestrutura"
echo "   aws cloudformation delete-stack --stack-name $STACK_NAME --region $AWS_REGION"
echo ""
echo " 💰 Custos estimados (mensal):"
echo "   • ECS Fargate (2 tasks): ~\$30"
echo "   • RDS PostgreSQL t3.micro: ~\$15"
echo "   • OpenSearch t3.small: ~\$45"
echo "   • ALB: ~\$20"
echo "   • Total aproximado: ~\$110/mês"
echo ""
echo " ⚠️  Para reduzir custos em ambiente de desenvolvimento:"
echo "   - Reduza DesiredCount para 1 no CloudFormation"
echo "   - Use OpenSearch t3.micro ao invés de t3.small"
echo ""
