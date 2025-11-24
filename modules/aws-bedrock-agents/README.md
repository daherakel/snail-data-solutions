# Infrastructure as Code (IaC)

Infraestructura de AWS definida como código usando Terraform para el proyecto Snail Data Solutions.

## Estructura

```
infrastructure/
└── terraform/
    ├── modules/                    # Módulos reutilizables
    │   ├── bedrock-agent/         # Configuración del agente Bedrock
    │   ├── bedrock-knowledge-base/ # Knowledge Base con vector store
    │   ├── lambda/                # Lambda functions
    │   ├── step-functions/        # Definición de workflows
    │   ├── s3-storage/           # Buckets S3 por ambiente
    │   └── iam/                  # Roles y políticas
    ├── environments/              # Configuración por ambiente
    │   ├── dev/
    │   │   ├── main.tf
    │   │   ├── variables.tf
    │   │   ├── outputs.tf
    │   │   └── terraform.tfvars
    │   ├── staging/
    │   └── prod/
    ├── backend.tf                 # Backend de Terraform (S3 + DynamoDB)
    └── versions.tf                # Versiones de providers
```

## Principios

### 1. Modularidad
- Cada módulo es independiente y reutilizable
- Los módulos reciben parámetros vía variables
- Outputs bien definidos para composición

### 2. Multi-Ambiente
- Configuración separada por ambiente (dev/staging/prod)
- Variables específicas en `terraform.tfvars`
- Backend remoto con workspaces de Terraform

### 3. Seguridad
- Principio de privilegios mínimos en IAM
- Secrets en AWS Secrets Manager (no en código)
- Encriptación habilitada por defecto
- Tags obligatorios para auditoría

### 4. Estado Remoto
- Backend en S3 con versionado
- Locking con DynamoDB para evitar conflictos
- Separación de estado por ambiente

## Prerrequisitos

### 1. Terraform Instalado
```bash
# macOS
brew install terraform

# Verificar instalación
terraform version
```

### 2. AWS CLI Configurado
```bash
# Ya está configurado en este proyecto
aws sts get-caller-identity
```

### 3. Permisos AWS
Necesitas permisos para crear:
- S3 buckets
- Lambda functions
- IAM roles y políticas
- Bedrock agents y knowledge bases
- Step Functions
- EventBridge rules
- Textract (para OCR)

## Uso

### Inicializar Terraform (Primera vez)

```bash
# Navegar al ambiente
cd terraform/environments/dev

# Inicializar Terraform
terraform init

# Ver qué va a crear
terraform plan

# Aplicar cambios
terraform apply
```

### Workflow de Desarrollo

```bash
# 1. Hacer cambios en módulos o configuración
vim terraform/modules/lambda/main.tf

# 2. Formatear código
terraform fmt -recursive

# 3. Validar sintaxis
terraform validate

# 4. Ver plan de cambios
terraform plan

# 5. Revisar cambios y aplicar
terraform apply

# 6. Verificar outputs
terraform output
```

### Cambiar de Ambiente

```bash
# Dev
cd terraform/environments/dev
terraform plan

# Staging
cd ../staging
terraform plan

# Prod
cd ../prod
terraform plan
```

### Destruir Recursos (⚠️ Cuidado)

```bash
# Solo en dev/staging
terraform destroy

# NUNCA en prod sin aprobación
```

## Variables por Ambiente

### Dev
- Modelos más pequeños y económicos
- Retención corta de logs y datos
- Sin replicación
- Sin backups automáticos

### Staging
- Configuración idéntica a prod
- Para testing pre-release
- Datos de prueba

### Prod
- Modelos optimizados
- Alta disponibilidad
- Backups automáticos
- Retención según compliance
- Monitoreo y alertas

## Convenciones

### Nomenclatura de Recursos

**Formato general**: `{proyecto}-{ambiente}-{servicio}-{proposito}`

Ejemplos:
- `snail-dev-bedrock-agent`
- `snail-prod-lambda-pdf-processor`
- `snail-staging-s3-raw-documents`

### Variables

```hcl
# variables.tf
variable "environment" {
  description = "Environment name (dev/staging/prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "snail"
}
```

### Tags Obligatorios

Todos los recursos deben tener:
```hcl
tags = {
  Project     = "snail-data-solutions"
  Environment = var.environment
  ManagedBy   = "terraform"
  Module      = "bedrock-agents"
  CostCenter  = "data-engineering"
}
```

### Outputs

```hcl
# outputs.tf
output "bucket_name" {
  description = "Name of the S3 bucket for raw documents"
  value       = module.s3_storage.bucket_name
}

output "lambda_function_arn" {
  description = "ARN of the PDF processor Lambda function"
  value       = module.lambda.function_arn
}
```

