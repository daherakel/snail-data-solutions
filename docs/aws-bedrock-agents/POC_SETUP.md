# Configuración POC Ultra-Económica (<$10/mes)

Guía para implementar un POC/Playground del módulo AWS Bedrock Agents manteniendo costos bajo $5-10 USD/mes.

## 🎯 Objetivo

Crear un agente de AI funcional para probar capacidades sin gastos significativos. Ideal para:
- Playground personal
- Proof of Concept (POC)
- Validación de arquitectura
- Testing de funcionalidad

## 💰 Costo Total Estimado: **$0.50-3/mes**

| Servicio | Configuración | Costo Mensual |
|----------|---------------|---------------|
| Bedrock (Claude Haiku) | 100 queries/mes | $0.50 |
| Vector Store (ChromaDB) | Open source, sin límites | $0.00 |
| Lambda | Dentro de free tier | $0.00 |
| S3 | Backup ChromaDB (<1GB) | $0.02 |
| Step Functions | Dentro de free tier | $0.00 |
| EventBridge | Dentro de free tier | $0.00 |
| **TOTAL** | | **~$0.52/mes** ✅ |

### Escenario con más uso:
- 500 queries/mes: $2.50
- 50 documentos/mes: +$0.02 (S3)
- **Total: $2.52/mes** ✅

## ⚙️ Stack Recomendado para POC

### 1. Modelo de IA: Claude Haiku

**Por qué Haiku:**
- **80% más barato** que Sonnet
- Input: $0.25 por millón tokens (vs $3.00 Sonnet)
- Output: $1.25 por millón tokens (vs $15.00 Sonnet)
- Suficientemente capaz para POC y testing

**Ejemplo de costos:**
- Query típica: 2K input + 500 output tokens
- Costo por query: $0.00088 (~0.09 centavos)
- 100 queries: **$0.088** (~9 centavos)
- 1,000 queries: **$0.88** (~88 centavos)

### 2. Vector Store: ChromaDB (Open Source)

**Por qué ChromaDB:**
- **100% GRATIS** - Open source (Apache 2.0)
- **Sin límites** de vectores
- Súper fácil de implementar (API simple)
- Corre en Lambda (free tier)
- Persistencia en S3 ($0.02/mes)
- Migración fácil a ECS/Fargate para producción

**Alternativas gratuitas:**
- FAISS: Más rápido, más bajo nivel
- Qdrant local: Para desarrollo en tu laptop
- Ver `docs/aws-bedrock-agents/FREE_VECTOR_DB_OPTIONS.md` para detalles

### 3. Procesamiento: Lambda + PyPDF2

**Sin Textract:**
- Usar librerías Python gratuitas:
  - **PyPDF2** para PDFs digitales
  - **pdfplumber** para PDFs complejos
  - **python-docx** para Word docs
  - **pandas** para CSV/Excel

**Costos Lambda:**
- Free tier: 1M requests/mes + 400K GB-segundos/mes
- Para POC: **$0.00** (dentro de free tier)

### 4. Orquestación: Step Functions Express

**Por qué Express:**
- $1.00 por millón de requests (vs $25.00 Standard)
- Free tier: Primeras 4,000 transiciones/mes
- Para POC: **$0.00** (dentro de free tier)

### 5. Storage: S3 Standard con Lifecycle

**Optimización:**
- Free tier: 5GB storage primeros 12 meses
- Lifecycle: Mover a Glacier después de 30 días
- Para POC (<1GB data): **$0.00 - $0.10/mes**

## 🏗️ Arquitectura Simplificada POC

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  S3 Bucket (documentos)                 │
│  - PDFs digitales únicamente            │
│  - No usar Textract (gratis)            │
└──────┬──────────────────────────────────┘
       │ trigger
       ▼
