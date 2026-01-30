#!/bin/bash

# Script para configurar .env.local automáticamente

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FRONTEND_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$FRONTEND_DIR"

echo "🔧 Configurando variables de entorno para el frontend..."

# Obtener credenciales AWS desde AWS CLI
AWS_ACCESS_KEY=$(aws configure get aws_access_key_id 2>/dev/null || echo "")
AWS_SECRET_KEY=$(aws configure get aws_secret_access_key 2>/dev/null || echo "")
AWS_REGION=$(aws configure get region 2>/dev/null || echo "us-east-1")

# Obtener URL del Lambda desde Terraform
TERRAFORM_DIR="../../modules/aws-bedrock-agents/infrastructure/terraform/environments/dev"
LAMBDA_URL=""

if [ -d "$TERRAFORM_DIR" ]; then
    cd "$TERRAFORM_DIR"
    LAMBDA_URL=$(terraform output -raw query_handler_url 2>/dev/null || echo "")
    cd "$FRONTEND_DIR"
fi

# Obtener bucket name
BUCKET_NAME="snail-bedrock-dev-raw-documents"
if [ -d "$TERRAFORM_DIR" ]; then
    cd "$TERRAFORM_DIR"
    BUCKET_NAME=$(terraform output -raw raw_documents_bucket 2>/dev/null || echo "snail-bedrock-dev-raw-documents")
    cd "$FRONTEND_DIR"
fi

# Crear o actualizar .env.local
ENV_FILE="$FRONTEND_DIR/.env.local"

echo "" > "$ENV_FILE"
echo "# AWS Bedrock Agents - Frontend Configuration" >> "$ENV_FILE"
echo "# Configurado automáticamente el $(date)" >> "$ENV_FILE"
echo "" >> "$ENV_FILE"
echo "# AWS Configuration" >> "$ENV_FILE"
echo "AWS_REGION=${AWS_REGION}" >> "$ENV_FILE"

if [ -n "$AWS_ACCESS_KEY" ]; then
    echo "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY}" >> "$ENV_FILE"
    echo "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_KEY}" >> "$ENV_FILE"
    echo "✅ Credenciales AWS configuradas desde AWS CLI"
else
    echo "# AWS_ACCESS_KEY_ID=tu_access_key_aqui" >> "$ENV_FILE"
    echo "# AWS_SECRET_ACCESS_KEY=tu_secret_key_aqui" >> "$ENV_FILE"
    echo "⚠️  No se encontraron credenciales AWS. Configúralas manualmente o usa default provider."
fi

echo "" >> "$ENV_FILE"
echo "# Lambda Query Handler URL" >> "$ENV_FILE"
if [ -n "$LAMBDA_URL" ]; then
    echo "LAMBDA_QUERY_URL=${LAMBDA_URL}" >> "$ENV_FILE"
    echo "✅ Lambda URL configurada: ${LAMBDA_URL}"
else
    echo "LAMBDA_QUERY_URL=https://tu-lambda-url.lambda-url.us-east-1.on.aws/" >> "$ENV_FILE"
    echo "⚠️  No se encontró Lambda URL. Configúrala manualmente."
    echo "   Obtener con: cd $TERRAFORM_DIR && terraform output query_handler_url"
fi

echo "" >> "$ENV_FILE"
echo "# S3 Bucket Configuration" >> "$ENV_FILE"
echo "RAW_DOCUMENTS_BUCKET=${BUCKET_NAME}" >> "$ENV_FILE"

echo ""
echo "✅ Archivo .env.local configurado en: $ENV_FILE"
echo ""
echo "📝 Verifica la configuración:"
echo "   cat .env.local"

