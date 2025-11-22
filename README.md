# Snail Data Solutions

Repositorio centralizado de soluciones de datos utilizando Apache Airflow (Astronomer) y dbt.

## Estructura del Proyecto

```
snail-data-solutions/
├── dags/                       # DAGs de Airflow
│   └── default_dag.py         # DAG por defecto
├── include/                    # Recursos adicionales
│   └── dbt/                   # Proyecto dbt
│       ├── models/
│       │   ├── staging/       # Modelos de staging
│       │   └── marts/         # Modelos de marts
│       ├── macros/            # Macros de dbt
│       ├── tests/             # Tests de dbt
│       ├── seeds/             # Archivos CSV de referencia
│       ├── dbt_project.yml    # Configuración del proyecto dbt
│       └── profiles.yml       # Perfiles de conexión dbt
├── plugins/                    # Plugins personalizados de Airflow
├── tests/                      # Tests de Airflow
├── docker-compose.yml          # Orquestación de contenedores
├── Dockerfile                  # Imagen base de Astronomer
├── Makefile                    # Comandos útiles
├── requirements.txt            # Dependencias Python
└── packages.txt               # Paquetes del sistema
```

## Requisitos Previos

- Docker Desktop instalado y corriendo
- Docker Compose v2.0+
- Make (opcional, pero recomendado)

## Inicio Rápido

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd snail-data-solutions
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env si es necesario
```

### 3. Inicializar el proyecto

```bash
make init
# O manualmente:
# make build
# make up
```

### 4. Acceder a la UI de Airflow

Abrir en el navegador: http://localhost:8080

- **Usuario**: airflow
- **Password**: airflow

## Comandos Disponibles

### Gestión de Servicios

```bash
make help              # Mostrar todos los comandos disponibles
make build             # Construir las imágenes de Docker
make up                # Levantar todos los servicios
make down              # Detener todos los servicios
make restart           # Reiniciar todos los servicios
make clean             # Limpiar volúmenes y datos
```

### Logs y Debugging

```bash
make logs              # Ver logs de todos los servicios
make logs-scheduler    # Ver logs del scheduler
make logs-webserver    # Ver logs del webserver
```

### Shell Access

```bash
make shell-scheduler   # Abrir shell en el scheduler
make shell-webserver   # Abrir shell en el webserver
make shell-db          # Abrir shell de PostgreSQL
```

### Comandos dbt

```bash
make dbt-debug         # Verificar configuración de dbt
make dbt-run           # Ejecutar modelos de dbt
make dbt-test          # Ejecutar tests de dbt
make dbt-compile       # Compilar modelos de dbt
```

### Airflow

```bash
make trigger-default   # Ejecutar el DAG default
make test              # Ejecutar tests de Airflow
```

## Configuración de dbt

El proyecto dbt está configurado para usar PostgreSQL por defecto. Para usar otro data warehouse:

1. Editar `requirements.txt` y descomentar el adaptador apropiado:
   - `dbt-postgres` para PostgreSQL
   - `dbt-snowflake` para Snowflake
   - `dbt-bigquery` para BigQuery
   - `dbt-redshift` para Redshift

2. Actualizar `include/dbt/profiles.yml` con la configuración correspondiente

3. Reconstruir la imagen: `make build`

## Desarrollo

### Agregar un nuevo DAG

1. Crear archivo Python en `dags/`
2. El DAG será detectado automáticamente por Airflow

### Agregar modelos dbt

1. Crear archivos SQL en `include/dbt/models/staging/` o `include/dbt/models/marts/`
2. Ejecutar `make dbt-run` para probar

### Agregar dependencias Python

1. Agregar al `requirements.txt`
2. Ejecutar `make build && make restart`

## Estructura de Soluciones

Este repositorio está diseñado para contener múltiples soluciones de datos. Cada solución puede tener:

- DAGs específicos en `dags/`
- Modelos dbt organizados en subdirectorios de `include/dbt/models/`
- Plugins personalizados en `plugins/`

## Base de Datos

PostgreSQL está disponible en:
- **Host**: localhost
- **Puerto**: 5432
- **Database**: airflow
- **Usuario**: airflow
- **Password**: airflow

## Troubleshooting

### Problemas de permisos

Si encuentras problemas de permisos, asegúrate de configurar el AIRFLOW_UID correcto:

```bash
echo "AIRFLOW_UID=$(id -u)" >> .env
make down
make up
```

### Reiniciar desde cero

```bash
make clean
make init
```

### Ver estado de los servicios

```bash
docker-compose ps
```

## Contribuir

1. Crear una rama para tu feature
2. Agregar tests si aplica
3. Asegurar que los DAGs pasen validación
4. Crear Pull Request

## Licencia

[Especificar licencia]

## Contacto

[Información de contacto]