┌──────────────────────────────────────────┐
│  Lambda: PDF Processor                   │
│  ┌────────────────────────────────────┐  │
│  │ ChromaDB (in-memory)               │  │
│  │ - Carga desde S3                   │  │
│  │ - Procesa + indexa                 │  │
│  │ - Guarda a S3                      │  │
│  └────────────────────────────────────┘  │
│  - PyPDF2 (gratis)                       │
│  - Bedrock embeddings                    │
└──────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  S3 Bucket (chroma_backup/)             │
│  - ChromaDB data comprimida             │
│  - $0.02/mes                            │
└─────────────────────────────────────────┘
       ▲
       │
┌──────┴────────────────────────────────────┐
│  Lambda: Query Handler                    │
│  ┌────────────────────────────────────┐   │
│  │ ChromaDB (in-memory)               │   │
│  │ - Carga desde S3                   │   │
│  │ - Busca vectores                   │   │
│  │ - Retorna top-K                    │   │
│  └────────────────────────────────────┘   │
│  - Llama Bedrock (Haiku)                  │
│  - Retorna respuesta                      │
└───────────────────────────────────────────┘
```

## 📝 Configuración Paso a Paso

### Paso 1: Instalar ChromaDB Localmente (Testing)

```bash
# Instalar para testing local
pip install chromadb

# Crear layer para Lambda
mkdir -p lambda-layers/chromadb/python
pip install chromadb -t lambda-layers/chromadb/python/
cd lambda-layers/chromadb
zip -r chromadb-layer.zip python/

# Subir layer a AWS
aws lambda publish-layer-version \
  --layer-name chromadb-layer \
  --zip-file fileb://chromadb-layer.zip \
  --compatible-runtimes python3.11 \
  --region us-east-1
```

### Paso 2: Configurar Terraform Variables

```hcl
# modules/aws-bedrock-agents/terraform/environments/dev/terraform.tfvars

environment = "dev"
project_name = "snail-poc"

# Usar Haiku en lugar de Sonnet
bedrock_model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# Sin OpenSearch - usar ChromaDB en Lambda
use_opensearch = false
vector_store_type = "chromadb"  # Open source, gratis

# Lambda configuration para ChromaDB
lambda_memory_mb = 512  # ChromaDB en memoria
lambda_timeout_seconds = 60  # Tiempo para cargar/guardar S3
lambda_ephemeral_storage_mb = 1024  # /tmp para ChromaDB data

# S3 para backup de ChromaDB
create_chroma_backup_bucket = true

# Sin Textract
enable_textract = false
```

### Paso 3: Configurar Lambda con ChromaDB

```python
# modules/aws-bedrock-agents/lambda-functions/pdf-processor/handler.py

import os
import boto3
import chromadb
from chromadb.config import Settings
from PyPDF2 import PdfReader
from io import BytesIO
import json
import tarfile

# Clientes AWS
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# Bucket para backup de ChromaDB
CHROMA_BACKUP_BUCKET = os.environ.get('CHROMA_BACKUP_BUCKET', 'snail-chroma-backup')
CHROMA_BACKUP_KEY = 'chroma_data.tar.gz'

def lambda_handler(event, context):
    # 1. Cargar ChromaDB existente desde S3 (si existe)
    chroma_client = load_chroma_from_s3()

    # 2. Obtener o crear colección
    collection = chroma_client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"}
    )

    # 3. Leer PDF desde S3
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    obj = s3.get_object(Bucket=bucket, Key=key)
    pdf = PdfReader(BytesIO(obj['Body'].read()))

    # 4. Extraer texto (GRATIS - PyPDF2)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()

    # 5. Chunking simple
    chunks = simple_chunk(text, chunk_size=500)

    # 6. Generar embeddings y agregar a ChromaDB
    for i, chunk in enumerate(chunks):
        # Generar embedding con Bedrock
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=json.dumps({"inputText": chunk})
        )
        embedding = json.loads(response['body'].read())['embedding']

        # Agregar a ChromaDB
        collection.add(
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source": key, "chunk_id": i}],
            ids=[f"{key}_{i}"]
        )

    # 7. Persistir ChromaDB a S3
    persist_chroma_to_s3(chroma_client)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Document processed',
            'source': key,
            'chunks': len(chunks)
        })
    }

