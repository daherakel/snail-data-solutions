# Comparativa: Vector Databases para AWS Bedrock Agents

Análisis de las mejores opciones de bases de datos vectoriales para usar con AWS Bedrock.

## 🎯 Objetivo

Encontrar la mejor vector database que:
- ✅ Se integre bien con AWS Bedrock
- ✅ Tenga buen performance
- ✅ Sea económica para POC/Playground
- ✅ Escale para producción
- ✅ Preferiblemente open source o con free tier

## 📊 Comparativa Completa

| Vector DB | Tipo | Costo POC | Costo Prod | Performance | Integración Bedrock | Open Source | Recomendación |
|-----------|------|-----------|------------|-------------|---------------------|-------------|---------------|
| **Qdrant** | Self-hosted | $5-10 (EC2) | $20-100 | ⭐⭐⭐⭐⭐ | Vía Lambda | ✅ Sí | 🥇 **MEJOR OPCIÓN** |
| **Pinecone** | Managed SaaS | $0 (free tier) | $70-200 | ⭐⭐⭐⭐⭐ | Vía Lambda | ❌ No | 🥈 Excelente para POC |
| **Weaviate** | Híbrido | $0 (free tier) / $10 EC2 | $50-150 | ⭐⭐⭐⭐ | Vía Lambda | ✅ Sí | 🥉 Muy buena |
| **pgvector** | PostgreSQL | $15-30 (RDS) | $50-150 | ⭐⭐⭐ | Vía Lambda | ✅ Sí | 👍 Buena si ya usas Postgres |
| **ChromaDB** | Self-hosted | $0 (Lambda/local) | $20-80 | ⭐⭐⭐ | Nativa (Python) | ✅ Sí | 👍 Simple, buena para empezar |
| **Milvus** | Self-hosted | $15-30 | $100-300 | ⭐⭐⭐⭐⭐ | Vía Lambda | ✅ Sí | ⚠️ Complejo, overkill para POC |
| **OpenSearch** | AWS Native | $175 | $175-700 | ⭐⭐⭐⭐ | Nativa | ✅ Sí (fork) | ❌ MUY CARO |

## 🥇 Opción 1: Qdrant (RECOMENDADA)

### Por qué es la mejor:

**Ventajas:**
- ✅ **100% Open Source** (Apache 2.0)
- ✅ **Excelente performance**: Escrito en Rust, súper rápido
- ✅ **Fácil de usar**: API REST simple
- ✅ **Económico**: Self-hosted en EC2 pequeña
- ✅ **Escalable**: Diseñado para producción desde el inicio
- ✅ **Filtros avanzados**: Metadata filtering potente
- ✅ **Snapshots**: Backup y restore fácil
- ✅ **Cloud option**: Qdrant Cloud si quieres managed

**Desventajas:**
- ⚠️ Requiere gestionar infraestructura (pero simple)
- ⚠️ No tiene free tier managed (pero open source es gratis)

### Arquitectura con Qdrant:

```
┌──────────────┐
│ Documentos   │
│   (S3)       │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│ Lambda: PDF Processor        │
│ - Extrae texto (PyPDF2)      │
│ - Chunking                   │
│ - Llama Bedrock (embeddings) │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Qdrant (EC2 t3.small)        │
│ - Vector search              │
│ - Metadata filtering         │
│ - $10-15/mes                 │
└──────────────────────────────┘
       ▲
       │
┌──────┴───────────────────────┐
│ Lambda: Query Handler        │
│ - Busca en Qdrant            │
│ - Llama Bedrock (Claude)     │
└──────────────────────────────┘
```

### Costos Qdrant:

**POC/Playground:**
- EC2 t3.small (2 vCPU, 2GB RAM): **$15/mes**
- EBS 20GB: **$2/mes**
- **Total: ~$17/mes**

**Producción:**
- EC2 t3.medium (2 vCPU, 4GB RAM): **$30/mes**
- Con backups y HA: **$60-100/mes**

### Configuración Qdrant en EC2:

```bash
# User data script para EC2
#!/bin/bash
# Instalar Docker
yum update -y
yum install -y docker
service docker start

# Ejecutar Qdrant
docker run -d \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  --restart always \
  qdrant/qdrant

# Configurar security group para permitir 6333 solo desde Lambdas
```

### Código Python con Qdrant:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import boto3
import json

# Cliente Qdrant
qdrant = QdrantClient(
    url="http://ec2-instance-ip:6333",  # O usar URL interna de VPC
    timeout=30
)

# Cliente Bedrock
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# Crear colección (una vez)
qdrant.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=1536,  # Dimensión de Titan embeddings
        distance=Distance.COSINE
    )
)