## Módulos Disponibles

### bedrock-agent
Configura un agente de Bedrock con Knowledge Base y action groups.

**Inputs**:
- `agent_name`: Nombre del agente
- `model_id`: ID del modelo (claude-3-sonnet, etc.)
- `knowledge_base_id`: ID de la knowledge base

**Outputs**:
- `agent_id`: ID del agente creado
- `agent_arn`: ARN del agente

### lambda
Despliega Lambda functions con configuración estandarizada.

**Inputs**:
- `function_name`: Nombre de la función
- `handler`: Handler de Python (ej: `handler.lambda_handler`)
- `runtime`: Runtime de Python (ej: `python3.11`)
- `source_dir`: Directorio con el código

**Outputs**:
- `function_name`: Nombre de la función
- `function_arn`: ARN de la función
- `invoke_arn`: ARN para invocar

### s3-storage
Crea buckets S3 con encriptación y lifecycle policies.

**Inputs**:
- `bucket_name`: Nombre del bucket
- `versioning_enabled`: Habilitar versionado
- `lifecycle_rules`: Reglas de lifecycle

**Outputs**:
- `bucket_name`: Nombre del bucket
- `bucket_arn`: ARN del bucket

## Estado Remoto (Backend)

### Configuración

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "snail-terraform-state"
    key            = "environments/dev/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "snail-terraform-locks"
  }
}
```

### Setup del Backend (Una sola vez)

```bash
# 1. Crear bucket para estado
aws s3 mb s3://snail-terraform-state --region us-east-1

# 2. Habilitar versionado
aws s3api put-bucket-versioning \
  --bucket snail-terraform-state \
  --versioning-configuration Status=Enabled

# 3. Crear tabla DynamoDB para locks
aws dynamodb create-table \
  --table-name snail-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

## Seguridad

### Secrets

**NUNCA** colocar secrets en el código Terraform. Usar AWS Secrets Manager:

```hcl
# Referencia a secret existente
data "aws_secretsmanager_secret_version" "api_key" {
  secret_id = "snail/bedrock/api-key"
}

# Usar en configuración
resource "aws_lambda_function" "processor" {
  environment {
    variables = {
      API_KEY = data.aws_secretsmanager_secret_version.api_key.secret_string
    }
  }
}
```

### IAM Roles

Principio de privilegios mínimos:

```hcl
# Rol específico para Lambda
resource "aws_iam_role" "lambda_processor" {
  name = "${var.project_name}-${var.environment}-lambda-processor"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Solo permisos necesarios
resource "aws_iam_role_policy" "lambda_s3_read" {
  role = aws_iam_role.lambda_processor.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:GetObject"]
      Resource = "${aws_s3_bucket.raw_docs.arn}/*"
    }]
  })
}
```

## Best Practices

### 1. Versionado
- Commitear cambios de Terraform junto con código
- Usar tags en releases
- Documentar cambios en commits

### 2. Testing
- Probar en dev primero
- Validar en staging
- Desplegar a prod con aprobación

### 3. Rollback
- Backend con versionado permite rollback
- Mantener state files anteriores
- Tener plan de rollback para prod

### 4. Costos
- Usar tags para tracking de costos
- Implementar lifecycle policies en S3
- Dimensionar recursos apropiadamente por ambiente

### 5. Documentación
- Documentar módulos con README
- Comentarios en configuraciones complejas
- Mantener outputs actualizados

## Troubleshooting

### Error: Backend initialization failed
```bash
# Verificar que el bucket existe
aws s3 ls s3://snail-terraform-state

# Verificar permisos
aws s3api get-bucket-versioning --bucket snail-terraform-state
```

### Error: Lock acquisition failed
```bash
# Verificar locks en DynamoDB
aws dynamodb scan --table-name snail-terraform-locks

# Forzar unlock (solo si estás seguro)
terraform force-unlock <lock-id>
```

### Error: Resource already exists
```bash
# Importar recurso existente
terraform import aws_s3_bucket.example my-bucket-name

# O eliminar de estado si no lo quieres gestionar
terraform state rm aws_s3_bucket.example
```

## Próximos Pasos

1. ⏳ Implementar módulos de Terraform
2. ⏳ Configurar backend remoto
3. ⏳ Desplegar en ambiente dev
4. ⏳ Testing y validación
5. ⏳ Documentar outputs y variables
6. ⏳ CI/CD para Terraform (GitHub Actions)

## Referencias

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS Bedrock Terraform](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/bedrock_agent)
