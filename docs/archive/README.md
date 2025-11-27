# Archived Documentation

This directory contains historical documentation preserved for reference purposes only.

**⚠️ Note**: These documents describe **alternative implementations** or **outdated architectures**. They are NOT the current implementation.

---

## Current Implementation

Our **production system** uses:
- **Vector Store**: FAISS (Lambda layer)
- **LLM**: Meta Llama 3.3 70B / Amazon Titan Express
- **Deployment**: See [DEPLOYMENT.md](../DEPLOYMENT.md)
- **Costs**: See [COST_AND_SCALING.md](../COST_AND_SCALING.md)

---

## Archived Documents

### Vector Database Evaluations

#### `VECTOR_DB_COMPARISON.md`
Comprehensive comparison of 7 vector database options (Qdrant, Pinecone, Weaviate, ChromaDB, FAISS, Milvus, OpenSearch).

**Date**: 2025-11-23
**Status**: Archived
**Reason**: Comparison completed. FAISS selected as primary implementation for cost optimization.
**Use case**: Reference if considering migration to different vector store for scale (>50K documents)

---

#### `FREE_VECTOR_DB_OPTIONS.md`
Detailed guide to zero-cost vector database implementations with code examples.

**Date**: 2025-11-23
**Status**: Archived
**Reason**: FAISS implementation adopted. Other free options preserved for reference.
**Use case**: Useful for understanding trade-offs of different free vector stores

---

### Alternative Implementations

#### `POC_SETUP.md`
Original POC setup guide using ChromaDB as vector store.

**Date**: 2025-11-23
**Status**: Archived
**Reason**: Implementation migrated to FAISS. ChromaDB approach preserved as alternative.
**Use case**:
- Historical reference for ChromaDB implementation
- Alternative if FAISS doesn't meet future requirements
- Code examples for document processing pipeline

---

#### `SESSIONS_DESIGN.md`
Detailed conversational sessions system design with DynamoDB schema.

**Date**: 2025-11-23
**Status**: Archived
**Reason**: Content integrated into main module README and DEPLOYMENT guide
**Use case**:
- Detailed DynamoDB schema reference
- Conversation state machine design
- Deep dive into session management implementation

---

## When to Use Archived Docs

### ✅ Use archived docs when:
- Evaluating migration to different vector database (>50K documents)
- Understanding historical architecture decisions
- Comparing alternative implementations
- Need detailed DynamoDB schema reference
- Researching ChromaDB as alternative to FAISS

### ❌ Don't use archived docs for:
- New deployments (use [DEPLOYMENT.md](../DEPLOYMENT.md) instead)
- Cost planning (use [COST_AND_SCALING.md](../COST_AND_SCALING.md) instead)
- Current architecture reference (use [Module README](../../modules/aws-bedrock-agents/README.md) instead)

---

## Migration History

| Date | Change | Reason |
|------|--------|--------|
| 2025-11-26 | FAISS adopted as primary vector store | Cost optimization ($175/mo OpenSearch → $0.78/mo FAISS) |
| 2025-11-23 | ChromaDB POC completed | Validated RAG architecture |
| 2025-11-22 | Vector DB comparison completed | Evaluated 7 options for best fit |

---

## Related Current Documentation

- **[DEPLOYMENT.md](../DEPLOYMENT.md)** - Current deployment guide
- **[COST_AND_SCALING.md](../COST_AND_SCALING.md)** - Cost analysis & scaling strategies
- **[Module README](../../modules/aws-bedrock-agents/README.md)** - Architecture & implementation
- **[Root README](../../README.md)** - Project overview

---

**Last Updated**: 2025-11-26
**Archive Purpose**: Historical reference and alternative implementation examples
