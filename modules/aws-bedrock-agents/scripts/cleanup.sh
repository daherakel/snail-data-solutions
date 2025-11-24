#!/bin/bash
# Script para limpiar recursos de AWS

set -e

ENVIRONMENT=${1:-dev}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/../infrastructure/terraform/environments/$ENVIRONMENT"

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}⚠️  ADVERTENCIA: Esto eliminará TODOS los recursos del ambiente $ENVIRONMENT${NC}"
echo ""
read -p "¿Estás seguro? Escribe 'yes' para continuar: " -r
echo

if [ "$REPLY" != "yes" ]; then
    echo "❌ Cleanup cancelado"
    exit 1
fi

cd "$TERRAFORM_DIR"

# Obtener nombres de buckets
echo "📦 Obteniendo nombres de buckets..."
RAW_BUCKET=$(terraform output -raw raw_documents_bucket 2>/dev/null || echo "")
PROCESSED_BUCKET=$(terraform output -raw processed_documents_bucket 2>/dev/null || echo "")
CHROMADB_BUCKET=$(terraform output -raw chromadb_backup_bucket 2>/dev/null || echo "")

# Vaciar buckets
if [ -n "$RAW_BUCKET" ]; then
    echo "🗑️  Vaciando bucket: $RAW_BUCKET"
    aws s3 rm "s3://$RAW_BUCKET" --recursive || true
fi

if [ -n "$PROCESSED_BUCKET" ]; then
    echo "🗑️  Vaciando bucket: $PROCESSED_BUCKET"
    aws s3 rm "s3://$PROCESSED_BUCKET" --recursive || true
fi

if [ -n "$CHROMADB_BUCKET" ]; then
    echo "🗑️  Vaciando bucket: $CHROMADB_BUCKET"
    aws s3 rm "s3://$CHROMADB_BUCKET" --recursive || true
fi

# Destruir infraestructura
echo ""
echo "🔥 Destruyendo infraestructura con Terraform..."
terraform destroy

echo ""
echo "✅ Cleanup completado"