# Indexar documento
def index_document(doc_id, chunks):
    points = []
    for i, chunk in enumerate(chunks):
        # Generar embedding con Bedrock
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=json.dumps({"inputText": chunk['text']})
        )
        embedding = json.loads(response['body'].read())['embedding']

        points.append(PointStruct(
            id=f"{doc_id}_{i}",
            vector=embedding,
            payload={
                "text": chunk['text'],
                "source": doc_id,
                "metadata": chunk.get('metadata', {})
            }
        ))

    qdrant.upsert(
        collection_name="documents",
        points=points
    )

# Buscar
def search(query_text, top_k=5):
    # Generar embedding de la query
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({"inputText": query_text})
    )
    query_embedding = json.loads(response['body'].read())['embedding']

    # Buscar en Qdrant
    results = qdrant.search(
        collection_name="documents",
        query_vector=query_embedding,
        limit=top_k,
        with_payload=True
    )

    return results
```

---

## 🥈 Opción 2: Pinecone (Excelente para POC)

### Por qué es buena:

**Ventajas:**
- ✅ **Free tier generoso**: 1M vectors gratis (~5K docs)
- ✅ **Zero ops**: Completamente managed
- ✅ **Muy rápido**: Latencia <100ms
- ✅ **Simple**: API super fácil de usar
- ✅ **Escalable**: Hasta billones de vectores

**Desventajas:**
- ❌ **No open source**: Vendor lock-in
- ❌ **Caro en producción**: $70-200+/mes después de free tier
- ❌ **Límites free tier**: Solo 1 índice, 1 namespace

### Costos Pinecone:

**Free Tier (Starter):**
- 1M vectors
- 1 índice
- 1 namespace
- **$0/mes** ✅

**Producción (Standard):**
- s1 pod (small): **$70/mes**
- p1 pod (performance): **$100/mes**
- p2 pod (high performance): **$200/mes**

### Código con Pinecone:

```python
from pinecone import Pinecone, ServerlessSpec
import boto3
import json

# Cliente Pinecone
pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])

# Crear índice (una vez)
pc.create_index(
    name="snail-docs",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(
        cloud='aws',
        region='us-east-1'
    )
)

index = pc.Index("snail-docs")

# Indexar
index.upsert(vectors=vectors)

