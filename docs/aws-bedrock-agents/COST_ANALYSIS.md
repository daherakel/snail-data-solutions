# Análisis de Costos - AWS Bedrock AI Agents

Análisis detallado de costos para el módulo de agentes de AI con AWS Bedrock.

**Última actualización**: 2025-11-23
**Región**: us-east-1 (N. Virginia)

## Resumen Ejecutivo

| Escenario | Costo Mensual Estimado |
|-----------|------------------------|
| **Desarrollo/Testing** (bajo volumen) | **$10 - $50** |
| **Producción - Uso Ligero** (100 docs/mes, 500 queries/mes) | **$50 - $150** |
| **Producción - Uso Moderado** (500 docs/mes, 2,000 queries/mes) | **$200 - $400** |
| **Producción - Uso Intensivo** (2,000 docs/mes, 10,000 queries/mes) | **$800 - $1,500** |

## Desglose de Costos por Servicio

### 1. Amazon Bedrock (Modelos de IA)

**Claude Sonnet 4.5** (Recomendado para producción)
- Input tokens: **$3.00 por millón** ($0.003 por 1,000 tokens)
- Output tokens: **$15.00 por millón** ($0.015 por 1,000 tokens)

**Claude 3.7 Sonnet** (Alternativa económica)
- Input tokens: **$3.00 por millón**
- Output tokens: **$15.00 por millón**

**Con optimizaciones**:
- Prompt caching: **hasta 90% de ahorro**
- Batch processing: **50% de ahorro**

**Ejemplo práctico**:
- Query típica: 2,000 tokens input + 500 tokens output
- Costo por query: (2 × $0.003) + (0.5 × $0.015) = **$0.0135** (~1.4 centavos)
- 1,000 queries/mes: **$13.50**

**Free Tier**: No hay free tier permanente para Bedrock

---

### 2. Knowledge Bases for Amazon Bedrock

**Componentes de costo**:

**a) Embedding Model** (para vectorización)
- Amazon Titan Embeddings: **$0.0001 por 1,000 tokens**
- Cohere Embed: **$0.0001 por 1,000 tokens**

**b) Vector Store (OpenSearch Serverless)**
- OCU (OpenSearch Compute Units): **~$0.24/hora** ($175/mes por OCU)
- Storage: **$0.024 per GB-month**

**Ejemplo práctico**:
- 1,000 documentos × 2,000 tokens promedio = 2M tokens
- Embeddings: 2M × $0.0001/1K = **$0.20**
- Vector store (1 OCU mínimo): **$175/mes**
- Storage (100 MB vectores): **$0.002/mes**

**Costo base mensual Knowledge Base**: **~$175** (principalmente OpenSearch)

**Nota**: Este es el costo más significativo y constante, independiente del uso.

---

### 3. AWS Lambda

**Pricing**:
- Requests: **$0.20 por millón** (primeros 1M gratis/mes)
- Compute: **$0.0000166667 por GB-segundo** (primeros 400,000 GB-seg gratis/mes)

**Free Tier permanente**:
- 1 millón de requests/mes
- 400,000 GB-segundos/mes

**Ejemplo práctico** (PDF processor con 1GB RAM, 10 seg promedio):
- 100 documentos/mes × 10 seg × 1 GB = 1,000 GB-seg
- Dentro del free tier: **$0.00**
- Si excedes: 1,000 GB-seg × $0.0000166667 = **$0.017**

**Estimado mensual para volumen moderado**: **$0 - $5**

---

### 4. AWS Step Functions

**Standard Workflows**:
- **$0.025 por 1,000 state transitions**
- Free tier: 4,000 transitions/mes (permanente)

**Express Workflows** (alternativa para alto volumen):
- **$1.00 por millón de requests**
- Mejor para workflows <5 minutos

**Ejemplo práctico** (document ingestion con 8 estados):
- 100 documentos × 8 estados = 800 transitions
- Dentro del free tier: **$0.00**
- Si excedes: 800 transitions × $0.000025 = **$0.02**

**Estimado mensual**: **$0 - $2**

---

### 5. Amazon S3

**Standard Storage**:
- Primeros 50 TB: **$0.023 per GB/mes**
- Siguientes 450 TB: **$0.022 per GB/mes**

**S3 Intelligent-Tiering** (Recomendado):
- Mismo precio base pero auto-optimiza costos
- Mueve datos a tiers más baratos automáticamente

**S3 Glacier** (para archivos antiguos):
- **$0.0036 per GB/mes** (90x más barato)

**Requests**:
- PUT/POST: **$0.005 per 1,000 requests**
- GET: **$0.0004 per 1,000 requests**

**Ejemplo práctico**:
- 500 documentos × 5 MB promedio = 2.5 GB
- Storage Standard: 2.5 × $0.023 = **$0.058/mes**
- Requests (1,000 uploads): $0.005
- Con lifecycle a Glacier después de 90 días: **$0.01/mes**

