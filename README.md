# 🐌 Snail Data Solutions

Repositorio de soluciones SaaS de Data Engineering y AI, con módulos independientes listos para desplegar.

## 🔗 Quick Links

| Módulo | Descripción | Status |
|--------|-------------|--------|
| [🐌 Snail Doc](modules/snail-doc/) | Asistente AI de documentos con RAG | ✅ Production |
| [⚙️ Airflow Orchestration](modules/airflow-orchestration/) | Pipelines de datos | ✅ Production |
| [📧 Contact Lambda](modules/contact-lambda/) | Formulario de contacto | ✅ Ready |
| [⚡ Databricks AI TODO](modules/databricks-ai-todo/) | Agente conversacional Databricks (Pampa) | 🚧 POC |

**Documentación**:
- [📖 Deployment Guide](docs/DEPLOYMENT.md) - Guía de despliegue completa
- [💰 Cost & Scaling](docs/COST_AND_SCALING.md) - Análisis de costos

---

## 📁 Estructura del Proyecto

```
snail-data-solutions/
├── modules/                           # Módulos SaaS independientes
│   ├── snail-doc/                    # 🐌 Asistente AI de documentos
│   │   ├── frontend/                 # Next.js UI
│   │   ├── infrastructure/           # Terraform IaC
│   │   ├── lambda-functions/         # AWS Lambda
│   │   └── README.md
│   │
│   ├── airflow-orchestration/        # ⚙️ Data pipelines
│   │   ├── dags/                     # DAGs de Airflow
│   │   ├── include/                  # dbt, SQL, config
│   │   └── README.md
│   │
│   └── contact-lambda/               # 📧 Formulario de contacto
│
├── docs/                              # Documentación general
│   ├── DEPLOYMENT.md                 # Guía de deployment
│   ├── COST_AND_SCALING.md          # Análisis de costos
│   └── archive/                      # Docs históricos
│
├── CLAUDE.md                          # Instrucciones del proyecto
└── README.md                          # Este archivo
```

---

## 🐌 Snail Doc - AI Document Assistant

**Asistente inteligente de documentos** usando AWS Bedrock con FAISS vector search. Sistema conversacional replicable para múltiples clientes/tenants.

### Features v1.1.0
- ✅ Procesamiento automático de PDFs (S3 → Lambda)
- ✅ Vector search con FAISS (38 MB Lambda Layer)
- ✅ RAG conversacional con Claude/Llama/Titan
- ✅ Sistema multi-tenant replicable
- ✅ Historial de conversaciones (DynamoDB)
- ✅ Cache de queries (7 días TTL)
- ✅ Detección de intenciones y guardrails
- ✅ Frontend Next.js con chat, analytics y admin
- ✅ Soporte multi-modelo (Claude, Llama 3.3, Titan)

### Quick Start

```bash
cd modules/snail-doc

# Deploy completo
./scripts/deploy.sh dev

# O manualmente
cd infrastructure/terraform/environments/dev
terraform init && terraform apply
```

### Costos Estimados

| Escenario | Costo/mes | Uso |
|-----------|-----------|-----|
| POC/Dev | $0.78 - $3 | Testing |
| Production Light | $15 - $30 | 500 queries/mes |
| Production | $120 - $200 | 5K queries/mes |

📚 **Documentación completa**:
- [modules/snail-doc/README.md](modules/snail-doc/README.md) - Features & quick start
- [modules/snail-doc/REPLICABILITY.md](modules/snail-doc/REPLICABILITY.md) - Guía de replicación multi-tenant

---

## ⚙️ Airflow Orchestration

**Pipelines de datos** con Apache Airflow y dbt para transformaciones.

### Features
- ✅ Airflow 2.10.3 (Astronomer)
- ✅ dbt 1.10.15 integrado
- ✅ PostgreSQL de ejemplo
- ✅ DAGs de ejemplo listos

### Quick Start

```bash
cd modules/airflow-orchestration
make start
# Abrir http://localhost:8080 (admin/admin)
```

📚 **Documentación completa**: [modules/airflow-orchestration/README.md](modules/airflow-orchestration/README.md)

---

## 🛠️ Stack Tecnológico

### AI & Cloud
- **AWS Bedrock**: Claude/Titan models
- **AWS Lambda**: Serverless compute
- **Amazon S3**: Document storage
- **FAISS**: Vector search

### Data Engineering
- **Apache Airflow**: Orchestration
- **dbt**: SQL transformations
- **PostgreSQL**: Database

### Infrastructure
- **Terraform**: IaC multi-ambiente
- **Docker**: Containerization
- **Next.js**: Frontend framework

---

## 📝 Comandos Útiles

### Snail Doc
```bash
cd modules/snail-doc
./scripts/deploy.sh dev          # Deploy completo
./scripts/upload-document.sh dev file.pdf  # Subir PDF
./scripts/test-query.sh dev "pregunta"     # Test query
```

### Airflow
```bash
cd modules/airflow-orchestration
make start      # Iniciar Airflow
make stop       # Detener
make dbt-run    # Ejecutar dbt
make pytest     # Tests
```

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [CLAUDE.md](CLAUDE.md) | Instrucciones para Claude/AI |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Guía de deployment |
| [docs/COST_AND_SCALING.md](docs/COST_AND_SCALING.md) | Costos y escalamiento |

---

**Desarrollado por Snail Data Solutions** 🐌
