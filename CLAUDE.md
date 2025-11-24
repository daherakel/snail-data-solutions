# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# Instrucciones del Proyecto Snail Data Solutions

## Sobre Snail Data Solutions

**Snail Data Solutions** es una consultora especializada en Data Engineering y AI. Este repositorio contiene soluciones, proyectos, templates y playgrounds reutilizables para acelerar implementaciones de clientes y servir como base de conocimiento.

## Quick Reference

### Common Commands (Airflow Module)
```bash
# Working directory
cd modules/airflow-orchestration

# Core operations
make start          # Start Airflow (http://localhost:8080, admin/admin)
make stop           # Stop Airflow
make logs           # View all logs
make shell          # Open shell in container

# dbt operations
make dbt-run        # Run dbt models
make dbt-test       # Run dbt tests
make dbt-debug      # Verify dbt configuration

# Testing
make pytest         # Run Airflow tests

# Single test
astro dev pytest tests/dags/test_specific_dag.py
```

### Architecture at a Glance
- **Airflow Orchestration Module**: `modules/airflow-orchestration/`
  - DAGs: `dags/` (setup_*, example_*, dbt_*)
  - dbt models: `include/dbt/models/` (staging/, marts/)
  - SQL queries: `include/sql/`
  - Config: `include/config/`

- **AWS Bedrock Module**: `modules/aws-bedrock-agents/` (in development)
  - Infrastructure: `infrastructure/terraform/`
  - Lambda functions: `lambda-functions/`
  - Docs: `docs/aws-bedrock-agents/`

### Key Files to Read First
- This file (CLAUDE.md) for project context
- `modules/airflow-orchestration/README.md` for Airflow setup
- `modules/aws-bedrock-agents/README.md` for Bedrock module
- `docs/aws-bedrock-agents/COST_ANALYSIS.md` for AWS cost estimates

## Objetivo del Repositorio

Este repositorio funciona como:
- **Biblioteca de soluciones**: Templates y patrones probados listos para usar
- **Playground**: Espacio para experimentar con nuevas tecnologías y patrones
- **Base de conocimiento**: Ejemplos y documentación de mejores prácticas
- **Acelerador de proyectos**: Código reutilizable para implementaciones de clientes

## Stack Tecnológico

### Actual
- **Orquestación**: Apache Airflow 2.10.3 (Astro Runtime 12.5.0)
- **Transformación**: dbt 1.10.15 con adaptador PostgreSQL
- **Plataforma**: Astronomer (desarrollo local y deployment)
- **Cloud**: AWS (Bedrock, Lambda, Step Functions, S3, Textract)
- **Base de Datos**: PostgreSQL 13 (para ejemplos locales)
- **Contenedores**: Docker
- **IaC**: Terraform (multi-ambiente: dev/staging/prod)

### Próximamente
- **Databricks**: Para procesamiento de big data y ML

## Principios y Valores del Proyecto

Todo código y arquitectura debe seguir estos principios:

### 1. Excelencia Operativa
- Código limpio, legible y bien documentado
- Automatización de procesos repetitivos
- Monitoreo y observabilidad desde el diseño
- Documentación siempre actualizada

### 2. Seguridad
- Credenciales NUNCA en código (usar variables de entorno, secrets managers)
- Principio de privilegios mínimos
- Validación de inputs y outputs
- Logs sin información sensible

### 3. Confiabilidad y Fiabilidad
- Tests unitarios y de integración
- Manejo de errores robusto
- Idempotencia en todas las operaciones
- Retry logic con backoff exponencial

### 4. Optimización de Costos
- Recursos dimensionados apropiadamente
- Limpieza de recursos temporales
- Monitoreo de uso de recursos
- Cacheo inteligente cuando aplique

### 5. Rendimiento Eficiente
- Queries optimizadas
- Procesamiento en paralelo cuando sea posible
- Lazy loading y streaming para grandes volúmenes
- Índices apropiados en bases de datos