**Estimado mensual**: **$1 - $20** (depende del volumen)

---

### 6. Amazon Textract (OCR)

**Detect Document Text API**:
- Primeros 1M pages: **$1.50 por 1,000 páginas**
- Después de 1M: **$0.60 por 1,000 páginas**

**Free Tier**:
- 1,000 páginas/mes por 3 meses (solo nuevos clientes)

**Ejemplo práctico**:
- 100 imágenes/PDF escaneados por mes
- 100 × $0.0015 = **$0.15/mes**

**Estimado mensual**: **$0.15 - $10** (solo si procesas imágenes/PDFs escaneados)

---

### 7. Amazon EventBridge

**Pricing**:
- Primeros 14 millones de eventos: **GRATIS**
- Después: **$1.00 por millón de eventos**

**Ejemplo práctico**:
- 1,000 documentos subidos a S3 = 1,000 eventos
- Dentro del free tier: **$0.00**

**Estimado mensual**: **$0.00** (para volúmenes normales)

---

## Escenarios de Uso y Costos

### Escenario 1: Desarrollo y Testing (Ambiente Dev)

**Uso mensual**:
- 50 documentos procesados
- 200 queries al agente
- Sin OCR (solo PDFs digitales)

| Servicio | Costo |
|----------|-------|
| Bedrock (queries) | $2.70 |
| Knowledge Base (embeddings) | $0.10 |
| Knowledge Base (OpenSearch) | $175.00 |
| Lambda | $0.00 (free tier) |
| Step Functions | $0.00 (free tier) |
| S3 | $0.50 |
| EventBridge | $0.00 (free tier) |
| **TOTAL** | **~$178/mes** |

**Optimización para dev**:
- Usar modelos más pequeños (Claude Haiku): **$0.25/1M input, $1.25/1M output**
- Apagar OpenSearch cuando no se use: **-$140/mes**
- **Costo optimizado dev**: **$10-$30/mes**

---

### Escenario 2: Producción - Uso Ligero

**Uso mensual**:
- 100 documentos/mes (50 PDFs digitales, 50 imágenes con OCR)
- 500 queries/mes
- Retención de 90 días

| Servicio | Costo |
|----------|-------|
| Bedrock (queries) | $6.75 |
| Knowledge Base (embeddings) | $0.20 |
| Knowledge Base (OpenSearch) | $175.00 |
| Lambda | $0.00 |
| Step Functions | $0.00 |
| S3 | $1.00 |
| Textract (OCR) | $0.75 |
| EventBridge | $0.00 |
| **TOTAL** | **~$184/mes** |

---

### Escenario 3: Producción - Uso Moderado

**Uso mensual**:
- 500 documentos/mes (mix de tipos)
- 2,000 queries/mes
- 30% con prompt caching (90% ahorro)

| Servicio | Costo |
|----------|-------|
| Bedrock (queries) | $27.00 |
| Bedrock (con caching) | $19.00 |
| Knowledge Base (embeddings) | $1.00 |
| Knowledge Base (OpenSearch 2 OCU) | $350.00 |
| Lambda | $2.00 |
| Step Functions | $0.10 |
| S3 (10 GB) | $2.50 |
| Textract | $3.75 |
| EventBridge | $0.00 |
| **TOTAL** | **~$378/mes** |

---

### Escenario 4: Producción - Uso Intensivo

**Uso mensual**:
- 2,000 documentos/mes
- 10,000 queries/mes
- Prompt caching + batch processing

| Servicio | Costo |
|----------|-------|
| Bedrock (queries optimizadas) | $75.00 |
| Knowledge Base (embeddings) | $4.00 |
| Knowledge Base (OpenSearch 4 OCU) | $700.00 |
| Lambda | $10.00 |
| Step Functions | $0.50 |
| S3 (40 GB + Glacier) | $10.00 |
| Textract | $15.00 |
| EventBridge | $0.00 |
| **TOTAL** | **~$814/mes** |

---

## Estrategias de Optimización de Costos

### 1. Knowledge Base / OpenSearch (Mayor costo)

**Problema**: OpenSearch Serverless cuesta ~$175/mes mínimo (1 OCU)

**Opciones**:
- ✅ **Alternativa**: Usar **Amazon Aurora PostgreSQL con pgvector** (~$50-80/mes)
- ✅ **Alternativa**: Usar **Pinecone** o **Weaviate** (free tier hasta cierto límite)
- ✅ Apagar en dev cuando no se use
- ✅ Usar OpenSearch solo en prod, alternativas en dev/staging

### 2. Bedrock Models

**Optimizaciones**:
- ✅ **Prompt Caching**: Ahorra 90% en tokens repetidos
- ✅ **Batch Processing**: Ahorra 50% para procesamiento no urgente
- ✅ **Modelo apropiado por caso**:
  - Queries simples: Claude Haiku ($0.25/$1.25 por millón) - **80% más barato**
  - Queries complejas: Claude Sonnet
  - Análisis profundo: Claude Opus (solo cuando necesario)

