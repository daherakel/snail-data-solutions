# Cost Analysis & Scaling - Snail Doc

Análisis completo de costos y estrategias de escalamiento para Snail Doc (asistente AI de documentos).

**Última actualización**: 2025-11-26
**Región de referencia**: us-east-1 (N. Virginia)
**Implementación actual**: **FAISS**-based RAG (Lambda layer)

---

## 📊 Executive Summary

| Scenario | Monthly Cost | Best For |
|----------|-------------|----------|
| **POC/Development** | **$0.78 - $3** | Testing, playground, proof of concept |
| **Production Light** | **$15 - $30** | Small projects, 100-500 queries/month |
| **Production Moderate** | **$120 - $200** | Medium projects, 1,000-5,000 queries/month |
| **Production Intensive** | **$450 - $800** | Large projects, 10,000+ queries/month |

### Key Cost Driver

❗ **Important**: Our current implementation uses **FAISS (Lambda layer)**, which eliminates the traditional $175/month OpenSearch cost. This makes the system **90% cheaper** than Knowledge Bases-based implementations.

---

## 💰 Cost Breakdown by Service

### 1. Amazon Bedrock (LLM Models)

#### Llama 3.3 70B (Current - Cost-Optimized)
- **Input**: $0.00099 per 1K tokens
- **Output**: $0.00099 per 1K tokens

**Example Cost**:
- Typical query: 2,000 input + 500 output tokens
- Cost per query: (2 × $0.00099) + (0.5 × $0.00099) = **$0.0025** (~0.25 centavos)
- 1,000 queries/month: **$2.50**

#### Titan Text Express (Budget Alternative)
- **Input**: $0.0002 per 1K tokens
- **Output**: $0.0006 per 1K tokens

**Example Cost**:
- Same query: (2 × $0.0002) + (0.5 × $0.0006) = **$0.0007**
- 1,000 queries/month: **$0.70**

#### Claude 3.5 Sonnet (Premium Quality)
- **Input**: $3.00 per 1M tokens ($0.003 per 1K)
- **Output**: $15.00 per 1M tokens ($0.015 per 1K)

**Example Cost**:
- Same query: (2 × $0.003) + (0.5 × $0.015) = **$0.0135**
- 1,000 queries/month: **$13.50**

**With prompt caching**: Up to **90% savings** on repeated context

---

### 2. Vector Store (FAISS - Lambda Layer)

**Current Implementation**: FAISS embedded in Lambda

#### Costs:
- **Storage (S3)**: $0.023 per GB/month
  - 1,000 documents (100MB vectors): **$0.002/month**
  - 10,000 documents (1GB vectors): **$0.023/month**

- **Lambda compute**: Included in Lambda pricing below
  - No separate vector database cost ✅
  - No minimum monthly charge ✅

**Total Vector Store Cost**: **$0.00 - $0.10/month** (just S3 backup)

#### Comparison with Alternatives:

| Vector Store | Monthly Cost | Our Choice |
|--------------|--------------|------------|
| **FAISS (Lambda)** | $0.00 - $0.10 | ✅ Current |
| OpenSearch Serverless | $175+ (1 OCU minimum) | ❌ Too expensive |
| Aurora pgvector | $50-80 | 🔄 Alternative for scale |
| Pinecone | Free tier → $70/month | 🔄 Alternative option |

**Why FAISS**:
- Zero recurring cost (vs $175/month OpenSearch)
- Scales with Lambda automatically
- Simple S3 backup strategy
- Fast enough for <50K documents
- Easy migration path to managed services

---

### 3. Embedding Model (Amazon Titan Embed)

**Pricing**: $0.0001 per 1,000 tokens

**Example Cost**:
- 1,000 documents × 2,000 tokens average = 2M tokens
- Embeddings cost: 2M × $0.0001/1K = **$0.20**

**Monthly estimate**: $0.20 - $5.00 (depends on document ingestion rate)

---

### 4. AWS Lambda

**Pricing**:
- **Requests**: $0.20 per million (first 1M free/month)
- **Compute**: $0.0000166667 per GB-second
- **Free Tier** (permanent): 1M requests + 400K GB-seconds/month

**Example Cost** (1GB RAM Lambda):
- `pdf-processor`: 100 docs/month × 10 sec × 1GB = 1,000 GB-sec → **$0.00** (within free tier)
- `query-handler`: 1,000 queries/month × 2 sec × 1GB = 2,000 GB-sec → **$0.00** (within free tier)

**Monthly estimate**: $0 - $10 (most usage covered by free tier)

---

### 5. DynamoDB

**Pricing**:
- **On-Demand**:
  - Write: $1.25 per million
  - Read: $0.25 per million
- **Storage**: $0.25 per GB/month

**Example Cost**:
- 1,000 queries cached: 1,000 writes + 500 reads
- Writes: 1K × $0.00000125 = $0.00125
- Reads: 500 × $0.00000025 = $0.000125
- Storage (10MB): $0.0025