### 6. Sostenibilidad y Escalabilidad
- Arquitectura modular y desacoplada
- Configuración externalizada
- Diseño para escalar horizontalmente
- Abstracciones reutilizables

### 7. Reusabilidad
- Código DRY (Don't Repeat Yourself)
- Templates y funciones compartidas
- Convenciones claras y consistentes
- Documentación de casos de uso

### 8. Principios de Programación
- SOLID principles
- KISS (Keep It Simple, Stupid)
- YAGNI (You Aren't Gonna Need It)
- Separation of Concerns
- Single Responsibility

### 9. Infraestructura como Código
- Todo infrastructure debe ser código
- Versionado en Git
- Ambientes reproducibles
- Deployment automatizado

## Arquitectura Modular

El proyecto está diseñado para ser **completamente modular**. Puedes levantar componentes específicos sin necesidad de correr todo el stack.

### Estructura de Módulos

```
snail-data-solutions/
├── modules/                        # Todos los módulos del proyecto
│   ├── airflow-orchestration/     # Módulo de orquestación con Airflow + dbt
│   │   ├── dags/                  # DAGs de Airflow
│   │   │   ├── setup_*            # DAGs de setup/inicialización
│   │   │   ├── example_*          # DAGs de ejemplo/referencia
│   │   │   └── dbt_*              # DAGs que ejecutan dbt
│   │   ├── include/               # Código compartido
│   │   │   ├── dbt/               # Proyecto dbt
│   │   │   ├── sql/               # SQL queries
│   │   │   └── config/            # Configuraciones YAML
│   │   ├── plugins/               # Plugins de Airflow
│   │   ├── tests/                 # Tests del módulo
│   │   ├── Dockerfile             # Imagen de Astronomer
│   │   ├── requirements.txt       # Dependencias Python
│   │   ├── Makefile              # Comandos del módulo
│   │   └── README.md              # Documentación del módulo
│   │
│   └── aws-bedrock-agents/        # Módulo de agentes AI con AWS Bedrock
│       ├── infrastructure/        # IaC con Terraform
│       │   └── terraform/
│       │       ├── modules/       # Módulos reutilizables
│       │       └── environments/  # dev/staging/prod
│       ├── lambda-functions/      # Código de Lambdas
│       ├── step-functions/        # Workflows
│       ├── tests/                 # Tests del módulo
│       └── README.md              # Documentación del módulo
│
├── docs/                           # Documentación general del proyecto
│   ├── architecture/              # Diagramas y arquitectura
│   └── aws-bedrock-agents/        # Docs específicos de Bedrock
│       ├── README.md
│       ├── ARCHITECTURE.md
│       └── COST_ANALYSIS.md
│
├── .claude/                        # Configuración de Claude Code
│   └── commands/
│       └── init.md
│
├── CLAUDE.md                       # Este archivo
├── README.md                       # README principal
└── .gitignore
```

### Cómo Levantar Componentes Específicos

**Módulo Airflow Orchestration:**
```bash
# Desde el root del proyecto
cd modules/airflow-orchestration
astro dev start

# O usando make
make start

# Solo dbt (dentro del contenedor)
make dbt-run
```

**Módulo AWS Bedrock Agents:**
```bash
# Ver análisis de costos primero
cat docs/aws-bedrock-agents/COST_ANALYSIS.md

# Desplegar infraestructura (ambiente dev)
cd modules/aws-bedrock-agents/infrastructure/terraform/environments/dev
terraform init
terraform plan
terraform apply

# Ver documentación completa
cat modules/aws-bedrock-agents/README.md
```

**DAGs específicos:**
Los DAGs se pueden activar/desactivar individualmente en la UI de Airflow o mediante tags.

## Módulos del Proyecto

### Módulo AWS Bedrock AI Agents

**Descripción**: Solución modular para crear agentes de AI usando AWS Bedrock que procesan y responden consultas sobre diversos tipos de archivos.

**Componentes**:
- Amazon Bedrock (Claude/Titan) para modelos de lenguaje
- Knowledge Bases for Amazon Bedrock (RAG)
- AWS Lambda para procesamiento de documentos
- AWS Step Functions para orquestación de workflows
- Amazon S3 para almacenamiento (raw → processed)
- Amazon Textract para OCR
- Terraform para IaC multi-ambiente

**Tipos de archivos soportados**:
- PDFs y documentos
- Datos estructurados (CSV, JSON)
- Código fuente
- Multimedia (imágenes con texto vía OCR)

**Casos de uso**:
- Análisis de documentos y contratos
- Code assistant para bases de código
- Data analysis sobre datasets
- Document processing multi-fuente

**Arquitectura**:
- Pipeline de ingesta: S3 → EventBridge → Step Functions → Lambda → S3 processed → Knowledge Base
- Agente AI: Bedrock Agent + Knowledge Base + Lambda custom actions
- Multi-ambiente: dev/staging/prod con Terraform

**Documentación completa**:
- Módulo: `modules/aws-bedrock-agents/README.md`
- Arquitectura: `docs/aws-bedrock-agents/README.md`
- Costos: `docs/aws-bedrock-agents/COST_ANALYSIS.md`

**Costos estimados mensuales** (ver análisis completo en COST_ANALYSIS.md):
- MVP/Testing: **$10-30** (Claude Haiku + Pinecone free tier)
- Producción ligera: **$120-200** (Claude Sonnet + Aurora pgvector)
- Producción moderada: **$350-450** (Sonnet + OpenSearch 2 OCU)
- Producción intensiva: **$800-1,200** (Sonnet/Opus + OpenSearch escalado)

⚠️ **Nota**: El costo principal es el vector store (OpenSearch ~$175/mes mínimo). Para minimizar costos iniciales, usar alternativas como Aurora pgvector ($50-80/mes) o Pinecone free tier.

**Estado**: 🔄 En desarrollo
- ✅ Arquitectura diseñada
- ✅ Estructura de directorios creada
- ✅ Documentación base
- ✅ Análisis completo de costos
- ✅ Estructura modular documentada
- ⏳ Módulos de Terraform
- ⏳ Lambda functions
- ⏳ Step Functions workflows

## Convenciones del Proyecto

### Nomenclatura

**DAGs:**
- Prefijos: `setup_`, `example_`, `dbt_`, `etl_`, `ml_`
- Formato: `{prefix}_{descripcion_snake_case}.py`
- Ejemplos: `setup_sample_database.py`, `etl_customer_orders.py`

**Modelos dbt:**
- Staging: `stg_{source}_{entity}.sql` (ej: `stg_postgres_customers.sql`)
- Marts: `{tipo}_{descripcion}.sql` (ej: `fct_sales.sql`, `dim_customers.sql`)

**Archivos SQL:**
- Formato: `{numero}_{descripcion}.sql` si son secuenciales
- Formato: `{descripcion}.sql` si son independientes

**Variables de entorno:**
- Mayúsculas con underscores: `DBT_HOST`, `AIRFLOW_CONN_POSTGRES`

**Módulos de Terraform:**
- Formato: `{servicio}-{proposito}` (ej: `bedrock-agent`, `lambda-processor`)
- Variables: snake_case (ej: `knowledge_base_name`, `lambda_timeout`)
- Outputs: snake_case con sufijo descriptivo (ej: `bucket_arn`, `lambda_function_name`)

**Lambda Functions:**
- Directorio: `{tipo}-{proposito}` (ej: `pdf-processor`, `query-handler`)
- Handler: `handler.py` con función `lambda_handler`
- Archivos: snake_case (ej: `pdf_extractor.py`, `text_processor.py`)

**Step Functions:**
- Archivos: `{workflow}-{proposito}.asl.json` (ej: `document-ingestion.asl.json`)
- Estados: PascalCase (ej: `ProcessDocument`, `IndexContent`)

### Organización de Código

**SQL Externalizado:**
- NUNCA escribir SQL hardcoded en Python
- Todo SQL debe estar en `include/sql/` o modelos dbt
- Usar funciones helper para leer archivos SQL

**Configuración Externalizada:**
- Parámetros en archivos YAML en `include/config/`
- Variables de entorno en `.env` (nunca commiteadas)
- `.env.example` siempre actualizado

**Secrets y Credenciales:**
- NUNCA en código o configs commiteados
- Usar `.env` local (en `.gitignore`)
- Usar Airflow Connections/Variables en producción
- Usar AWS Secrets Manager en cloud

### Tests

**Obligatorios para:**
- Todos los DAGs nuevos (test de import mínimo)
- Todos los modelos dbt (unique, not_null como mínimo)
- Funciones compartidas/helpers

**Ubicación:**
- Tests de DAGs: `tests/dags/`
- Tests de dbt: `include/dbt/models/*/schema.yml`
- Tests de helpers: `tests/unit/`

### Documentación

**README.md:**
- Información para usuarios/developers
- Quick start y comandos básicos
- Troubleshooting común

**CLAUDE.md (este archivo):**
- Contexto del proyecto para Claude
- Principios y valores
- Instrucciones específicas para desarrollo
- **DEBE actualizarse en cada cambio significativo**

**Docstrings:**
- Todas las funciones públicas
- Todos los DAGs (en el docstring del DAG)
- Modelos dbt (en archivos `.yml`)

## Instrucciones para Claude

### Typical Development Workflows

#### Adding a New DAG
1. Read existing DAGs in `modules/airflow-orchestration/dags/` to understand patterns
2. Create new DAG file with appropriate prefix (setup_*, example_*, etl_*, etc.)
3. Externalize SQL queries to `include/sql/`
4. Externalize configuration to `include/config/` (YAML)
5. Add test in `tests/dags/test_your_dag.py`
6. Run: `cd modules/airflow-orchestration && make start`
7. Verify DAG appears in UI at http://localhost:8080
8. Run tests: `make pytest`

#### Adding a dbt Model
1. Navigate to `modules/airflow-orchestration/include/dbt/models/`
2. Create staging model in `staging/stg_{source}_{entity}.sql`
3. Create mart model in `marts/{fct|dim}_{description}.sql`
4. Add tests in corresponding `schema.yml` file (unique, not_null minimum)
5. Run: `make dbt-run` to materialize
6. Run: `make dbt-test` to validate
7. Update documentation in schema.yml

#### Modifying AWS Bedrock Infrastructure
1. Read existing Terraform modules in `modules/aws-bedrock-agents/infrastructure/terraform/modules/`
2. Review cost analysis first: `docs/aws-bedrock-agents/COST_ANALYSIS.md`
3. Modify Terraform module or create new one
4. Update variables in `environments/dev/variables.tf`
5. Plan: `terraform plan` from environment directory
6. Apply: `terraform apply` (with user confirmation)
7. Document changes in module README and update costs if applicable

#### Running Single Test
```bash
cd modules/airflow-orchestration
astro dev pytest tests/dags/test_specific_dag.py::test_function_name -v
```

#### Debugging a DAG Issue
1. Check scheduler logs: `make logs-scheduler`
2. Verify DAG syntax: `astro dev bash -c "python dags/your_dag.py"`
3. Check Airflow UI for import errors
4. Verify SQL files exist in `include/sql/`
5. Check database connection: `make dbt-debug`

### Code Patterns to Follow

**SQL Externalization Pattern:**
```python
# Read SQL from file (see example DAGs)
def read_sql_file(filepath):
    with open(filepath, 'r') as f:
        return f.read()

# Usage in DAG
sql = read_sql_file('include/sql/analytics/query.sql')
```

**YAML Configuration Pattern:**
```python
# Load config from YAML (see example DAGs)
import yaml

with open('include/config/dag_config.yaml') as f:
    config = yaml.safe_load(f)

# Access config values
schedule = config['dag']['schedule']
```

**dbt Model Pattern:**
```sql
-- Staging: stg_source_entity.sql (materialized as view)
-- Clean and standardize raw data
with source as (
    select * from {{ source('postgres', 'raw_table') }}
)
select
    id,
    lower(trim(name)) as name_clean,
    created_at
from source

-- Marts: fct_entity.sql (materialized as table)
-- Business logic and aggregations
select
    d.id,
    d.name_clean,
    count(*) as total_count
from {{ ref('stg_source_entity') }} d
group by 1, 2
```

**Airflow Connection Pattern:**
```python
# Use Airflow connections, not hardcoded credentials
from airflow.providers.postgres.hooks.postgres import PostgresHook

pg_hook = PostgresHook(postgres_conn_id='postgres_default')
```

### Al Trabajar en Este Proyecto

1. **SIEMPRE lee el código existente antes de modificar**
   - Entiende los patrones actuales mostrados arriba
   - Mantén consistencia con el estilo existente
   - Busca ejemplos similares en `dags/example_*.py`

2. **Sigue los principios del proyecto**
   - Revisa la sección "Principios y Valores" antes de proponer cambios
   - Optimiza para reusabilidad y escalabilidad
   - Aplica los patrones de código establecidos

3. **Mantén la modularidad**
   - Cada DAG debe ser independiente
   - Cada módulo de dbt debe ser autocontenido
   - Usa configuraciones externalizadas

4. **Documenta todos los cambios**
   - Actualiza README.md si afecta uso/comandos
   - Actualiza CLAUDE.md si cambian principios/estructura
   - Agrega docstrings a código nuevo
   - Actualiza archivos `.yml` de dbt

5. **Tests son obligatorios**
   - Agrega tests para código nuevo
   - Verifica que tests existentes pasen
   - No hacer commits si los tests fallan

6. **Seguridad primero**
   - Nunca expongas credenciales
   - Valida inputs externos
   - Usa conexiones de Airflow para DBs

### Al Crear Nuevas Soluciones

1. **Identifica si es reusable**
   - Si sí: crear template genérico en `/templates` (futuro)
   - Si no: documentar caso de uso específico

2. **Sigue nomenclatura establecida**
   - Usa prefijos apropiados
   - Nombres descriptivos y claros

3. **Externaliza configuración**
   - Parámetros en YAML
   - Credenciales en variables de entorno
   - Documentar configuración en README

4. **Agrega ejemplos y tests**
   - Al menos un ejemplo de uso
   - Tests básicos de funcionamiento

### Al Actualizar Documentación

**Actualiza CLAUDE.md cuando:**
- Se agreguen nuevos módulos/componentes
- Cambien principios o convenciones
- Se agreguen nuevas herramientas al stack
- Se modifique la estructura del proyecto

**Actualiza README.md cuando:**
- Cambien comandos o instrucciones de uso
- Se agreguen nuevas dependencias
- Cambien los pasos de setup
- Se agreguen nuevos DAGs relevantes

### Common Issues and Solutions

**Issue: DAG not appearing in Airflow UI**
```bash
# Check scheduler logs for import errors
make logs-scheduler

# Verify DAG syntax
astro dev bash -c "python dags/your_dag.py"

# Common causes:
# - Syntax errors in DAG file
# - Missing dependencies in requirements.txt
# - Import errors (missing modules)
```

**Issue: dbt models failing**
```bash
# Verify dbt connection
make dbt-debug

# Check compiled SQL
make dbt-compile

# Common causes:
# - Database connection issues (check .env)
# - Missing source tables (run setup_sample_database DAG first)
# - Invalid Jinja syntax in models
# - Missing dependencies in dbt_project.yml
```

**Issue: "Permission denied" or database connection errors**
```bash
# Verify environment variables
astro dev bash -c "env | grep DBT"

# Restart Airflow to reload .env
make restart

# Common causes:
# - .env file not loaded
# - PostgreSQL container not running
# - Incorrect credentials in .env
```

**Issue: Changes not reflected after editing code**
```bash
# For DAG changes: Wait ~30 seconds (auto-reload)
# For include/ changes: Restart required
make restart

# For dbt changes: Recompile
make dbt-compile
```

**Issue: Docker resource issues**
```bash
# Clean up Docker resources
make clean

# Remove all volumes and start fresh
docker system prune -a --volumes

# Restart from scratch
make start
```

## Estado Actual del Proyecto

### Implementado
- ✅ Setup de Airflow con Astronomer
- ✅ Integración de dbt con PostgreSQL
- ✅ Base de datos de ejemplo (e-commerce)
- ✅ DAGs de ejemplo (ETL, CRUD, branching)
- ✅ Estructura modular con carpeta `modules/`
- ✅ SQL y configs externalizados
- ✅ Tests básicos de DAGs
- ✅ Tests de dbt con validaciones
- ✅ Makefile con comandos útiles
- ✅ Documentación en README.md
- ✅ Documentación CLAUDE.md con principios y convenciones
- ✅ Comando `/init` para cargar contexto automáticamente
- ✅ AWS CLI configurado y verificado

### En Progreso
- 🔄 Módulo AWS Bedrock AI Agents
  - ✅ Arquitectura diseñada con diagrama de flujo
  - ✅ Estructura modular documentada (modules/aws-bedrock-agents/)
  - ✅ Documentación completa del módulo
  - ✅ Análisis detallado de costos (MVP: $10-30/mes, Prod: $120-1,200/mes)
  - ✅ Estrategias de optimización de costos identificadas
  - ✅ Alternativas de vector store evaluadas (OpenSearch vs Aurora vs Pinecone)
  - ⏳ Módulos de Terraform (bedrock, lambda, step-functions, s3, iam)
  - ⏳ Lambda functions para procesamiento de documentos
  - ⏳ Step Functions workflows

### Por Implementar
- ⏳ Templates reutilizables para DAGs comunes
- ⏳ CI/CD pipeline (GitHub Actions)
- ⏳ Integración Airflow + AWS (S3, Redshift operators)
- ⏳ Databricks integration
- ⏳ Deployment a Astronomer Cloud
- ⏳ Monitoreo y alertas
- ⏳ Catálogo de datos (dbt docs)

## Comandos de Claude Code

### Iniciar una Nueva Sesión

Cuando abras una nueva ventana/sesión de Claude Code, ejecuta:

```
/init
```

Este comando carga automáticamente todo el contexto del proyecto desde CLAUDE.md, incluyendo principios, convenciones, y arquitectura.

### Otros Comandos Útiles

```
/context        # Ver qué contexto está cargado actualmente
/help           # Ver todos los comandos disponibles
```

## Comandos del Proyecto

```bash
# Desarrollo
make start              # Levantar todo el stack
make stop               # Detener todo
make restart            # Reiniciar
make logs               # Ver logs

# dbt
make dbt-debug          # Verificar config dbt
make dbt-run            # Ejecutar modelos
make dbt-test           # Ejecutar tests dbt

# Testing
make pytest             # Tests de Airflow

# Limpieza
make clean              # Limpiar todo y empezar fresh
```

## Recursos

- [Documentación Airflow](https://airflow.apache.org/docs/)
- [Documentación dbt](https://docs.getdbt.com/)
- [Astronomer Docs](https://www.astronomer.io/docs/)
- [AWS Best Practices](https://aws.amazon.com/architecture/well-architected/)

---

**Última actualización**: 2025-11-24
**Mantenedor**: Snail Data Solutions
**Versión**: 1.1.0