### 3. Lambda

**Optimizaciones**:
- ✅ Usar ARM64 (Graviton2): **20% más barato**
- ✅ Optimizar memoria: Solo usar lo necesario
- ✅ Batch processing: Procesar múltiples documentos por invocación

### 4. S3

**Optimizaciones**:
- ✅ **S3 Intelligent-Tiering**: Auto-optimiza costos
- ✅ **Lifecycle policies**:
  - 30 días: Standard → Infrequent Access (-46%)
  - 90 días: → Glacier (-84%)
  - 180 días: → Deep Archive (-96%)
- ✅ **Compression**: Comprimir documentos antes de almacenar

### 5. Textract

**Optimizaciones**:
- ✅ Solo usar para imágenes/PDFs escaneados
- ✅ Para PDFs digitales: usar PyPDF2/pdfplumber (gratis)
- ✅ Batch processing para ahorrar en Lambda

---

## Comparativa: OpenSearch vs Alternativas

| Vector Store | Costo Mínimo/Mes | Escalabilidad | Integración Bedrock |
|--------------|------------------|---------------|---------------------|
| **OpenSearch Serverless** | $175 (1 OCU) | ⭐⭐⭐⭐⭐ | Nativa |
| **Aurora PostgreSQL (pgvector)** | $50-80 | ⭐⭐⭐⭐ | Vía Lambda |
| **Pinecone** | Free hasta 1M vectors | ⭐⭐⭐⭐ | Vía Lambda |
| **Weaviate Cloud** | Free tier disponible | ⭐⭐⭐ | Vía Lambda |
| **FAISS (local/Lambda)** | Solo Lambda costs | ⭐⭐ | Vía Lambda |

**Recomendación**:
- **Dev/Staging**: Pinecone free tier o FAISS
- **Prod bajo volumen**: Aurora pgvector
- **Prod alto volumen**: OpenSearch Serverless

---

## Costo Total Estimado por Ambiente

| Ambiente | Configuración | Costo Mensual |
|----------|---------------|---------------|
| **Dev** | Haiku + Pinecone free + mínimo uso | **$10 - $30** |
| **Staging** | Sonnet + Aurora pgvector | **$80 - $120** |
| **Prod (ligero)** | Sonnet + Aurora pgvector + optimizaciones | **$120 - $200** |
| **Prod (moderado)** | Sonnet + OpenSearch (2 OCU) + caching | **$350 - $450** |
| **Prod (intensivo)** | Sonnet/Opus + OpenSearch (4 OCU) + todas optimizaciones | **$800 - $1,200** |

---

## Recomendaciones

### Fase 1: MVP / Proof of Concept
**Objetivo**: Minimizar costos, validar solución

**Stack recomendado**:
- Bedrock: Claude Haiku
- Vector store: Pinecone free tier o FAISS
- Solo ambiente dev
- Sin OCR (solo PDFs digitales)

**Costo estimado**: **$10-20/mes**

### Fase 2: Pilot con Cliente
**Objetivo**: Testing real, bajo volumen

**Stack recomendado**:
- Bedrock: Claude Sonnet con prompt caching
- Vector store: Aurora PostgreSQL pgvector
- Ambientes: dev + staging
- OCR selectivo

**Costo estimado**: **$100-150/mes**

### Fase 3: Producción
**Objetivo**: Escalabilidad y performance

**Stack recomendado**:
- Bedrock: Claude Sonnet 4.5 con todas las optimizaciones
- Vector store: OpenSearch Serverless (prod) + Aurora (staging)
- Ambientes: dev + staging + prod
- OCR completo

**Costo estimado**: **$400-800/mes** (según volumen)

---

## Monitoreo y Alertas de Costos

**Configurar**:
1. AWS Cost Explorer: Análisis de costos por servicio
2. AWS Budgets: Alertas cuando se excede presupuesto
3. CloudWatch Metrics: Monitoreo de uso
4. Tags obligatorios: `Environment`, `Project`, `CostCenter`

**Alertas sugeridas**:
- Alert at 50% of monthly budget
- Alert at 80% of monthly budget
- Alert at 100% of monthly budget
- Daily cost anomaly detection

---

## Fuentes

- [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [AWS Knowledge Bases Pricing](https://aws.amazon.com/bedrock/pricing/)
- [AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/)
- [AWS Step Functions Pricing](https://aws.amazon.com/step-functions/pricing/)
- [AWS S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [AWS Textract Pricing](https://aws.amazon.com/textract/pricing/)

---

**Conclusión**: El costo principal es el vector store (OpenSearch). Usando alternativas como Aurora pgvector o Pinecone en fases iniciales, puedes empezar con **$10-30/mes** y escalar según necesidad.
