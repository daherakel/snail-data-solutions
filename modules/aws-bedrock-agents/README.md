# AWS Bedrock AI Agents Module

Módulo completo para crear agentes de AI usando AWS Bedrock que procesan y responden consultas sobre documentos PDF usando RAG (Retrieval Augmented Generation).

## 🎯 Características

- ✅ **Procesamiento automático de PDFs** con EventBridge + Step Functions + Lambda
- ✅ **Vector database gratuita** con ChromaDB (open source)
- ✅ **Embeddings con Bedrock Titan** para búsqueda semántica
- ✅ **RAG con Claude** para respuestas contextuales
- ✅ **Infraestructura completa con Terraform** (modular y multi-ambiente)
- ✅ **Scripts de deployment y testing** listos para usar
- ✅ **Costo optimizado**: <$2/mes para POC

## 📁 Estructura del Módulo

```
modules/aws-bedrock-agents/
├── infrastructure/
│   └── terraform/
│       ├── modules/                    # Módulos reusables
│       │   ├── s3/                    # Buckets para documentos
│       │   ├── iam/                   # Roles y policies
│       │   ├── lambda/                # Funciones Lambda
│       │   ├── step-functions/        # Workflows
│       │   └── eventbridge/           # Event rules
│       └── environments/              # Configuraciones por ambiente
│           ├── dev/                   # Desarrollo
│           ├── staging/               # Staging
│           └── prod/                  # Producción
│
├── lambda-functions/
│   ├── pdf-processor/                 # Procesa PDFs → embeddings
│   │   ├── handler.py
│   │   └── requirements.txt
│   ├── query-handler/                 # RAG queries
│   │   ├── handler.py
│   │   └── requirements.txt
│   └── lambda-layer-chromadb/         # Layer compartido
│       ├── requirements.txt
│       └── build-layer.sh
│
├── scripts/
│   ├── deploy.sh                      # Deployment completo
│   ├── upload-document.sh             # Subir y procesar PDF
│   ├── test-query.sh                  # Testear queries
│   └── cleanup.sh                     # Limpiar recursos
│
└── README.md                          # Este archivo
```

## 🚀 Quick Start

### Prerrequisitos

1. **Terraform** >= 1.0
   ```bash
   brew install terraform
   ```

2. **AWS CLI** configurado
   ```bash
   aws configure
   aws sts get-caller-identity  # Verificar
   ```

3. **Docker** (para crear Lambda Layer)
   ```bash
   docker --version
   ```

### Deployment Automático

```bash
# Desde el directorio del módulo
cd modules/aws-bedrock-agents

# Ejecutar deployment completo
./scripts/deploy.sh dev
```

Este script hará:
1. ✅ Crear Lambda Layer de ChromaDB
2. ✅ Desplegar infraestructura con Terraform
3. ✅ Mostrar outputs y próximos pasos

### Deployment Manual (paso por paso)

#### Paso 1: Crear Lambda Layer

```bash
cd lambda-functions/lambda-layer-chromadb

# Construir layer
./build-layer.sh

# Publicar en AWS
aws lambda publish-layer-version \
  --layer-name snail-bedrock-chromadb \
  --zip-file fileb://chromadb-layer.zip \
  --compatible-runtimes python3.11 python3.12 \
  --region us-east-1
```

#### Paso 2: Deploy Terraform

```bash
cd infrastructure/terraform/environments/dev

# Inicializar
terraform init

# Ver plan
terraform plan

# Aplicar
terraform apply
```

#### Paso 3: Obtener Outputs

```bash
terraform output

# Outputs disponibles:
# - raw_documents_bucket
# - query_handler_url
# - step_functions_arn
```

## 📊 Arquitectura

```
┌─────────────────┐
│   PDF Upload    │
│   (S3 Bucket)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  EventBridge    │◄─── Detecta .pdf
│     Rule        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step Functions  │
│   Workflow      │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│ Lambda: PDF Processor        │
│ 1. Extrae texto (PyPDF2)     │
│ 2. Chunking                  │
│ 3. Embeddings (Titan)        │
│ 4. Guarda en ChromaDB        │
│ 5. Backup a S3               │
└──────────────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ ChromaDB (persistido en S3)  │
│ - Vector search              │
│ - Cosine similarity          │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Lambda: Query Handler        │
│ 1. Query → embedding         │
│ 2. Busca en ChromaDB         │
│ 3. RAG con Claude            │
│ 4. Respuesta contextual      │
└──────────────────────────────┘
```

## 🧪 Testing

### 1. Subir un documento

```bash
# Usando script
./scripts/upload-document.sh dev mi-documento.pdf

# O manualmente
export BUCKET=$(cd infrastructure/terraform/environments/dev && terraform output -raw raw_documents_bucket)
aws s3 cp test.pdf s3://$BUCKET/
```

### 2. Monitorear procesamiento

```bash
export SF_ARN=$(cd infrastructure/terraform/environments/dev && terraform output -raw step_functions_arn)

# Ver ejecuciones
aws stepfunctions list-executions --state-machine-arn $SF_ARN

# Ver logs
aws logs tail /aws/lambda/snail-bedrock-dev-pdf-processor --follow
```

### 3. Hacer queries

```bash
# Usando script
./scripts/test-query.sh dev "¿De qué trata el documento?"

# O manualmente con curl
export QUERY_URL=$(cd infrastructure/terraform/environments/dev && terraform output -raw query_handler_url)

curl -X POST $QUERY_URL \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuáles son los puntos principales?"}'
```

## 💰 Costos Estimados

