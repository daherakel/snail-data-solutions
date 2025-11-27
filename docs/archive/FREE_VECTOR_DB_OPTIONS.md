# Opciones 100% Gratuitas de Vector Databases

Bases de datos vectoriales que puedes usar **sin costo** para playground/POC.

## 🎯 Objetivo: $0 en Vector Database

Para mantener el costo total del POC en $3-5/mes (solo Bedrock), necesitamos una vector DB **completamente gratis**.

## 🆓 Opciones 100% Gratuitas

### 🥇 Opción 1: ChromaDB (RECOMENDADA para POC)

**Por qué es la mejor opción gratuita:**
- ✅ **100% Gratis**: Open source (Apache 2.0)
- ✅ **Sin límites**: Millones de vectores sin pagar
- ✅ **Super simple**: API minimalista, 3 líneas de código
- ✅ **En Lambda**: Corre en memoria, sin infra extra
- ✅ **Persistencia**: Opcional con EFS o S3
- ✅ **Producción**: Puede escalar con ECS/Fargate después

**Desventajas:**
- ⚠️ No distribuido (single-node)
- ⚠️ Menos features que Qdrant/Weaviate
- ⚠️ Performance moderado para >10M vectores

#### Arquitectura con ChromaDB:

```
┌─────────────────────────────────────────┐
│  Lambda: Document Processor             │
│  ┌───────────────────────────────────┐  │
│  │ ChromaDB (in-memory)              │  │
│  │ - Carga colección desde S3        │  │
│  │ - Procesa documento                │  │
│  │ - Guarda a S3 después             │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  S3 Bucket    │
            │ chroma_data/  │
            └───────────────┘
                    ▲
                    │
┌─────────────────────────────────────────┐
│  Lambda: Query Handler                  │
│  ┌───────────────────────────────────┐  │
│  │ ChromaDB (in-memory)              │  │
│  │ - Carga colección desde S3        │  │
│  │ - Busca vectores                  │  │
│  │ - Retorna resultados              │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

#### Código ChromaDB en Lambda:

```python
# lambda-functions/pdf-processor/handler.py
import chromadb
from chromadb.config import Settings
import boto3
import json
import os

# Cliente S3
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# ChromaDB client (persistencia en /tmp/)
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="/tmp/chroma"
))

def lambda_handler(event, context):
    # 1. Cargar colección existente desde S3 (si existe)
    try:
        s3.download_file(
            'snail-chroma-backup',
            'chroma_data.tar.gz',
            '/tmp/chroma_data.tar.gz'
        )
        # Extraer
        import tarfile
        with tarfile.open('/tmp/chroma_data.tar.gz', 'r:gz') as tar:
            tar.extractall('/tmp/')
    except:
        print("No existing collection, creating new")

    # 2. Obtener o crear colección
    collection = chroma_client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"}
    )

    # 3. Procesar documento
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Extraer texto del PDF
    obj = s3.get_object(Bucket=bucket, Key=key)
    text = extract_text_from_pdf(obj['Body'])  # PyPDF2

    # Chunking simple
    chunks = simple_chunk(text, chunk_size=500)

    # 4. Generar embeddings con Bedrock y agregar a ChromaDB
    for i, chunk in enumerate(chunks):
        # Embedding
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

    # 5. Persistir a S3
    chroma_client.persist()

    # Comprimir y subir
    import tarfile
    with tarfile.open('/tmp/chroma_data.tar.gz', 'w:gz') as tar:
        tar.add('/tmp/chroma', arcname='chroma')

    s3.upload_file(
        '/tmp/chroma_data.tar.gz',
        'snail-chroma-backup',
        'chroma_data.tar.gz'
    )

    return {'statusCode': 200, 'body': 'Success'}

def extract_text_from_pdf(pdf_bytes):
    from PyPDF2 import PdfReader
    from io import BytesIO

    pdf = PdfReader(BytesIO(pdf_bytes.read()))
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

