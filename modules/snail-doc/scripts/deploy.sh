#!/bin/bash
# Script de deployment completo para AWS Bedrock Agents módulo

set -e

ENVIRONMENT=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Deploying AWS Bedrock Agents - Environment: $ENVIRONMENT"
echo "=================================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar prerrequisitos
echo "📋 Verificando prerrequisitos..."

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform no está instalado${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI no está instalado${NC}"
    exit 1
fi

# Verificar credenciales AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI no está configurado correctamente${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerrequisitos verificados${NC}"
echo ""

# Paso 1: Crear Lambda Layer (si no existe)
echo "📦 Paso 1: Creando Lambda Layer de FAISS..."
LAYER_DIR="$PROJECT_ROOT/lambda-functions/lambda-layer-chromadb"

if [ ! -f "$LAYER_DIR/faiss-layer.zip" ]; then
    echo "   Building FAISS layer (faiss-cpu + PyPDF2 + numpy)..."
    cd "$LAYER_DIR"
    ./build-layer.sh

    echo "   Publicando layer en AWS..."
    LAYER_ARN=$(aws lambda publish-layer-version \
        --layer-name snail-bedrock-$ENVIRONMENT-faiss-layer \
        --zip-file fileb://faiss-layer.zip \
        --compatible-runtimes python3.11 \
        --region us-east-1 \
        --query 'LayerVersionArn' \
        --output text)

    echo -e "${GREEN}✅ Lambda Layer creado: $LAYER_ARN${NC}"
else
    echo -e "${YELLOW}⚠️  Lambda Layer ya existe (faiss-layer.zip), saltando...${NC}"
fi
echo ""

# Paso 2: Deploy Terraform
echo "🏗️  Paso 2: Desplegando infraestructura con Terraform..."
TERRAFORM_DIR="$PROJECT_ROOT/infrastructure/terraform/environments/$ENVIRONMENT"

cd "$TERRAFORM_DIR"

echo "   Inicializando Terraform..."
terraform init

echo "   Validando configuración..."
terraform validate

echo "   Generando plan..."
terraform plan -out=tfplan

echo ""
read -p "¿Continuar con el deployment? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Deployment cancelado${NC}"
    rm -f tfplan
    exit 1
fi

echo "   Aplicando cambios..."
terraform apply tfplan
rm -f tfplan

echo -e "${GREEN}✅ Infraestructura desplegada${NC}"
echo ""

# Paso 3: Mostrar outputs
echo "📊 Paso 3: Información del deployment..."
terraform output

echo ""
echo -e "${GREEN}🎉 Deployment completado exitosamente!${NC}"
echo ""
echo "Próximos pasos:"
echo "  1. Subir un PDF de prueba (se procesará automáticamente):"
echo "     aws s3 cp test.pdf s3://\$(terraform output -raw raw_documents_bucket)/"
echo ""
echo "  2. Monitorear procesamiento:"
echo "     aws logs tail /aws/lambda/snail-bedrock-$ENVIRONMENT-pdf-processor --follow"
echo ""
echo "  3. Hacer una query:"
echo "     curl -X POST \$(terraform output -raw query_handler_url) \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"query\": \"¿De qué trata el documento?\"}'"
echo ""
echo "  4. Verificar FAISS index en S3:"
echo "     aws s3 ls s3://\$(terraform output -raw chromadb_backup_bucket)/"