def load_chroma_from_s3():
    """Carga ChromaDB desde S3 o crea nuevo"""
    try:
        # Descargar backup
        s3.download_file(
            CHROMA_BACKUP_BUCKET,
            CHROMA_BACKUP_KEY,
            '/tmp/chroma_data.tar.gz'
        )

        # Extraer
        with tarfile.open('/tmp/chroma_data.tar.gz', 'r:gz') as tar:
            tar.extractall('/tmp/')

        print("ChromaDB loaded from S3")
    except Exception as e:
        print(f"No existing ChromaDB found: {e}")

    # Inicializar cliente
    return chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="/tmp/chroma"
    ))

def persist_chroma_to_s3(chroma_client):
    """Guarda ChromaDB a S3"""
    # Persistir localmente
    chroma_client.persist()

    # Comprimir
    with tarfile.open('/tmp/chroma_data.tar.gz', 'w:gz') as tar:
        tar.add('/tmp/chroma', arcname='chroma')

    # Subir a S3
    s3.upload_file(
        '/tmp/chroma_data.tar.gz',
        CHROMA_BACKUP_BUCKET,
        CHROMA_BACKUP_KEY
    )

    print("ChromaDB persisted to S3")

def simple_chunk(text, chunk_size=500):
    """Chunking simple sin dependencias externas"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1

        if current_length >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
```

### Paso 4: Lambda para Queries

```python
# modules/aws-bedrock-agents/lambda-functions/query-handler/handler.py

import os
import boto3
import chromadb
from chromadb.config import Settings
import json
import tarfile

# Clientes AWS
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

CHROMA_BACKUP_BUCKET = os.environ.get('CHROMA_BACKUP_BUCKET', 'snail-chroma-backup')
CHROMA_BACKUP_KEY = 'chroma_data.tar.gz'

def lambda_handler(event, context):
    query = event.get('query')

    if not query:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Query parameter required'})
        }

    # 1. Cargar ChromaDB desde S3
    chroma_client = load_chroma_from_s3()
    collection = chroma_client.get_collection(name="documents")

    # 2. Generar embedding de la query
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({"inputText": query})
    )
    query_embedding = json.loads(response['body'].read())['embedding']

    # 3. Buscar en ChromaDB (GRATIS)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=['documents', 'metadatas', 'distances']
    )

    # 4. Construir contexto
    if not results['documents'][0]:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'No documents found in database'})
        }

    context = "\n\n".join(results['documents'][0])

    # 5. Llamar a Claude Haiku (BARATO)
    prompt = f"""Contexto de documentos:

{context}

Pregunta del usuario: {query}