**Monthly estimate**: $0.25 - $5.00

---

### 6. Amazon S3

**Standard Storage**: $0.023 per GB/month

**Example Cost**:
- 500 documents × 5MB average = 2.5GB
- Storage: 2.5 × $0.023 = **$0.058/month**
- Requests (1,000 uploads): $0.005

**With lifecycle policies** (move to Glacier after 90 days):
- Standard (0-90 days): $0.058
- Glacier (90+ days): $0.009 (90% cheaper)

**Monthly estimate**: $1 - $20

---

### 7. EventBridge

**Pricing**: First 14 million events **FREE**, then $1.00 per million

**Example Cost**:
- 1,000 documents uploaded = 1,000 events
- Within free tier: **$0.00**

**Monthly estimate**: $0.00

---

## 💸 Complete Cost Scenarios

### Scenario 1: POC/Development (~$0.78/month)

**Usage**:
- 50 queries/month
- 10 documents processed/month
- Only digital PDFs (no OCR)

| Service | Configuration | Cost |
|---------|--------------|------|
| Bedrock (Titan Express) | 50 queries | $0.35 |
| FAISS (S3 backup) | 10MB vectors | $0.00 |
| Embeddings (Titan) | 10 docs | $0.04 |
| Lambda | Within free tier | $0.00 |
| DynamoDB | Minimal usage | $0.25 |
| S3 | 50MB storage | $0.001 |
| EventBridge | 10 events | $0.00 |
| **TOTAL** | | **~$0.78/month** ✅ |

---

### Scenario 2: Production Light (~$15/month)

**Usage**:
- 500 queries/month
- 50 documents/month
- Digital PDFs

| Service | Configuration | Cost |
|---------|--------------|------|
| Bedrock (Llama 3.3 70B) | 500 queries | $1.25 |
| FAISS (S3 backup) | 100MB vectors | $0.002 |
| Embeddings (Titan) | 50 docs | $0.20 |
| Lambda | Light usage | $2.00 |
| DynamoDB | 500 cached queries | $1.00 |
| S3 | 250MB storage | $0.01 |
| EventBridge | 50 events | $0.00 |
| **TOTAL** | | **~$4.50/month** ✅ |

**With Claude 3.5 Sonnet** (better quality): **~$15/month**

---

### Scenario 3: Production Moderate (~$120/month)

**Usage**:
- 5,000 queries/month
- 200 documents/month
- Mixed PDF types
- Prompt caching enabled (30% of queries)

| Service | Configuration | Cost |
|---------|--------------|------|
| Bedrock (Claude 3.5 Sonnet) | 5,000 queries | $67.50 |
| Bedrock (with 30% caching) | Optimized | $47.25 |
| FAISS (S3 backup) | 500MB vectors | $0.01 |
| Embeddings (Titan) | 200 docs | $0.80 |
| Lambda | Moderate usage | $10.00 |
| DynamoDB | 5K cached queries | $10.00 |
| S3 | 1GB storage | $0.50 |
| EventBridge | 200 events | $0.00 |
| **TOTAL** | | **~$70/month** ✅ |

---

### Scenario 4: Production Intensive (~$450/month)

**Usage**:
- 20,000 queries/month
- 1,000 documents/month
- Advanced optimizations

| Service | Configuration | Cost |
|---------|--------------|------|
| Bedrock (Claude 3.5 Sonnet) | 20K queries optimized | $200.00 |
| FAISS (S3 backup) | 2GB vectors | $0.046 |
| Embeddings (Titan) | 1,000 docs | $4.00 |
| Lambda | Heavy usage | $50.00 |
| DynamoDB | 20K cached queries | $50.00 |
| S3 | 5GB storage + lifecycle | $5.00 |
| CloudWatch | Enhanced monitoring | $10.00 |
| **TOTAL** | | **~$320/month** ✅ |

---

## 📈 Scaling Strategies

### When to Scale: Decision Matrix

| Metric | POC | Light | Moderate | Intensive |
|--------|-----|-------|----------|-----------|
| Queries/month | <100 | 100-1K | 1K-10K | 10K+ |
| Documents | <50 | 50-500 | 500-5K | 5K+ |
| Users | 1-5 | 5-50 | 50-500 | 500+ |
| Response time SLA | None | <5s | <2s | <1s |
| **Recommended model** | Titan | Llama 3.3 | Claude Sonnet | Claude Sonnet + caching |

### Vertical Scaling (Better Performance)

1. **Increase Lambda Memory** (also increases CPU):
   - 1GB → 2GB: 2x faster processing
   - Cost impact: +100% compute, but -50% duration = neutral

2. **Use ARM64 (Graviton2)**:
   - 20% cost reduction
   - Same or better performance

3. **Upgrade to Claude Opus** (highest quality):
   - For complex queries only
   - 4x cost of Sonnet

### Horizontal Scaling (More Capacity)

1. **Lambda Auto-Scaling** (built-in):
   - Automatically handles concurrent requests
   - Pay only for what you use
   - No configuration needed ✅

