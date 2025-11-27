# Terraform - DEV Environment

Configuración de Terraform para el ambiente de desarrollo del módulo AWS Bedrock Agents.

> 📖 **For complete deployment guide**, see **[DEPLOYMENT.md](../../../../../../docs/DEPLOYMENT.md)**

## 🚀 Quick Commands

```bash
# Initialize
terraform init

# Plan changes
terraform plan

# Apply infrastructure
terraform apply

# View outputs
terraform output

# Destroy (requires empty S3 buckets first)
terraform destroy
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

## 💰 Estimated Cost (DEV)

~$0.78/month with Titan Express | ~$3/month with Llama 3.3 70B

For detailed cost breakdown, see **[COST_AND_SCALING.md](../../../../../../docs/COST_AND_SCALING.md)**

---

**For testing, cleanup, and troubleshooting**, see **[DEPLOYMENT.md](../../../../../../docs/DEPLOYMENT.md)**