Por favor, responde la pregunta basándote únicamente en el contexto proporcionado. Si la información no está en el contexto, indícalo claramente."""

    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        })
    )

    answer = json.loads(response['body'].read())['content'][0]['text']

    return {
        'statusCode': 200,
        'body': json.dumps({
            'answer': answer,
            'sources': [m['source'] for m in results['metadatas'][0]],
            'confidence_scores': results['distances'][0]
        })
    }

def load_chroma_from_s3():
    """Carga ChromaDB desde S3"""
    # Descargar
    s3.download_file(
        CHROMA_BACKUP_BUCKET,
        CHROMA_BACKUP_KEY,
        '/tmp/chroma_data.tar.gz'
    )

    # Extraer
    with tarfile.open('/tmp/chroma_data.tar.gz', 'r:gz') as tar:
        tar.extractall('/tmp/')

    # Inicializar cliente
    return chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="/tmp/chroma"
    ))
```

## 🚫 Qué NO Hacer en POC

Para mantener costos bajos:

❌ **NO usar OpenSearch Serverless** ($175/mes mínimo)
✅ Usar Pinecone free tier o FAISS

❌ **NO usar Claude Sonnet/Opus** para testing
✅ Usar Claude Haiku (80% más barato)

❌ **NO usar Textract** para PDFs digitales
✅ Usar PyPDF2/pdfplumber (gratis)

❌ **NO procesar imágenes/PDFs escaneados** en POC
✅ Solo PDFs digitales inicialmente

❌ **NO dejar Step Functions en Standard**
✅ Usar Express workflows

❌ **NO mantener documentos en S3 Standard indefinidamente**
✅ Lifecycle a Glacier después de 7-30 días

## 📊 Monitoreo de Costos

### Configurar Alertas

```bash
# AWS Budget para alertas
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file://budget.json

# budget.json
{
  "BudgetName": "snail-poc-monthly-budget",
  "BudgetLimit": {
    "Amount": "10",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

### Tags para Tracking

Todos los recursos deben tener:
```hcl
tags = {
  Project     = "snail-poc"
  Environment = "dev"
  CostCenter  = "playground"
  Owner       = "tu-nombre"
}
```

## 🎓 Limitaciones del POC

**Documenta claramente que este POC NO es para producción:**

1. **Escalabilidad limitada**: Pinecone free tier → máximo ~5K docs
2. **Performance**: Haiku es más rápido pero menos preciso que Sonnet
3. **Sin OCR**: Solo PDFs digitales (no imágenes/escaneados)
4. **Sin alta disponibilidad**: Configuración mínima
5. **Sin monitoring avanzado**: Solo CloudWatch básico

## 🚀 Migración a Producción

Cuando el POC valide la solución, migrar a:

**Modelo**: Haiku → Sonnet 4.5
**Vector Store**: Pinecone free → Aurora pgvector ($50-80/mes) o OpenSearch ($175+/mes)
**OCR**: Agregar Textract para documentos escaneados
**Monitoring**: CloudWatch dashboards + alertas
**Ambientes**: dev + staging + prod separados

**Costo producción**: $120-450/mes (según volumen)

## 📝 Checklist de Setup

- [ ] Instalar ChromaDB localmente para testing
- [ ] Crear Lambda layer con ChromaDB
- [ ] Crear bucket S3 para backup de ChromaDB
- [ ] Modificar terraform.tfvars para usar Haiku + ChromaDB
- [ ] Implementar Lambdas con ChromaDB + PyPDF2
- [ ] Configurar Lambda con 512MB RAM y 60s timeout
- [ ] Configurar S3 lifecycle policies para backups
- [ ] Crear AWS Budget de $5/mes con alertas
- [ ] Usar Step Functions Express (no Standard)
- [ ] Documentar limitaciones del POC
- [ ] Testear con 5-10 documentos inicialmente
- [ ] Verificar costos en AWS Cost Explorer después de 1 semana

## 💡 Tips para Minimizar Costos Aún Más

1. **Cachear resultados**: No re-procesar documentos
2. **Batch processing**: Procesar múltiples docs juntos
3. **Prompt caching**: Reusar prompts comunes (90% ahorro)
4. **Lazy indexing**: Solo indexar cuando sea necesario
5. **Limitar tamaño de chunks**: Menos tokens = menos costo
6. **Usar S3 Intelligent Tiering**: Auto-optimiza costos
7. **Apagar recursos cuando no se usen**: Lambdas solo ejecutan cuando se invocan

## ⚠️ IMPORTANTE

Este setup está optimizado para **PLAYGROUND/POC únicamente**.

Para uso en producción o con clientes, consultar `COST_ANALYSIS.md` para configuraciones apropiadas.

---

**Con esta configuración, puedes tener un agente AI funcional por menos de $3/mes.** 🎉

## 📚 Recursos Adicionales

- **Opciones Gratuitas Detalladas**: `docs/aws-bedrock-agents/FREE_VECTOR_DB_OPTIONS.md`
- **Comparativa Vector DBs**: `docs/aws-bedrock-agents/VECTOR_DB_COMPARISON.md`
- **Análisis Completo de Costos**: `docs/aws-bedrock-agents/COST_ANALYSIS.md`
- **ChromaDB Docs**: https://docs.trychroma.com/
- **AWS Bedrock Pricing**: https://aws.amazon.com/bedrock/pricing/
