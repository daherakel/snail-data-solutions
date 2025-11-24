# Terraform - DEV Environment

Configuración de Terraform para el ambiente de desarrollo del módulo AWS Bedrock Agents.

## 📋 Prerrequisitos

1. **Terraform instalado** (>= 1.0)
   ```bash
   brew install terraform
   ```

2. **AWS CLI configurado**
   ```bash
   aws configure
   # Verificar
   aws sts get-caller-identity
   ```

3. **Lambda functions creadas** (en `lambda-functions/`)
   - `pdf-processor/`
   - `query-handler/`

## 🚀 Quick Start

### 1. Inicializar Terraform

```bash
terraform init
```

### 2. Ver el plan

```bash
terraform plan
```

### 3. Aplicar cambios

```bash
terraform apply
```

### 4. Ver outputs

```bash
terraform output
```

## 📝 Configuración

### Variables Principales

Las variables se definen en `variables.tf` con valores por defecto para dev.

**Modificar valores**:
Crear un archivo `terraform.tfvars`:

```hcl
project_name = "snail-bedrock"
environment  = "dev"

# Lambda timeouts
pdf_processor_timeout = 300  # 5 minutos
query_handler_timeout = 60   # 1 minuto

# Bedrock model (Haiku es más barato para dev)
bedrock_llm_model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# Logging (DEBUG en dev)
lambda_log_level = "DEBUG"
```

### Módulos Incluidos

1. **S3** - Buckets para documentos y backups
2. **IAM** - Roles y policies para Lambda/Step Functions
3. **Lambda** - Funciones de procesamiento
4. **Step Functions** - Workflow de orquestación
5. **EventBridge** - Triggers automáticos desde S3

## 📊 Recursos Creados

```
S3 Buckets:
├── snail-bedrock-dev-raw-documents        # PDFs originales
├── snail-bedrock-dev-processed-documents  # Documentos procesados
└── snail-bedrock-dev-chromadb-backup      # Backups de ChromaDB

Lambda Functions:
├── snail-bedrock-dev-pdf-processor   # Procesa PDFs → embeddings
└── snail-bedrock-dev-query-handler   # RAG queries

Step Functions:
└── snail-bedrock-dev-document-processing  # Workflow

EventBridge:
└── snail-bedrock-dev-s3-object-created    # Trigger S3 → Step Functions
```

## 🧪 Testing

### Subir un documento de prueba

```bash
# Obtener nombre del bucket
export RAW_BUCKET=$(terraform output -raw raw_documents_bucket)

# Subir PDF
aws s3 cp test.pdf s3://$RAW_BUCKET/

# Ver ejecuciones de Step Functions
export SF_ARN=$(terraform output -raw step_functions_arn)
aws stepfunctions list-executions --state-machine-arn $SF_ARN
```

### Hacer una query

```bash
# Obtener URL del query handler
export QUERY_URL=$(terraform output -raw query_handler_url)

# Hacer una query
curl -X POST $QUERY_URL \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Qué dice el documento sobre...?"}'
```

## 💰 Costos Estimados (DEV)

| Recurso | Costo/Mes |
|---------|-----------|
| S3 (<1GB) | $0.02 |
| Lambda (free tier) | $0.00 |
| Step Functions (Express) | $0.50 |
| Bedrock (Claude Haiku, 100 queries) | $0.50 |
| CloudWatch Logs | $0.05 |
| **TOTAL** | **~$1.07/mes** ✅ |

## 🧹 Limpiar Recursos

```bash
# Eliminar todos los recursos
terraform destroy

# Confirmar con: yes
```

⚠️ **Importante**: Los buckets de S3 deben estar vacíos antes de hacer destroy.

```bash
# Vaciar buckets
aws s3 rm s3://snail-bedrock-dev-raw-documents --recursive
aws s3 rm s3://snail-bedrock-dev-processed-documents --recursive
aws s3 rm s3://snail-bedrock-dev-chromadb-backup --recursive
```

## 📚 Siguiente Paso

Una vez desplegada la infraestructura, crear las **Lambda functions** en:
- `modules/aws-bedrock-agents/lambda-functions/pdf-processor/`
- `modules/aws-bedrock-agents/lambda-functions/query-handler/`

Ver documentación en `docs/aws-bedrock-agents/POC_SETUP.md`
