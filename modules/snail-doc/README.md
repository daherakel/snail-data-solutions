# 🐌 Snail Doc - AI Document Assistant

Asistente inteligente de documentos usando AWS Bedrock con RAG (Retrieval Augmented Generation). Procesa PDFs y responde consultas usando búsqueda semántica con FAISS y modelos de Claude.

## 🎯 Características

- ✅ **Procesamiento automático de PDFs** con S3 triggers + Lambda
- ✅ **Vector search con FAISS** (Facebook AI Similarity Search) - rápido y eficiente
- ✅ **Embeddings con Bedrock Titan** para búsqueda semántica
- ✅ **RAG con Claude** para respuestas contextuales
- ✅ **Infraestructura completa con Terraform** (modular y multi-ambiente)
- ✅ **Lambda Layer optimizado** (38 MB vs 113 MB con ChromaDB)
- ✅ **Costo optimizado**: ~$0.78/mes para POC, ~$19/mes para producción
- ✅ **Multi-tenant y replicable**: Sistema de configuración por cliente
- ✅ **Integraciones extensibles**: Slack, Teams, WhatsApp, Instagram (plantillas)
- ✅ **Casos de uso configurables**: Documentos, atención al cliente, Google Sheets (plantillas)

## 🔄 Replicabilidad

Este módulo está diseñado para ser completamente **replicable para múltiples clientes/tenants**. Cada cliente puede tener su propia configuración con:

- **Personalización del agente**: Personalidad (warm, professional, technical, friendly), tono, idioma
- **Casos de uso específicos**: Documentos, atención al cliente, Google Sheets, etc.
- **Integraciones configuradas**: Slack, Teams, WhatsApp, Instagram
- **Modelos independientes**: Configuración de modelos por cliente
- **Prompts personalizados**: Sistema modular de prompts

### Quick Start para Nuevo Tenant

```bash
# 1. Ver guía completa de replicación
cat REPLICABILITY.md

# 2. Usar template de setup
cat templates/tenant-setup.md

# 3. Deploy para nuevo tenant
./scripts/deploy-tenant.sh {TENANT_ID} dev
```

**📚 Documentación de Replicabilidad:**
- **[REPLICABILITY.md](REPLICABILITY.md)** - Guía completa paso a paso
- **[DEPLOYMENT_TEMPLATE.md](DEPLOYMENT_TEMPLATE.md)** - Template para documentar deployments
- **[templates/](templates/)** - Templates para nuevos clientes

## 📁 Estructura del Módulo

```
modules/snail-doc/
├── shared/                            # Código compartido reutilizable
│   ├── config/                        # Sistema de configuración multi-tenant
│   │   ├── tenant-config.yaml        # Configuración por tenant
│   │   ├── model-config.yaml         # Configuración de modelos
│   │   └── integration-config.yaml   # Configuración de integraciones
│   ├── prompts/                      # Sistema de prompts modular
│   │   ├── base_prompts.py          # Prompts base configurables
│   │   ├── document_assistant.py    # Prompts para documentos
│   │   └── customer_support.py      # Prompts para soporte (template)
│   ├── integrations/                 # Abstracción de integraciones (futuro)
│   ├── use_cases/                    # Abstracción de casos de uso (futuro)
│   ├── tools/                        # Sistema de herramientas (futuro)
│   └── utils/                        # Utilidades compartidas
│       └── config_loader.py         # Cargador de configuración
│
├── infrastructure/
│   └── terraform/
│       ├── modules/                    # Módulos reusables
│       │   ├── s3/                    # Buckets para documentos
│       │   ├── iam/                   # Roles y policies
│       │   ├── lambda/                # Funciones Lambda
│       │   ├── step-functions/        # Workflows
│       │   ├── eventbridge/           # Event rules
│       │   └── integrations/          # Módulos de integraciones (futuro)
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
│   ├── slack-handler/                 # Integración Slack
│   │   ├── handler.py
│   │   └── requirements.txt
│   └── lambda-layer-chromadb/         # Layer compartido (FAISS + PyPDF2)
│       ├── requirements.txt
│       └── build-layer.sh
│
├── config/                            # Configuraciones por tenant/caso de uso
│   ├── tenants/                       # Config por cliente (futuro)
│   └── use-cases/                     # Config por caso de uso (futuro)
│
├── templates/                         # Templates para nuevos clientes
│   ├── tenant-setup.md               # Guía de setup rápido
│   └── terraform.tfvars.example      # Template de variables Terraform
│
├── scripts/
│   ├── deploy.sh                      # Deployment completo
│   ├── upload-document.sh             # Subir y procesar PDF
│   ├── test-query.sh                  # Testear queries
│   ├── cleanup.sh                     # Limpiar recursos
│   ├── validate-config.sh             # Validar configuración (futuro)
│   ├── test-integration.sh            # Test de integración (futuro)
│   └── deploy-tenant.sh               # Deploy para nuevo tenant (futuro)
│
├── docs/
│   └── integrations/                  # Documentación por integración (futuro)
│
├── REPLICABILITY.md                   # Guía completa de replicación
├── DEPLOYMENT_TEMPLATE.md             # Template para documentar deployments
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
cd modules/snail-doc

# Ejecutar deployment completo
./scripts/deploy.sh dev
```

