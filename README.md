# Snail Data Solutions

Repositorio de soluciones de datos usando Apache Airflow y dbt, gestionado con Astronomer.

## 🛠️ Stack Tecnológico

- **Airflow**: 2.10.3 (Astro Runtime 12.5.0)
- **dbt**: 1.10.15 con adaptador PostgreSQL 1.9.1 (instalado automáticamente)
- **PostgreSQL**: 13
- **Astronomer CLI**: Para desarrollo local
- **Git**: Incluido para operaciones de dbt

## 📁 Estructura del Proyecto

```
snail-data-solutions/
├── dags/                          # DAGs de Airflow
│   ├── default_dag.py            # DAG de ejemplo básico
│   ├── dbt_example_dag.py        # DAG que ejecuta modelos dbt
│   ├── seed_database.py          # Carga datos de ejemplo
│   ├── etl_taskflow_example.py   # ETL con TaskFlow API
│   ├── etl_taskflow_refactored.py # ETL refactorizado (buenas prácticas)
│   ├── postgres_example.py       # Operaciones PostgreSQL
│   └── conditional_example.py    # Branching condicional
├── include/                       # Código compartido
│   ├── dbt/                      # Proyecto dbt
│   │   ├── models/
│   │   │   ├── staging/
│   │   │   └── marts/
│   │   ├── dbt_project.yml
│   │   └── profiles.yml
│   ├── sql/                      # Queries SQL externalizados
│   │   ├── seed/                 # Scripts de inicialización
│   │   │   ├── 01_create_schema.sql
│   │   │   ├── 02_create_tables.sql
│   │   │   └── 03_insert_sample_data.sql
│   │   ├── etl/                  # Queries ETL
│   │   └── analytics/            # Queries de análisis
│   └── config/                   # Configuraciones YAML
│       └── dag_config.yaml       # Configuración de DAGs
├── plugins/                       # Plugins de Airflow
├── tests/                         # Tests
│   └── dags/                     # Tests de DAGs
├── Dockerfile                     # Imagen base de Astronomer
├── requirements.txt               # Dependencias Python
├── packages.txt                   # Paquetes del sistema
├── airflow_settings.yaml          # Configuración local
└── Makefile                      # Comandos útiles
```

## 🚀 Quick Start

### Prerrequisitos

- Docker Desktop
- Astronomer CLI: `brew install astro`
- Make (opcional, para usar atajos)

### Iniciar el proyecto

```bash
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

**IMPORTANTE**: Ejecuta el DAG `seed_database` primero para cargar datos de ejemplo:

1. Ve a http://localhost:8080
2. Busca el DAG `seed_database`
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

Los DAGs de ejemplo (`etl_taskflow_refactored`, `postgres_example`) usan estos datos.

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

Cada DAG demuestra un patrón diferente:
- `seed_database`: Inicialización de datos
- `etl_taskflow_refactored`: ETL con buenas prácticas
- `postgres_example`: Operaciones SQL directas
- `conditional_example`: Lógica condicional
- `dbt_example_dag`: Transformaciones con dbt

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
