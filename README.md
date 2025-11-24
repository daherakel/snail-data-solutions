# Snail Data Solutions

Repositorio de soluciones de Data Engineering y AI, incluyendo pipelines con Apache Airflow y dbt, y agentes de AI con AWS Bedrock.

## 🛠️ Stack Tecnológico

### Orquestación y Transformación
- **Airflow**: 2.10.3 (Astro Runtime 12.5.0)
- **dbt**: 1.10.15 con adaptador PostgreSQL 1.9.1
- **Astronomer CLI**: Para desarrollo local
- **PostgreSQL**: 13 (para ejemplos locales)

### Cloud e AI
- **AWS Bedrock**: Agentes de AI con Claude/Titan
- **AWS Lambda**: Procesamiento serverless
- **AWS Step Functions**: Orquestación de workflows
- **Amazon S3**: Storage de documentos
- **Amazon Textract**: OCR para imágenes

### Infraestructura
- **Terraform**: Infrastructure as Code
- **Docker**: Containerización
- **Git**: Control de versiones

## 📁 Estructura del Proyecto

```
snail-data-solutions/
├── modules/                                # Todos los módulos del proyecto
│   ├── airflow-orchestration/            # Orquestación con Airflow + dbt
│   │   ├── dags/                         # DAGs de Airflow
│   │   ├── include/                      # Código compartido (dbt, sql, config)
│   │   ├── plugins/                      # Plugins de Airflow
│   │   ├── tests/                        # Tests del módulo
│   │   ├── Dockerfile                    # Imagen de Astronomer
│   │   ├── requirements.txt              # Dependencias Python
│   │   ├── Makefile                      # Comandos del módulo
│   │   └── README.md                     # Documentación
│   │
│   └── aws-bedrock-agents/               # Agentes AI con AWS Bedrock
│       ├── infrastructure/               # IaC con Terraform
│       ├── lambda-functions/             # Funciones Lambda
│       ├── step-functions/               # Workflows
│       ├── tests/                        # Tests del módulo
│       └── README.md                     # Documentación
│
├── docs/                                  # Documentación general
│   ├── architecture/                     # Diagramas y arquitectura
│   └── aws-bedrock-agents/               # Docs de Bedrock
│       ├── README.md                     # Arquitectura detallada
│       └── COST_ANALYSIS.md              # Análisis de costos
│
├── .claude/                               # Configuración Claude Code
│   └── commands/                         # Comandos personalizados
│
├── CLAUDE.md                              # Instrucciones del proyecto
├── README.md                              # Este archivo
└── .gitignore
```

### Módulos Disponibles

#### 1. Airflow Orchestration
Orquestación de pipelines de datos con Apache Airflow y transformaciones con dbt.

**Ubicación**: `modules/airflow-orchestration/`
**Documentación**: `modules/airflow-orchestration/README.md`

#### 2. AWS Bedrock AI Agents
Agentes de AI para procesamiento y consulta de documentos usando AWS Bedrock.

**Ubicación**: `modules/aws-bedrock-agents/`
**Documentación**:
- Módulo: `modules/aws-bedrock-agents/README.md`
- Arquitectura: `docs/aws-bedrock-agents/README.md`
- Costos: `docs/aws-bedrock-agents/COST_ANALYSIS.md`
```

## 🚀 Quick Start

### Módulo Airflow Orchestration

**Prerrequisitos**:
- Docker Desktop
- Astronomer CLI: `brew install astro`
- Make (opcional, para usar atajos)

**Iniciar el módulo**:
```bash
# Navegar al módulo
cd modules/airflow-orchestration

# Opción 1: Con Makefile
make start