def simple_chunk(text, chunk_size=500):
    words = text.split()
    chunks = []
    current = []
    length = 0

    for word in words:
        current.append(word)
        length += len(word) + 1
        if length >= chunk_size:
            chunks.append(' '.join(current))
            current = []
            length = 0

    if current:
        chunks.append(' '.join(current))

    return chunks
```

```python
# lambda-functions/query-handler/handler.py
import chromadb
from chromadb.config import Settings
import boto3
import json

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    query = event['query']

    # 1. Cargar ChromaDB desde S3
    s3.download_file(
        'snail-chroma-backup',
        'chroma_data.tar.gz',
        '/tmp/chroma_data.tar.gz'
    )

    import tarfile
    with tarfile.open('/tmp/chroma_data.tar.gz', 'r:gz') as tar:
        tar.extractall('/tmp/')

    # 2. Inicializar ChromaDB
    chroma_client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="/tmp/chroma"
    ))

    collection = chroma_client.get_collection(name="documents")

    # 3. Generar embedding de la query
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({"inputText": query})
    )
    query_embedding = json.loads(response['body'].read())['embedding']

    # 4. Buscar en ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=['documents', 'metadatas', 'distances']
    )

    # 5. Construir contexto y consultar Bedrock
    context = "\n\n".join(results['documents'][0])

    prompt = f"""Contexto: {context}

Pregunta: {query}

Responde basándote en el contexto."""

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
            'sources': [m['source'] for m in results['metadatas'][0]]
        })
    }
```

#### Costos ChromaDB:

| Componente | Costo |
|-----------|-------|
| ChromaDB | **$0** (open source) |
| Lambda (dentro free tier) | **$0** |
| S3 backup (<1GB) | **$0.02/mes** |
| **TOTAL Vector DB** | **~$0** |

**Costo total POC con ChromaDB:**
- Bedrock (Haiku, 500 queries): $2-3/mes
- ChromaDB + Lambda: $0
- S3: $0.02/mes
- **TOTAL: $2-3/mes** ✅

---

### 🥈 Opción 2: FAISS (Facebook AI Similarity Search)

**Por qué es buena:**
- ✅ **100% Gratis**: Open source (MIT)
- ✅ **Muy rápido**: Optimizado por Meta
- ✅ **Battle-tested**: Usado en producción por Meta
- ✅ **Flexible**: Múltiples algoritmos de índices
- ✅ **En Lambda**: Funciona perfectamente

**Desventajas:**
- ⚠️ Más bajo nivel que ChromaDB (más código)
- ⚠️ Sin metadata filtering nativo
- ⚠️ Solo vectores (no almacena documentos)

#### Código FAISS en Lambda:

```python
# lambda-functions/pdf-processor/handler.py
import faiss
import numpy as np
import boto3
import json
import pickle

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    # 1. Cargar índice FAISS existente desde S3 (si existe)
    try:
        s3.download_file('snail-faiss-backup', 'index.faiss', '/tmp/index.faiss')
        s3.download_file('snail-faiss-backup', 'metadata.pkl', '/tmp/metadata.pkl')

        index = faiss.read_index('/tmp/index.faiss')
        with open('/tmp/metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
    except:
        # Crear nuevo índice
        dimension = 1536  # Titan embeddings
        index = faiss.IndexFlatL2(dimension)
        metadata = []

    # 2. Procesar documento
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    obj = s3.get_object(Bucket=bucket, Key=key)
    text = extract_text_from_pdf(obj['Body'])
    chunks = simple_chunk(text, chunk_size=500)

    # 3. Generar embeddings y agregar a FAISS
    vectors = []
    for i, chunk in enumerate(chunks):
        response = bedrock.invoke_model(
            modelId='amazon.titan-embed-text-v1',
            body=json.dumps({"inputText": chunk})
        )
        embedding = json.loads(response['body'].read())['embedding']
        vectors.append(embedding)

        # Agregar metadata
        metadata.append({
            "text": chunk,
            "source": key,
            "chunk_id": i
        })

    # Agregar vectores a FAISS
    vectors_np = np.array(vectors).astype('float32')
    index.add(vectors_np)

    # 4. Guardar a S3
    faiss.write_index(index, '/tmp/index.faiss')
    with open('/tmp/metadata.pkl', 'wb') as f:
        pickle.dump(metadata, f)

    s3.upload_file('/tmp/index.faiss', 'snail-faiss-backup', 'index.faiss')
    s3.upload_file('/tmp/metadata.pkl', 'snail-faiss-backup', 'metadata.pkl')

    return {'statusCode': 200, 'body': 'Success'}
```

```python
# lambda-functions/query-handler/handler.py
import faiss
import numpy as np
import boto3
import json
import pickle

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    query = event['query']

    # 1. Cargar FAISS desde S3
    s3.download_file('snail-faiss-backup', 'index.faiss', '/tmp/index.faiss')
    s3.download_file('snail-faiss-backup', 'metadata.pkl', '/tmp/metadata.pkl')

    index = faiss.read_index('/tmp/index.faiss')
    with open('/tmp/metadata.pkl', 'rb') as f:
        metadata = pickle.load(f)

    # 2. Generar embedding de la query
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({"inputText": query})
    )
    query_embedding = json.loads(response['body'].read())['embedding']
    query_vector = np.array([query_embedding]).astype('float32')

    # 3. Buscar en FAISS
    k = 5  # Top 5 results
    distances, indices = index.search(query_vector, k)

    # 4. Obtener resultados
    results = []
    for idx in indices[0]:
        if idx < len(metadata):  # Verificar que exista
            results.append(metadata[idx])

    # 5. Construir contexto y consultar Bedrock
    context = "\n\n".join([r['text'] for r in results])

    prompt = f"""Contexto: {context}

Pregunta: {query}

Responde basándote en el contexto."""

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
            'sources': [r['source'] for r in results]
        })
    }