2. **FAISS Partitioning** (>50K documents):
   - Split index by category/tenant
   - Parallel searches
   - Migration path to managed vector DB

3. **Read Replicas** (high read volume):
   - Replicate FAISS index to multiple Lambdas
   - Use CloudFront for global distribution

---

## 💡 Cost Optimization Tips

### 1. Model Selection (Biggest Impact)

| Optimization | Savings | Implementation |
|--------------|---------|----------------|
| Use Titan instead of Claude | 80% | Change `bedrock_llm_model_id` |
| Use Llama 3.3 instead of Claude | 60% | Use Meta model |
| Enable prompt caching | 90% on cached tokens | Add system prompt |
| Use batch processing | 50% | Process multiple queries together |

### 2. Lambda Optimization

```python
# ❌ Bad: Cold start on every request
def handler(event, context):
    import heavy_library
    client = boto3.client('bedrock')
    ...

# ✅ Good: Load once, reuse
import heavy_library
client = boto3.client('bedrock')

def handler(event, context):
    # Handler logic
    ...
```

**Savings**: 50-70% reduction in execution time

### 3. DynamoDB Caching

Enable query result caching:
- Cache TTL: 1 hour for dynamic content, 24 hours for static
- Cache hit rate: Aim for 30-50%
- **Savings**: 30-50% reduction in Bedrock costs

### 4. S3 Lifecycle Policies

```json
{
  "Rules": [{
    "Id": "MoveToGlacier",
    "Status": "Enabled",
    "Transitions": [
      { "Days": 90, "StorageClass": "GLACIER" }
    ]
  }]
}
```

**Savings**: 84% on old documents

### 5. FAISS Index Optimization

- **Compress index** before S3 upload: 50-70% size reduction
- **Use IVF index** for >100K documents: 10x faster search
- **Prune old embeddings**: Remove documents older than retention period

---

## 🚨 Cost Alerts & Monitoring

### Set Up Budget Alerts

```bash
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget '{
    "BudgetName": "BedrockMonthly",
    "BudgetLimit": {"Amount": "100", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }'
```

### CloudWatch Metrics to Monitor

1. **Lambda Duration** → Optimize if >3s average
2. **Bedrock Token Usage** → Track cost per query
3. **DynamoDB Read/Write Units** → Optimize if >1K/month
4. **S3 Storage Growth** → Set lifecycle policies

---

## 🔄 Migration Paths

### When FAISS Becomes Too Slow (>50K documents)

**Option 1: Aurora PostgreSQL pgvector**
- Cost: $50-80/month
- Supports: 1M+ vectors
- Migration: 2-3 days

**Option 2: Pinecone**
- Cost: $70-120/month
- Supports: 10M+ vectors
- Migration: 1 day (API compatible)

**Option 3: OpenSearch Serverless**
- Cost: $175/month minimum
- Supports: 100M+ vectors
- Migration: 3-5 days
- Best for: Enterprise scale

---

## 📊 Cost Comparison: FAISS vs Alternatives

| Solution | POC Cost | Prod Cost | Breakeven Point |
|----------|----------|-----------|-----------------|
| **FAISS (current)** | $0.78/mo | $15-120/mo | N/A (cheapest) |
| ChromaDB (self-hosted ECS) | $30/mo | $100-200/mo | >5K docs |
| Aurora pgvector | $50/mo | $120-200/mo | >10K docs |
| Pinecone | Free → $70/mo | $70-300/mo | >10K docs |
| OpenSearch Serverless | $175/mo | $350-700/mo | >100K docs |

**Recommendation**:
- 0-10K docs: **FAISS** (current) ✅
- 10K-100K docs: **Aurora pgvector**
- 100K+ docs: **OpenSearch Serverless**

---

## 🎯 Recommendations by Phase

### Phase 1: MVP/POC ($0.78 - $3/month)

**Goal**: Validate concept with minimal cost

**Stack**:
- Bedrock: Titan Text Express
- Vector: FAISS (Lambda)
- Only dev environment

**Duration**: 1-3 months

---

### Phase 2: Pilot ($15 - $30/month)

**Goal**: Test with real users, low volume

**Stack**:
- Bedrock: Llama 3.3 70B
- Vector: FAISS (Lambda)
- Dev + staging environments

**Duration**: 3-6 months

---

### Phase 3: Production ($120 - $450/month)

**Goal**: Scale to production workloads

**Stack**:
- Bedrock: Claude 3.5 Sonnet + caching
- Vector: FAISS → Aurora pgvector (if >10K docs)
- All environments + monitoring

**Duration**: Ongoing

---

## 📚 Additional Resources

- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/)
- [DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/)
- [AWS Cost Calculator](https://calculator.aws/)

---

**Key Takeaway**: By using FAISS instead of OpenSearch, we reduced base infrastructure cost from **$175/month to ~$0.78/month**, making this solution **225x more cost-effective** for small to medium scale deployments.

**Last Updated**: 2025-11-26
