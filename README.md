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
├── dags/                    # DAGs de Airflow
│   ├── default_dag.py      # DAG de ejemplo básico
│   └── dbt_example_dag.py  # DAG que ejecuta modelos dbt
├── include/                 # Código compartido y dbt
│   └── dbt/                # Proyecto dbt
│       ├── models/         # Modelos de dbt
│       │   ├── staging/    # Modelos staging
│       │   └── marts/      # Modelos marts
│       ├── dbt_project.yml
│       └── profiles.yml
├── plugins/                 # Plugins de Airflow
├── tests/                   # Tests
│   └── dags/               # Tests de DAGs
├── Dockerfile              # Imagen base de Astronomer
├── requirements.txt        # Dependencias Python
├── packages.txt            # Paquetes del sistema
├── airflow_settings.yaml   # Configuración local
└── Makefile               # Comandos útiles
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
