#!/bin/bash
# Script para testear el query handler

set -e

ENVIRONMENT=${1:-dev}
QUERY=${2:-"¿De qué trata el documento?"}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/../infrastructure/terraform/environments/$ENVIRONMENT"

echo "🔍 Testing Query Handler..."
echo ""

# Obtener URL de la Lambda desde Terraform
cd "$TERRAFORM_DIR"
QUERY_URL=$(terraform output -raw query_handler_url 2>/dev/null)

if [ -z "$QUERY_URL" ] || [ "$QUERY_URL" == "null" ]; then
    echo "❌ Query handler URL no disponible"
    echo "   Asegúrate de que create_function_url=true en variables"
    exit 1
fi

echo "📍 URL: $QUERY_URL"
echo "❓ Query: $QUERY"
echo ""

# Hacer request
echo "📤 Enviando query..."
RESPONSE=$(curl -s -X POST "$QUERY_URL" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\"}")

echo ""
echo "📥 Respuesta:"
echo "$RESPONSE" | jq '.'

echo ""
echo "✅ Test completado"