### POC/Development (~$1-2/mes)

| Servicio | Configuración | Costo/Mes |
|----------|---------------|-----------|
| S3 | <1GB storage | $0.02 |
| Lambda | Free tier (100 docs/mes) | $0.00 |
| Step Functions | Express, <1000 ejecuciones | $0.50 |
| Bedrock Titan Embeddings | 100 docs × 10 chunks | $0.01 |
| Bedrock Claude Haiku | 100 queries | $0.50 |
| CloudWatch Logs | 7 días retención | $0.05 |
| **TOTAL** | | **~$1.08/mes** ✅ |

### Producción Ligera (~$30-50/mes)

| Servicio | Configuración | Costo/Mes |
|----------|---------------|-----------|
| S3 | 10GB storage + requests | $0.50 |
| Lambda | 10,000 ejecuciones | $2.00 |
| Step Functions | 5,000 ejecuciones | $12.50 |
| Bedrock Embeddings | 1,000 docs | $0.30 |
| Bedrock Claude Sonnet | 1,000 queries | $15.00 |
| CloudWatch | 30 días retención | $2.00 |
| **TOTAL** | | **~$32.30/mes** |

## 🔧 Configuración Avanzada

### Variables de Terraform (dev)

Editar `infrastructure/terraform/environments/dev/terraform.tfvars`:

```hcl
# Proyecto
project_name = "snail-bedrock"
environment  = "dev"

# Lambda timeouts
pdf_processor_timeout = 300  # 5 minutos
query_handler_timeout = 60   # 1 minuto

# Bedrock models
bedrock_llm_model_id = "anthropic.claude-3-haiku-20240307-v1:0"  # Haiku (barato)
# bedrock_llm_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"  # Sonnet (mejor)

# RAG configuration
max_context_chunks = 5  # Chunks a incluir en contexto

# Logging
lambda_log_level = "DEBUG"  # DEBUG, INFO, WARNING, ERROR

# Function URL (para testing directo)
create_function_url = true
```

### Cambiar a Claude Sonnet (producción)

```hcl
# En terraform.tfvars
bedrock_llm_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

# Aplicar cambios
terraform apply
```

## 📚 Documentación Adicional

- **Arquitectura detallada**: `../../docs/aws-bedrock-agents/README.md`
- **Análisis de costos**: `../../docs/aws-bedrock-agents/COST_ANALYSIS.md`
- **Setup de POC**: `../../docs/aws-bedrock-agents/POC_SETUP.md`
- **Comparativa de Vector DBs**: `../../docs/aws-bedrock-agents/VECTOR_DB_COMPARISON.md`
- **Terraform dev**: `infrastructure/terraform/environments/dev/README.md`

## 🧹 Cleanup

Para eliminar todos los recursos:

```bash
# Usando script (recomendado)
./scripts/cleanup.sh dev

# O manualmente
cd infrastructure/terraform/environments/dev

# Vaciar buckets primero
aws s3 rm s3://$(terraform output -raw raw_documents_bucket) --recursive
aws s3 rm s3://$(terraform output -raw processed_documents_bucket) --recursive
aws s3 rm s3://$(terraform output -raw chromadb_backup_bucket) --recursive

# Destruir infraestructura
terraform destroy
```

## 🔒 Seguridad

### Implementado

- ✅ IAM roles con principio de least privilege
- ✅ Buckets S3 con encriptación (AES256)
- ✅ Buckets S3 sin acceso público
- ✅ VPC para Lambdas (opcional, no implementado por defecto para reducir costos)
- ✅ CloudWatch logging habilitado

### Recomendaciones para Producción

1. **Habilitar VPC** para Lambdas
2. **Usar AWS Secrets Manager** para API keys (si se migra a Pinecone/Qdrant Cloud)
3. **Habilitar AWS X-Ray** para tracing
4. **Implementar WAF** si se expone Function URL públicamente
5. **Configurar alertas** de CloudWatch
6. **Habilitar backup automático** de S3 con cross-region replication

## 🐛 Troubleshooting

### Lambda timeout al procesar PDFs grandes

```hcl
# Aumentar timeout en terraform.tfvars
pdf_processor_timeout = 600  # 10 minutos
pdf_processor_memory = 2048  # 2GB

terraform apply
```

### ChromaDB no carga en Lambda

```bash
# Verificar que el layer existe
aws lambda list-layers --region us-east-1

# Reconstruir layer
cd lambda-functions/lambda-layer-chromadb
rm chromadb-layer.zip
./build-layer.sh
```

### Query handler retorna "No hay documentos"

```bash
# Verificar que ChromaDB tiene datos
aws s3 ls s3://$(terraform output -raw chromadb_backup_bucket)/

# Verificar logs de pdf-processor
aws logs tail /aws/lambda/snail-bedrock-dev-pdf-processor --since 1h
```

## 🚦 Próximos Pasos

1. **Subir documentos de prueba** y validar procesamiento
2. **Testear queries** con diferentes tipos de preguntas
3. **Monitorear costos** en AWS Cost Explorer
4. **Optimizar chunking** según tipo de documentos
5. **Agregar soporte** para más formatos (Word, Excel, imágenes)
6. **Implementar UI web** para interacción con el agente

## 📞 Soporte

Para issues o preguntas:
- Revisar logs de CloudWatch
- Verificar IAM permissions
- Consultar documentación en `docs/aws-bedrock-agents/`

---

**Desarrollado por**: Snail Data Solutions
**Versión**: 1.0.0
**Última actualización**: 2025-01-24
