# Configuración POC Ultra-Económica (<$10/mes)

Guía para implementar un POC/Playground del módulo AWS Bedrock Agents manteniendo costos bajo $5-10 USD/mes.

## 🎯 Objetivo

Crear un agente de AI funcional para probar capacidades sin gastos significativos. Ideal para:
- Playground personal
- Proof of Concept (POC)
- Validación de arquitectura
- Testing de funcionalidad

## 💰 Costo Total Estimado: **$3-8/mes**

| Servicio | Configuración | Costo Mensual |
|----------|---------------|---------------|
| Bedrock (Claude Haiku) | 100 queries/mes | $0.50 |
| Vector Store (Pinecone Free) | Hasta 1M vectors | $0.00 |
| Lambda | Dentro de free tier | $0.00 |
| S3 | Dentro de free tier | $0.00 |
| Step Functions | Dentro de free tier | $0.00 |
| EventBridge | Dentro de free tier | $0.00 |
| **TOTAL** | | **~$0.50 - $2/mes** |

### Escenario con más uso:
- 500 queries/mes: $2.50
- 50 documentos/mes: +$0.50
- **Total: $3-5/mes**

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

### 2. Vector Store: Pinecone Free Tier

**Por qué Pinecone:**
- **Completamente GRATIS** hasta 1M vectors
- ~5,000 documentos de tamaño medio
- Suficiente para POC
- Fácil de implementar

**Alternativa (si Pinecone se queda corto):**
- FAISS local en Lambda: Gratis, solo pagas Lambda execution

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
┌─────────────────────────────────────┐
│  S3 Bucket (documentos)             │
│  - PDFs digitales únicamente        │
│  - No usar Textract (gratis)        │
└──────┬──────────────────────────────┘
       │ trigger
       ▼
┌─────────────────────────────────────┐
│  Lambda: PDF Processor              │
│  - PyPDF2/pdfplumber (gratis)       │
│  - Extrae texto                     │
│  - Chunking simple                  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Bedrock: Titan Embeddings          │
│  - $0.0001 por 1K tokens            │
│  - Genera vectors                   │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Pinecone Free Tier                 │
│  - 1M vectors gratis                │
│  - ~5K documentos                   │
└─────────────────────────────────────┘

 ┌──────────────────────────────────┐
 │  Query del Usuario               │
 └──────┬───────────────────────────┘
        │
        ▼
 ┌─────────────────────────────────┐
 │  Lambda: Query Handler          │
 │  1. Busca en Pinecone           │
 │  2. Llama Bedrock (Haiku)       │
 │  3. Retorna respuesta           │
 └─────────────────────────────────┘
```

## 📝 Configuración Paso a Paso

### Paso 1: Configurar Pinecone (Gratis)

```bash
# 1. Crear cuenta en Pinecone.io (free tier)
# 2. Crear API key
# 3. Guardar en AWS Secrets Manager

aws secretsmanager create-secret \
  --name snail-dev-pinecone-api-key \
  --secret-string '{"api_key":"tu-api-key"}'
```

### Paso 2: Configurar Terraform Variables

```hcl
# modules/aws-bedrock-agents/terraform/environments/dev/terraform.tfvars

environment = "dev"
project_name = "snail-poc"

# Usar Haiku en lugar de Sonnet
bedrock_model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# Sin OpenSearch - usar Pinecone
use_opensearch = false
vector_store_type = "pinecone"

# Minimal Lambda configuration
lambda_memory_mb = 512  # Mínimo necesario
lambda_timeout_seconds = 30

# S3 con lifecycle agresivo
s3_lifecycle_days_to_glacier = 7  # Mover a Glacier rápido

# Sin Textract
enable_textract = false
```

### Paso 3: Configurar Lambda para Pinecone

```python
# modules/aws-bedrock-agents/lambda-functions/pdf-processor/handler.py

import os
import boto3
from pinecone import Pinecone
from PyPDF2 import PdfReader
import json

# Inicializar Pinecone
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index = pc.Index("snail-poc")

# Inicializar Bedrock
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    # 1. Leer PDF desde S3
    s3 = boto3.client('s3')
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    obj = s3.get_object(Bucket=bucket, Key=key)
    pdf = PdfReader(obj['Body'])

    # 2. Extraer texto (GRATIS - no usar Textract)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()

    # 3. Chunking simple
    chunks = simple_chunk(text, chunk_size=1000)

    # 4. Generar embeddings con Titan (barato)
    vectors = []
    for i, chunk in enumerate(chunks):
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=json.dumps({"inputText": chunk})
        )
        embedding = json.loads(response['body'].read())['embedding']
        vectors.append({
            "id": f"{key}_{i}",
            "values": embedding,
            "metadata": {"text": chunk, "source": key}
        })

    # 5. Indexar en Pinecone (GRATIS)
    index.upsert(vectors=vectors)

    return {'statusCode': 200, 'body': 'Document processed'}

def simple_chunk(text, chunk_size=1000):
    """Simple chunking - sin dependencias externas"""
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
from pinecone import Pinecone
import json

pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
index = pc.Index("snail-poc")
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    query = event['query']

    # 1. Generar embedding de la query
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({"inputText": query})
    )
    query_embedding = json.loads(response['body'].read())['embedding']

    # 2. Buscar en Pinecone (GRATIS)
    results = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True
    )

    # 3. Construir contexto
    context = "\n\n".join([match['metadata']['text'] for match in results['matches']])

    # 4. Llamar a Haiku (BARATO)
    prompt = f"""Contexto: {context}

Pregunta: {query}

Responde basándote en el contexto proporcionado."""

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
            'sources': [m['metadata']['source'] for m in results['matches']]
        })
    }
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

- [ ] Crear cuenta Pinecone (free tier)
- [ ] Configurar API key en AWS Secrets Manager
- [ ] Modificar terraform.tfvars para usar Haiku
- [ ] Deshabilitar OpenSearch en configuración
- [ ] Implementar Lambdas con PyPDF2 (no Textract)
- [ ] Configurar S3 lifecycle policies agresivas
- [ ] Crear AWS Budget de $10/mes con alertas
- [ ] Usar Step Functions Express (no Standard)
- [ ] Documentar limitaciones del POC
- [ ] Testear con <20 documentos inicialmente

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

**Con esta configuración, puedes tener un agente AI funcional por menos de $5-10/mes.** 🎉
