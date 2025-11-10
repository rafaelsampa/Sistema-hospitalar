#!/bin/bash
# ========================================
# Script de Deploy - Farmácia & Prescrição
# ========================================

set -e

echo "=========================================="
echo " Deploy - Microserviço Farmácia & Prescrição"
echo "=========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    log_error "Docker não está instalado. Instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose não está instalado. Instale o Docker Compose primeiro."
    exit 1
fi

log_info "Docker e Docker Compose encontrados ✓"

# Parar containers existentes
log_info "Parando containers existentes..."
docker-compose down

# Remover volumes antigos (opcional - descomente se quiser reset completo)
# log_warn "Removendo volumes antigos..."
# docker-compose down -v

# Build das imagens
log_info "Construindo imagens Docker..."
docker-compose build --no-cache

# Iniciar serviços de infraestrutura primeiro
log_info "Iniciando PostgreSQL..."
docker-compose up -d postgres

log_info "Aguardando PostgreSQL ficar pronto..."
sleep 10

log_info "Iniciando Elasticsearch..."
docker-compose up -d elasticsearch

log_info "Aguardando Elasticsearch ficar pronto..."
sleep 30

# Verificar saúde dos serviços
log_info "Verificando saúde do PostgreSQL..."
docker-compose exec -T postgres pg_isready -U farmacia_user -d farmacia_prescricao || {
    log_error "PostgreSQL não está pronto"
    exit 1
}
log_info "PostgreSQL está pronto ✓"

log_info "Verificando saúde do Elasticsearch..."
docker-compose exec -T elasticsearch curl -k -u elastic:vl60PBF8o1qbViYLeAHe https://localhost:9200/_cluster/health || {
    log_error "Elasticsearch não está pronto"
    exit 1
}
log_info "Elasticsearch está pronto ✓"

# Iniciar API
log_info "Iniciando API..."
docker-compose up -d api

log_info "Aguardando API inicializar..."
sleep 15

# Verificar saúde da API
log_info "Verificando saúde da API..."
curl -f http://localhost:8000/health || {
    log_error "API não está respondendo"
    docker-compose logs api
    exit 1
}
log_info "API está pronta ✓"

# Mostrar status dos containers
echo ""
log_info "Status dos containers:"
docker-compose ps

# Mostrar logs da API
echo ""
log_info "Últimos logs da API:"
docker-compose logs --tail=20 api

echo ""
echo "=========================================="
log_info "Deploy concluído com sucesso!"
echo "=========================================="
echo ""
echo " Serviços disponíveis:"
echo "   • API:            http://localhost:8000"
echo "   • API Docs:       http://localhost:8000/docs"
echo "   • Health Check:   http://localhost:8000/health"
echo "   • PostgreSQL:     localhost:5432"
echo "   • Elasticsearch:  https://localhost:9200"
echo ""
echo " Para ver logs em tempo real:"
echo "   docker-compose logs -f api"
echo ""
echo " Para parar os serviços:"
echo "   docker-compose down"
echo ""
