#!/bin/bash
# Script para subir un documento y monitorear su procesamiento

set -e

ENVIRONMENT=${1:-dev}
DOCUMENT=${2}

if [ -z "$DOCUMENT" ]; then
    echo "❌ Uso: $0 <environment> <document.pdf>"
    echo "   Ejemplo: $0 dev mi-documento.pdf"
    exit 1
fi

if [ ! -f "$DOCUMENT" ]; then
    echo "❌ Archivo no encontrado: $DOCUMENT"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/../infrastructure/terraform/environments/$ENVIRONMENT"

echo "📤 Subiendo documento a S3..."
echo ""

# Obtener bucket desde Terraform
cd "$TERRAFORM_DIR"
RAW_BUCKET=$(terraform output -raw raw_documents_bucket)
SF_ARN=$(terraform output -raw step_functions_arn)

echo "📦 Bucket: $RAW_BUCKET"
echo "📄 Archivo: $DOCUMENT"
echo ""

# Subir documento
aws s3 cp "$DOCUMENT" "s3://$RAW_BUCKET/"

FILENAME=$(basename "$DOCUMENT")

echo "✅ Documento subido: s3://$RAW_BUCKET/$FILENAME"
echo ""
echo "⏳ Esperando procesamiento (esto puede tomar 1-2 minutos)..."
echo ""

# Esperar un poco para que se dispare EventBridge
sleep 5

# Monitorear ejecuciones
echo "📊 Ejecuciones recientes de Step Functions:"
aws stepfunctions list-executions \
    --state-machine-arn "$SF_ARN" \
    --max-results 5 \
    --query 'executions[*].[name,status,startDate]' \
    --output table

echo ""
echo "Para ver logs detallados:"
echo "  aws stepfunctions describe-execution --execution-arn <ARN>"