# Opción 2: Comando directo
astro dev start
```

### Acceder a Airflow

- **URL**: http://localhost:8080
- **Usuario**: `admin`
- **Password**: `admin`

### Cargar datos de ejemplo

**IMPORTANTE**: Ejecuta el DAG `setup_sample_database` primero para cargar datos de ejemplo:

1. Ve a http://localhost:8080
2. Busca el DAG `setup_sample_database`
3. Actívalo y ejecútalo (Trigger DAG)
4. Esto crea:
   - Schema `sample_data`
   - Tablas: `customers`, `products`, `orders`, `order_items`, `categories`
   - ~100 clientes, 25 productos, 200 órdenes con datos realistas

Una vez cargados los datos, los otros DAGs pueden trabajar con ellos.

## 📊 Base de Datos de Ejemplo

El schema `sample_data` contiene un e-commerce simplificado:

- **customers**: 100 clientes en diferentes países
- **categories**: 5 categorías de productos
- **products**: 25 productos con precios y stock
- **orders**: 200 órdenes con diferentes estados
- **order_items**: Detalles de cada orden

Los DAGs de ejemplo (`example_etl_products`, `example_postgres_crud`) usan estos datos.

## 📝 Comandos Útiles

### Gestión del entorno

```bash
make start          # Levantar Airflow
make stop           # Detener Airflow
make restart        # Reiniciar Airflow
make kill           # Detener y eliminar contenedores
make clean          # Limpiar volúmenes y datos
make logs           # Ver logs
make shell          # Abrir shell en el contenedor
```

### dbt

```bash
make dbt-debug      # Verificar configuración de dbt
make dbt-run        # Ejecutar modelos de dbt
make dbt-test       # Ejecutar tests de dbt
make dbt-compile    # Compilar modelos de dbt
```

### Tests

```bash
make pytest         # Ejecutar tests de Airflow
```

## 🔧 Configuración de dbt

**dbt viene preinstalado y configurado** automáticamente al levantar el proyecto.

El proyecto dbt está en `include/dbt/` y se conecta a PostgreSQL usando las variables de entorno en `.env`:

```bash
DBT_HOST=postgres
DBT_USER=postgres
DBT_PASSWORD=postgres
DBT_DATABASE=postgres
DBT_SCHEMA=public
DBT_PORT=5432
```

### DAG de dbt

`dbt_example_dag` ejecuta automáticamente:
1. **dbt debug**: Verifica la configuración y conexión
2. **dbt run**: Materializa los modelos (staging → marts)
3. **dbt test**: Ejecuta tests de validación

### Estructura de modelos

- **staging/**: Modelos que limpian y estandarizan datos raw (views)
  - `stg_example.sql`: Ejemplo de modelo staging
- **marts/**: Modelos finales para análisis y reporting (tables)
  - `fct_example.sql`: Ejemplo de tabla de hechos

## 📦 Agregar Dependencias

### Python

1. Editar `requirements.txt` para dependencias de Python
2. Ejecutar `astro dev restart`

**Nota**: dbt-postgres está instalado en el `Dockerfile` para evitar conflictos de dependencias.

### Sistema

1. Editar `packages.txt` con paquetes de Ubuntu (ej: `git`)
2. Ejecutar `astro dev restart`

### dbt

Para actualizar la versión de dbt, editar la línea correspondiente en el `Dockerfile`:

```dockerfile
RUN pip install --no-cache-dir "dbt-postgres>=1.9.0,<2.0.0"
```

## 🧪 Desarrollo

### Agregar un nuevo DAG

1. Crear archivo en `dags/`
2. El DAG aparecerá automáticamente en la UI (hot-reload)

### Agregar modelos dbt

1. Crear archivos `.sql` en `include/dbt/models/staging/` o `marts/`
2. Ejecutar `make dbt-run` para materializarlos

### Tests de DAGs

Crear tests en `tests/dags/` y ejecutar con `make pytest`

## 🐛 Troubleshooting

### El DAG no aparece en la UI

```bash
# Ver logs del scheduler
make logs-scheduler

# Verificar que no haya errores de sintaxis
astro dev bash -c "python dags/tu_dag.py"
```

### Problemas con dbt

```bash
# Verificar configuración
make dbt-debug

