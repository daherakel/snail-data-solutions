#!/bin/bash

# Script para deployar un nuevo tenant/cliente
# Uso: ./deploy-tenant.sh <TENANT_ID> <ENVIRONMENT> [OPTIONS]

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar argumentos
if [ $# -lt 2 ]; then
    log_error "Uso: $0 <TENANT_ID> <ENVIRONMENT> [OPTIONS]"
    echo ""
    echo "Opciones:"
    echo "  --skip-terraform    No ejecutar terraform apply"
    echo "  --skip-validation   No validar configuración"
    echo "  --terraform-args    Argumentos adicionales para terraform"
    echo ""
    echo "Ejemplo:"
    echo "  $0 client_acme dev"
    echo "  $0 client_acme prod --skip-validation"
    exit 1
fi

TENANT_ID=$1
ENVIRONMENT=$2
SKIP_TERRAFORM=false
SKIP_VALIDATION=false
TERRAFORM_ARGS=""

# Parsear opciones
shift 2
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-terraform)
            SKIP_TERRAFORM=true
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        --terraform-args)
            TERRAFORM_ARGS="$2"
            shift 2
            ;;
        *)
            log_error "Opción desconocida: $1"
            exit 1
            ;;
    esac
done

# Verificar que estamos en el directorio correcto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MODULE_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

if [ ! -f "$MODULE_DIR/README.md" ]; then
    log_error "No se encontró README.md. ¿Estás en el directorio correcto?"
    exit 1
fi

log_info "Deployando tenant: $TENANT_ID en ambiente: $ENVIRONMENT"
log_info "Directorio del módulo: $MODULE_DIR"

# Validar configuración del tenant
if [ "$SKIP_VALIDATION" = false ]; then
    log_info "Validando configuración del tenant..."
    
    TENANT_CONFIG="$MODULE_DIR/shared/config/tenant-config.yaml"
    if [ ! -f "$TENANT_CONFIG" ]; then
        log_error "Archivo de configuración no encontrado: $TENANT_CONFIG"
        exit 1
    fi
    
    # Verificar que el tenant existe en la configuración
    if ! grep -q "^$TENANT_ID:" "$TENANT_CONFIG"; then
        log_warn "Tenant '$TENANT_ID' no encontrado en tenant-config.yaml"
        log_warn "Usando configuración 'default'"
    fi
fi

# Verificar prerrequisitos
log_info "Verificando prerrequisitos..."

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI no está instalado"
    exit 1
fi

# Verificar Terraform
if ! command -v terraform &> /dev/null; then
    log_error "Terraform no está instalado"
    exit 1
fi

# Verificar credenciales AWS
if ! aws sts get-caller-identity &> /dev/null; then
    log_error "No se pueden obtener credenciales de AWS"
    exit 1
fi

log_info "Prerrequisitos verificados ✓"

# Configurar variables de entorno
export TENANT_ID=$TENANT_ID
export ENVIRONMENT=$ENVIRONMENT

# Preparar Terraform
TERRAFORM_DIR="$MODULE_DIR/infrastructure/terraform/environments/$ENVIRONMENT"

if [ ! -d "$TERRAFORM_DIR" ]; then
    log_error "Directorio de Terraform no encontrado: $TERRAFORM_DIR"
    log_info "Creando estructura de directorios..."
    mkdir -p "$TERRAFORM_DIR"
    log_warn "Necesitas crear los archivos de Terraform para este ambiente"
fi

cd "$TERRAFORM_DIR"

# Crear archivo de variables para el tenant si no existe
TFVARS_FILE="${TENANT_ID}.tfvars"
TFVARS_TEMPLATE="$MODULE_DIR/templates/terraform.tfvars.example"

if [ ! -f "$TFVARS_FILE" ]; then
    log_info "Creando archivo de variables Terraform: $TFVARS_FILE"
    if [ -f "$TFVARS_TEMPLATE" ]; then
        cp "$TFVARS_TEMPLATE" "$TFVARS_FILE"
        # Reemplazar valores en el template
        sed -i.bak "s/tenant_id = \"default\"/tenant_id = \"$TENANT_ID\"/g" "$TFVARS_FILE"
        rm -f "${TFVARS_FILE}.bak"
        log_info "Archivo creado desde template. Por favor, revisa y edita: $TFVARS_FILE"
    else
        log_warn "Template no encontrado. Creando archivo básico..."
        cat > "$TFVARS_FILE" <<EOF
project_name = "${TENANT_ID}"
environment  = "${ENVIRONMENT}"
tenant_id    = "${TENANT_ID}"
EOF
    fi
fi

# Inicializar Terraform si es necesario
if [ ! -d ".terraform" ]; then
    log_info "Inicializando Terraform..."
    terraform init
fi

# Ejecutar Terraform
if [ "$SKIP_TERRAFORM" = false ]; then
    log_info "Ejecutando terraform plan..."
    terraform plan -var="tenant_id=$TENANT_ID" -var-file="$TFVARS_FILE" $TERRAFORM_ARGS
    
    log_warn "¿Deseas continuar con terraform apply? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "Ejecutando terraform apply..."
        terraform apply -var="tenant_id=$TENANT_ID" -var-file="$TFVARS_FILE" $TERRAFORM_ARGS
        log_info "Terraform apply completado ✓"
    else
        log_warn "Terraform apply cancelado"
    fi
else
    log_info "Omitiendo terraform apply (--skip-terraform)"
fi

# Obtener outputs
log_info "Obteniendo outputs de Terraform..."
terraform output -json > "outputs-${TENANT_ID}.json" 2>/dev/null || log_warn "No se pudieron obtener outputs"

# Mostrar información útil
log_info "=== Deployment Completado ==="
log_info "Tenant ID: $TENANT_ID"
log_info "Environment: $ENVIRONMENT"
log_info ""
log_info "Próximos pasos:"
log_info "1. Verificar que los recursos se crearon correctamente"
log_info "2. Configurar integraciones si aplica (Slack, Teams, etc.)"
log_info "3. Subir documentos de prueba"
log_info "4. Probar query handler"
log_info ""
log_info "Ver documentación completa: $MODULE_DIR/REPLICABILITY.md"

# Mostrar outputs importantes si están disponibles
if [ -f "outputs-${TENANT_ID}.json" ]; then
    log_info ""
    log_info "Outputs importantes:"
    terraform output query_handler_url 2>/dev/null && echo "" || true
fi

log_info "Deployment completado exitosamente ✓"

