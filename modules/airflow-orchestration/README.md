# Airflow Orchestration Module

Orquestación de pipelines de datos con Apache Airflow y transformaciones con dbt.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Astronomer CLI: `brew install astro`

### Start Airflow

```bash
# From this directory
astro dev start

# Or using make
make start
```

**Access Airflow UI**: http://localhost:8080
- **Username**: `admin`
- **Password**: `admin`

### Load Sample Data

⚠️ **Important**: Run the `setup_sample_database` DAG first to load sample data:

1. Go to http://localhost:8080
2. Find `setup_sample_database` DAG
3. Enable and trigger it
4. This creates sample e-commerce data (~100 customers, 25 products, 200 orders)

## 📁 Module Structure

```
airflow-orchestration/
├── dags/                   # Airflow DAGs
│   ├── setup_*            # Setup DAGs
│   ├── example_*          # Example DAGs
│   └── dbt_*              # dbt workflow DAGs
├── include/
│   ├── dbt/               # dbt project
│   │   └── models/        # dbt models (staging/, marts/)
│   ├── sql/               # External SQL queries
│   └── config/            # YAML configurations
├── plugins/               # Airflow plugins
└── tests/                 # Tests
```

## 🛠️ Common Commands

```bash
# Start/Stop
make start              # Start Airflow
make stop               # Stop Airflow
make restart            # Restart Airflow
make logs               # View logs

# dbt
make dbt-debug          # Verify dbt configuration
make dbt-run            # Run dbt models
make dbt-test           # Run dbt tests

# Testing
make pytest             # Run Airflow tests

# Cleanup
make clean              # Clean volumes and data
```

## 📊 Tech Stack

- **Airflow**: 2.10.3 (Astro Runtime 12.5.0)
- **dbt**: 1.10.15 with PostgreSQL adapter
- **PostgreSQL**: 13 (local development)
- **Astronomer CLI**: Local development environment

## 📚 Complete Documentation

For detailed information, see the **[Main README](../../README.md)** sections:
- [Quick Start](../../README.md#-quick-start) - Setup instructions
- [Sample Database](../../README.md#-base-de-datos-de-ejemplo) - Data schema
- [dbt Configuration](../../README.md#-configuración-de-dbt) - dbt setup
- [Troubleshooting](../../README.md#-troubleshooting) - Common issues

## 🧪 Example DAGs

- **`setup_sample_database`** - Initialize sample e-commerce data
- **`example_etl_products`** - ETL pipeline with best practices
- **`example_postgres_crud`** - CRUD operations example
- **`example_conditional_branching`** - Data quality branching
- **`dbt_run_transformations`** - dbt workflow (debug → run → test)

## 🔧 Configuration

### Environment Variables

Configuration is in `.env` (auto-loaded by Astronomer):

```bash
DBT_HOST=postgres
DBT_USER=postgres
DBT_PASSWORD=postgres
DBT_DATABASE=postgres
DBT_SCHEMA=public
DBT_PORT=5432
```

### Adding Dependencies

**Python packages**: Edit `requirements.txt` and run `astro dev restart`

**System packages**: Edit `packages.txt` and run `astro dev restart`

## 📖 Best Practices

This module demonstrates:
- ✅ **SQL Externalization** - Queries in `include/sql/`
- ✅ **Configuration as Code** - YAML configs in `include/config/`
- ✅ **Modular Structure** - Separation of concerns
- ✅ **Testing** - Unit tests for DAGs and dbt
- ✅ **Documentation** - Inline docs and schema files

---

**For full documentation**, see [Main README](../../README.md)
