#!/bin/bash

# Script para testear integraciones
# Uso: ./test-integration.sh <INTEGRATION> <TENANT_ID> [OPTIONS]

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

if [ $# -lt 2 ]; then
    log_error "Uso: $0 <INTEGRATION> <TENANT_ID>"
    echo ""
    echo "Integraciones disponibles:"
    echo "  slack  - Testear integración de Slack"
    echo ""
    exit 1
fi

INTEGRATION=$1
TENANT_ID=$2
ENVIRONMENT=${ENVIRONMENT:-dev}

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MODULE_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

log_info "Testeando integración: $INTEGRATION para tenant: $TENANT_ID"

# Test específico por integración
case $INTEGRATION in
    slack)
        log_info "Testeando integración Slack..."
        
        # Verificar que la función Lambda existe
        FUNCTION_NAME="${TENANT_ID}-${ENVIRONMENT}-slack-handler"
        if aws lambda get-function --function-name "$FUNCTION_NAME" &> /dev/null; then
            log_info "✓ Función Lambda encontrada: $FUNCTION_NAME"
        else
            log_error "✗ Función Lambda no encontrada: $FUNCTION_NAME"
            exit 1
        fi
        
        # Obtener Function URL si existe
        FUNCTION_URL=$(aws lambda get-function-url-config --function-name "$FUNCTION_NAME" --query FunctionUrl --output text 2>/dev/null || echo "")
        
        if [ -n "$FUNCTION_URL" ]; then
            log_info "✓ Function URL encontrada: $FUNCTION_URL"
            
            # Test URL verification challenge
            log_info "Testeando URL verification challenge..."
            CHALLENGE="test-challenge-123"
            RESPONSE=$(curl -s -X POST "$FUNCTION_URL" \
                -H "Content-Type: application/json" \
                -d "{\"type\":\"url_verification\",\"challenge\":\"$CHALLENGE\"}")
            
            if echo "$RESPONSE" | grep -q "$CHALLENGE"; then
                log_info "✓ URL verification challenge exitoso"
            else
                log_error "✗ URL verification challenge falló"
                log_debug "Respuesta: $RESPONSE"
            fi
        else
            log_warn "Function URL no encontrada. Verificar configuración en Terraform."
        fi
        
        # Verificar logs recientes
        log_info "Verificando logs recientes..."
        LOG_GROUP="/aws/lambda/$FUNCTION_NAME"
        if aws logs describe-log-groups --log-group-name-prefix "$LOG_GROUP" --query 'logGroups[0].logGroupName' --output text | grep -q "$LOG_GROUP"; then
            log_info "✓ Log group existe"
        else
            log_warn "Log group no encontrado: $LOG_GROUP"
        fi
        
        log_info "Test de Slack completado"
        ;;
    
    *)
        log_error "Integración desconocida: $INTEGRATION"
        exit 1
        ;;
esac

log_info "Testing completado"