# Ver logs detallados
make logs
```

### Resetear todo

```bash
make clean
make start
```

## ✨ Buenas Prácticas Implementadas

Este repositorio sigue principios de **DRY** (Don't Repeat Yourself) y **KISS** (Keep It Simple):

### SQL Externalizado

✅ **Queries SQL en archivos separados** (`include/sql/`)
- Fácil de mantener y versionar
- Reutilizable entre DAGs
- Testeable independientemente
- Git diff más claro

```python
# Mal ❌
sql = "SELECT * FROM table WHERE..."

# Bien ✅
sql = read_sql_file('include/sql/analytics/query.sql')
```

### Configuración en YAML

✅ **Configuración externalizada** (`include/config/dag_config.yaml`)
- Un solo lugar para cambiar configuraciones
- Fácil de entender y modificar
- Versionable y documentable

```python
# Cargar config
with open('include/config/dag_config.yaml') as f:
    config = yaml.safe_load(f)
```

### Estructura Organizada

✅ **Separación clara de concerns**:
- `dags/`: Lógica de orquestación
- `include/sql/`: Queries SQL
- `include/config/`: Configuraciones
- `include/dbt/`: Modelos de transformación

### DAGs como Ejemplos

Cada DAG tiene un nombre descriptivo que indica su propósito:

**Setup:**
- `setup_sample_database`: Inicializa base de datos con datos de prueba

**Ejemplos:**
- `example_etl_products`: ETL de productos con buenas prácticas
- `example_postgres_crud`: Operaciones CRUD con PostgreSQL
- `example_conditional_branching`: Branching basado en calidad de datos

**dbt:**
- `dbt_run_transformations`: Ejecuta modelos dbt (debug → run → test)

### dbt Tests

Los modelos dbt incluyen tests de calidad de datos:

```bash
# Ejecutar tests de dbt
make dbt-test

# O manualmente
astro dev bash -c "cd include/dbt && dbt test"
```

**Tests implementados:**
- `unique`: Verifica valores únicos en columnas clave
- `not_null`: Asegura que columnas críticas no sean nulas
- `expression_is_true`: Valida reglas de negocio personalizadas

Los tests se definen en `include/dbt/models/*/schema.yml`

## 🤖 Módulo AWS Bedrock AI Agents

### Descripción

Solución modular para crear agentes de AI usando AWS Bedrock que procesan y responden consultas sobre diversos tipos de archivos (PDFs, documentos, CSVs, código, imágenes).

### Arquitectura

- **Document Ingestion Pipeline**: S3 → EventBridge → Step Functions → Lambda → S3 processed → Knowledge Base
- **AI Agent**: Bedrock Agent + Knowledge Bases (RAG) + Lambda custom actions
- **Multi-ambiente**: dev/staging/prod con Terraform

### Casos de Uso

- Análisis de documentos y contratos
- Code assistant para bases de código
- Data analysis sobre datasets
- Document processing multi-fuente

### Inicio Rápido

```bash
# 1. Revisar análisis de costos PRIMERO
cat docs/aws-bedrock-agents/COST_ANALYSIS.md

# 2. Ver documentación completa
cat modules/aws-bedrock-agents/README.md

# 3. Desplegar infraestructura (dev)
cd modules/aws-bedrock-agents/infrastructure/terraform/environments/dev
terraform init
terraform plan
terraform apply
```

### Estado

🔄 **En desarrollo**
- ✅ Arquitectura diseñada
- ✅ Estructura de directorios creada
- ✅ Documentación base
- ⏳ Módulos de Terraform
- ⏳ Lambda functions
- ⏳ Step Functions workflows

Ver documentación completa: `docs/aws-bedrock-agents/README.md`

## 📚 Recursos

- [Astronomer Docs](https://www.astronomer.io/docs/)
- [Apache Airflow Docs](https://airflow.apache.org/docs/)
- [dbt Docs](https://docs.getdbt.com/)

## 🤝 Contribuir

1. Crear una rama desde `main`
2. Hacer cambios y testear localmente
3. Crear Pull Request

## 📄 Licencia

[Definir licencia]