```

#### Costos FAISS:

**Idéntico a ChromaDB: ~$0**

---

### 🥉 Opción 3: Qdrant Local (en Docker localmente)

**Para desarrollo local:**
- ✅ **Gratis**: Correr en tu laptop
- ✅ **Full features**: Todas las capacidades
- ✅ **Fácil**: Docker compose
- ✅ **Testing**: Perfecto para dev

**Desventajas:**
- ❌ No para producción (en tu máquina)
- ❌ Necesitas tenerlo corriendo localmente

#### Setup Qdrant local:

```bash
# docker-compose.yml
version: '3'
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage
```

```bash
docker-compose up -d
```

**Costo: $0** (corre en tu máquina)

---

### 🥉 Opción 4: Weaviate Embedded

**Weaviate en modo embedded:**
- ✅ **Gratis**: No necesita servidor
- ✅ **Simple**: Corre in-process
- ✅ **Features completos**: Igual que Weaviate Cloud

**Desventajas:**
- ⚠️ Solo para desarrollo/testing
- ⚠️ Datos en memoria (no persistente por defecto)

```python
import weaviate
from weaviate.embedded import EmbeddedOptions

# Iniciar Weaviate embedded
client = weaviate.Client(
    embedded_options=EmbeddedOptions()
)
```

---

## 📊 Comparativa de Opciones Gratuitas

| Vector DB | Setup | Performance | Producción | Recomendación |
|-----------|-------|-------------|------------|---------------|
| **ChromaDB** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 🥇 **MEJOR para POC** |
| **FAISS** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 🥈 Si necesitas max performance |
| **Qdrant local** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ | Solo desarrollo local |
| **Weaviate embedded** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | Solo desarrollo local |

---

## 🎯 Recomendación Final para POC Gratis

### Stack Completo 100% Gratuito (casi):

```yaml
AI Model: AWS Bedrock (Claude Haiku)
Vector DB: ChromaDB en Lambda ✅ GRATIS
Processing: AWS Lambda + PyPDF2 ✅ Free tier
Storage: S3 ✅ Free tier
Orchestration: Step Functions Express ✅ Free tier