Este script hará:
1. ✅ Crear Lambda Layer de FAISS
2. ✅ Desplegar infraestructura con Terraform
3. ✅ Configurar S3 triggers automáticos
4. ✅ Mostrar outputs y próximos pasos

### Deployment Manual (paso por paso)

#### Paso 1: Crear Lambda Layer

```bash
cd lambda-functions/lambda-layer-chromadb

# Construir layer (FAISS + PyPDF2 + numpy)
./build-layer.sh

# Publicar en AWS
aws lambda publish-layer-version \
  --layer-name snail-bedrock-dev-faiss-layer \
  --zip-file fileb://faiss-layer.zip \
  --compatible-runtimes python3.11 \
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
│ 4. Indexa en FAISS           │
│ 5. Persiste a S3             │
└──────────────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ FAISS Index (persistido S3)  │
│ - faiss_index.bin            │
│ - faiss_metadata.pkl         │
│ - L2 distance search         │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│ Lambda: Query Handler        │
│ 1. Query → embedding (Titan) │
│ 2. FAISS similarity search   │
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

Nuestra implementación con **FAISS** es **90% más económica** que alternativas con OpenSearch (~$175/mes).

| Scenario | Monthly Cost | Use Case |
|----------|-------------|----------|
| **POC/Development** | **$0.78 - $3** | Testing, playground |
| **Production Light** | **$15 - $30** | 100-500 queries/month |
| **Production Moderate** | **$120 - $200** | 1K-5K queries/month |
| **Production Intensive** | **$450 - $800** | 10K+ queries/month |

**💡 Key Cost Driver**: Vector store choice. FAISS (current) = $0.00/month vs OpenSearch = $175/month.

**📊 For detailed cost breakdown and optimization strategies**, see **[COST_AND_SCALING.md](../../docs/COST_AND_SCALING.md)**

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

### Guías Principales
- **[Deployment Guide](../../docs/DEPLOYMENT.md)** - Guía completa de deployment (dev, staging, prod)
- **[Cost & Scaling](../../docs/COST_AND_SCALING.md)** - Análisis de costos y estrategias de escalamiento
- **[Project README](../../README.md)** - Visión general del proyecto
- **[Frontend Documentation](frontend/README.md)** - Next.js UI documentation

### Referencias Técnicas
- **[Terraform Dev Environment](infrastructure/terraform/environments/dev/README.md)** - Configuración específica de dev
- **[Archived Docs](../../docs/archive/)** - Evaluaciones históricas (ChromaDB, vector DB comparisons)

### Replicabilidad y Multi-Tenant
- **[REPLICABILITY.md](REPLICABILITY.md)** - Guía completa para replicar el módulo
- **[DEPLOYMENT_TEMPLATE.md](DEPLOYMENT_TEMPLATE.md)** - Template para documentar deployments de tenants
- **[Templates](templates/)** - Templates para setup rápido de nuevos clientes

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

### FAISS Layer no carga en Lambda

```bash
# Verificar que el layer existe
aws lambda list-layers --region us-east-1

# Reconstruir layer
cd lambda-functions/lambda-layer-chromadb
rm faiss-layer.zip
./build-layer.sh
```

### Query handler retorna "No hay documentos"

```bash
# Verificar que FAISS index existe en S3
aws s3 ls s3://$(terraform output -raw chromadb_backup_bucket)/
# Debe mostrar: faiss_index.bin y faiss_metadata.pkl

# Verificar logs de pdf-processor
aws logs tail /aws/lambda/snail-bedrock-dev-pdf-processor --since 1h
```

### S3 trigger no dispara automáticamente

```bash
# Verificar configuración de notificaciones S3
aws s3api get-bucket-notification-configuration \
  --bucket $(terraform output -raw raw_documents_bucket)

# Verificar permisos de Lambda
aws lambda get-policy --function-name snail-bedrock-dev-pdf-processor
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
**Versión**: 1.1.0 (FAISS migration)
**Última actualización**: 2025-11-24

## 📝 Changelog

### v1.1.0 (2025-11-24)
- ✅ Migrado de ChromaDB a FAISS para vector search
- ✅ Lambda Layer reducido de 113 MB a 38 MB (66% reducción)
- ✅ S3 triggers directos en lugar de EventBridge + Step Functions
- ✅ CloudWatch Alarms configuradas para monitoring
- ✅ Costos reducidos: $0.78/mes (POC), $19/mes (prod)
- ✅ Testing end-to-end validado (100% accuracy)

### v1.0.0 (2025-01-24)
- Versión inicial con ChromaDB
