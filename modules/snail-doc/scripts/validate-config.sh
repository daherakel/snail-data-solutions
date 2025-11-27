#!/bin/bash

# Script para validar configuración de tenant
# Uso: ./validate-config.sh <TENANT_ID>

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

if [ $# -lt 1 ]; then
    log_error "Uso: $0 <TENANT_ID>"
    exit 1
fi

TENANT_ID=$1
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MODULE_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

log_info "Validando configuración para tenant: $TENANT_ID"

# Verificar que el tenant existe en la configuración
TENANT_CONFIG="$MODULE_DIR/shared/config/tenant-config.yaml"
if [ ! -f "$TENANT_CONFIG" ]; then
    log_error "Archivo de configuración no encontrado: $TENANT_CONFIG"
    exit 1
fi

# Verificar que el tenant existe
if ! grep -q "^$TENANT_ID:" "$TENANT_CONFIG"; then
    log_warn "Tenant '$TENANT_ID' no encontrado en tenant-config.yaml"
    log_warn "Se usará la configuración 'default'"
else
    log_info "✓ Tenant encontrado en configuración"
fi

# Validar que Python está disponible para cargar configuración
if ! command -v python3 &> /dev/null; then
    log_warn "Python3 no encontrado - no se puede validar sintaxis YAML"
else
    log_info "Validando sintaxis YAML..."
    python3 -c "import yaml; yaml.safe_load(open('$TENANT_CONFIG'))" && log_info "✓ Sintaxis YAML válida" || log_error "Error en sintaxis YAML"
fi

# Verificar estructura de directorios necesaria
log_info "Verificando estructura de directorios..."

REQUIRED_DIRS=(
    "$MODULE_DIR/shared/config"
    "$MODULE_DIR/shared/prompts"
    "$MODULE_DIR/lambda-functions"
    "$MODULE_DIR/infrastructure/terraform/modules"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        log_info "✓ $dir existe"
    else
        log_error "✗ Directorio faltante: $dir"
    fi
done

log_info "Validación completada"