Costo Total: $2-3/mes
└─ Solo Bedrock (100 queries/mes)
```

### Costo Breakdown Ultra-Económico:

| Servicio | Configuración | Costo/Mes |
|----------|---------------|-----------|
| **Bedrock** | Claude Haiku, 100 queries | $0.50 |
| **ChromaDB** | Open source, en Lambda | $0.00 |
| **Lambda** | Free tier (1M requests) | $0.00 |
| **S3** | <1GB backup ChromaDB | $0.02 |
| **Step Functions** | Express, free tier | $0.00 |
| **EventBridge** | <14M eventos | $0.00 |
| **TOTAL** | | **$0.52/mes** ✅ |

**Con uso moderado (500 queries/mes):**
- Bedrock: $2.50
- Resto: $0.02
- **Total: $2.52/mes** ✅

---

## 🛠️ Implementación Recomendada

### Paso 1: Elegir ChromaDB

**Por qué:**
- API super simple (3 líneas para buscar)
- Funciona perfecto en Lambda
- Zero configuración
- Migración fácil a ECS si crece

### Paso 2: Lambda Layer para ChromaDB

```bash
# Crear layer
mkdir python
pip install chromadb -t python/
zip -r chromadb-layer.zip python/

# Subir a AWS Lambda Layer
aws lambda publish-layer-version \
    --layer-name chromadb \
    --zip-file fileb://chromadb-layer.zip \
    --compatible-runtimes python3.11
```

### Paso 3: Lambda con 512MB RAM

```yaml
# lambda configuration
Runtime: Python 3.11
Memory: 512 MB  # ChromaDB en memoria
Timeout: 30s
Layers: chromadb-layer
Environment:
  BEDROCK_MODEL_ID: anthropic.claude-3-haiku-20240307-v1:0
```

### Paso 4: Persistencia S3

```python
# Función helper para persistir
def persist_chroma_to_s3(chroma_client, bucket, key):
    chroma_client.persist()

    # Comprimir
    import tarfile
    with tarfile.open('/tmp/chroma.tar.gz', 'w:gz') as tar:
        tar.add('/tmp/chroma', arcname='chroma')

    # Subir
    s3.upload_file('/tmp/chroma.tar.gz', bucket, key)

def load_chroma_from_s3(bucket, key):
    import tarfile

    # Descargar
    s3.download_file(bucket, key, '/tmp/chroma.tar.gz')

    # Extraer
    with tarfile.open('/tmp/chroma.tar.gz', 'r:gz') as tar:
        tar.extractall('/tmp/')
```

---

## 🚀 Migración a Producción

Cuando el POC crezca, migrar a:

**Opción 1: Qdrant en EC2** ($15-20/mes)
- Mejor performance
- Sin límites
- Same API concept

**Opción 2: ChromaDB en ECS Fargate** ($20-30/mes)
- Persistent
- Mejor para múltiples usuarios concurrentes
- Escalable

**Opción 3: Managed (Qdrant Cloud/Pinecone)** ($70+/mes)
- Zero ops
- SLA
- Soporte

---

## ✅ Checklist POC Gratis

- [ ] Instalar ChromaDB localmente para testing
- [ ] Crear Lambda layer con ChromaDB
- [ ] Implementar PDF processor con ChromaDB
- [ ] Implementar query handler
- [ ] Configurar S3 bucket para backup
- [ ] Testear con 5-10 documentos
- [ ] Verificar costos en AWS Cost Explorer
- [ ] Documentar limitaciones (single-user, no HA, etc.)

---

**Con ChromaDB tu POC cuesta menos de $3/mes y es 100% funcional.** 🎉