# Buscar
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)
```

---

## 🥉 Opción 3: Weaviate (Open Source + Cloud)

### Por qué es interesante:

**Ventajas:**
- ✅ **Open Source** (BSD-3)
- ✅ **Free tier cloud**: 14 días gratis, luego opciones económicas
- ✅ **Self-hosted gratis**: En EC2/ECS
- ✅ **Vectorización integrada**: Puede usar Bedrock directamente
- ✅ **GraphQL API**: Queries muy expresivas
- ✅ **Hybrid search**: Vector + keyword combinados

**Desventajas:**
- ⚠️ Más complejo que Qdrant/Pinecone
- ⚠️ Requiere más recursos (RAM)

### Costos Weaviate:

**Cloud Free Tier:**
- Sandbox: **$0/mes** por 14 días
- Luego: $25-70/mes

**Self-hosted en EC2:**
- t3.medium: **$30/mes**
- t3.large (mejor performance): **$60/mes**

---

## 👍 Opción 4: pgvector (Si ya usas PostgreSQL)

### Por qué considerarla:

**Ventajas:**
- ✅ **100% Open Source**
- ✅ **PostgreSQL**: Si ya usas Postgres, reutilizas infra
- ✅ **ACID transactions**: Datos vectoriales + relacionales
- ✅ **Simple**: Solo una extensión de Postgres
- ✅ **RDS compatible**: Funciona en AWS RDS

**Desventajas:**
- ❌ **No tan rápido**: Para millones de vectores
- ❌ **Requiere tuning**: Índices HNSW, configuración

### Costos pgvector:

**RDS PostgreSQL:**
- db.t3.small: **$25/mes**
- db.t3.medium: **$50/mes**

**Aurora PostgreSQL:**
- Serverless v2: **$40-80/mes** (autoscaling)

---

## 👍 Opción 5: ChromaDB (Ultra simple)

### Por qué es útil:

**Ventajas:**
- ✅ **100% Open Source** (Apache 2.0)
- ✅ **Super simple**: API minimalista
- ✅ **Local development**: Perfecto para dev
- ✅ **Embeddings integrados**: Puede usar múltiples providers
- ✅ **Persistencia**: SQLite o DuckDB backend

**Desventajas:**
- ❌ **No diseñado para escala masiva**
- ❌ **Single-node**: No distribuido
- ❌ **Menos features**: Que Qdrant/Weaviate

### Costos ChromaDB:

**Local/Lambda:**
- En Lambda: **$0** (solo paga Lambda execution)
- En ECS Fargate: **$15-30/mes**

---

## 🚫 Opción a EVITAR: OpenSearch Serverless

**Por qué NO:**
- ❌ **Muy caro**: $175/mes mínimo (1 OCU)
- ❌ **Overkill**: Para solo vector search
- ❌ **Complejo**: Setup y configuración

**Única razón para usar:**
- Si necesitas full-text search + vector search combinados
- Si ya usas OpenSearch para otros propósitos

---

## 📋 Recomendación Final

### Para POC/Playground (<$10/mes):

**1ra opción: Pinecone Free Tier**
- ✅ Costo: $0
- ✅ Setup: 5 minutos
- ✅ Mantenimiento: 0
- ⚠️ Límite: 1M vectors (~5K docs)

### Para Producción Small (<$50/mes):

**1ra opción: Qdrant en EC2 t3.small**
- ✅ Costo: $15-20/mes
- ✅ Performance: Excelente
- ✅ Open Source: Sin vendor lock-in
- ✅ Escalable: Hasta millones de vectores

### Para Producción Medium ($50-150/mes):

**1ra opción: Qdrant en EC2 t3.medium + backup**
- ✅ Costo: $60-100/mes
- ✅ HA: Multi-AZ posible
- ✅ Performance: Muy buena
- ✅ Control total

**2da opción: Weaviate Cloud**
- ✅ Costo: $70-100/mes
- ✅ Managed: Zero ops
- ✅ Features avanzados

### Para Producción Large (>$150/mes):

**Qdrant Cloud o Weaviate Cloud**
- Managed service
- Soporte enterprise
- SLAs garantizados

---

## 🛠️ Stack Recomendado para Snail Data

### Fase 1: POC/Playground

```yaml
AI Model: AWS Bedrock (Claude Haiku)
Vector DB: Pinecone Free Tier
Processing: AWS Lambda + PyPDF2
Orchestration: Step Functions Express
Storage: S3
Cost: $3-8/mes ✅
```

### Fase 2: Cliente Pilot

```yaml
AI Model: AWS Bedrock (Claude Sonnet)
Vector DB: Qdrant (EC2 t3.small)
Processing: AWS Lambda + PyPDF2
Orchestration: Step Functions Express
Storage: S3 + Lifecycle
Cost: $30-50/mes
```

### Fase 3: Producción

```yaml
AI Model: AWS Bedrock (Claude Sonnet 4.5 + caching)
Vector DB: Qdrant (EC2 t3.medium) o Qdrant Cloud
Processing: AWS Lambda + opcional Textract
Orchestration: Step Functions Standard
Storage: S3 Intelligent Tiering
Monitoring: CloudWatch + custom dashboards
Cost: $120-300/mes (según volumen)
```

---

## 🔧 Decisión por Criterios

| Criterio | Mejor Opción |
|----------|--------------|
| **Más barato POC** | Pinecone Free Tier |
| **Mejor performance** | Qdrant |
| **Más fácil setup** | Pinecone |
| **Open source** | Qdrant / Weaviate / ChromaDB |
| **Escalabilidad** | Qdrant / Milvus |
| **Cero mantenimiento** | Pinecone / Weaviate Cloud |
| **Mejor relación costo/performance** | Qdrant self-hosted |
| **Integración con PostgreSQL** | pgvector |
| **Simplicidad extrema** | ChromaDB |

---

## 💡 Mi Recomendación Personal

**Para Snail Data Solutions:**

1. **Empezar con Pinecone Free Tier** ($0/mes)
   - Valida el concepto rápido
   - Cero setup, cero ops
   - 1M vectors suficiente para POC

2. **Migrar a Qdrant self-hosted** cuando:
   - Superes 1M vectors
   - Necesites más control
   - Quieras reducir costos long-term
   - **Costo: $15-30/mes**

3. **Considerar Qdrant Cloud** si:
   - El cliente necesita SLA
   - No quieres gestionar infraestructura
   - Necesitas soporte enterprise
   - **Costo: $70-150/mes**

**NUNCA usar OpenSearch Serverless** a menos que:
- Ya tengas OpenSearch para otros usos
- Necesites full-text + vector search combinados
- El presupuesto no sea problema

---

## 📚 Recursos

- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Pinecone Docs](https://docs.pinecone.io/)
- [Weaviate Docs](https://weaviate.io/developers/weaviate)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [ChromaDB Docs](https://docs.trychroma.com/)
