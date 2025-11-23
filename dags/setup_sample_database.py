"""
Setup Sample Database DAG

Carga datos de ejemplo en PostgreSQL ejecutando scripts SQL.
Este DAG debe ejecutarse primero para preparar la base de datos con datos de prueba.
"""
from datetime import datetime, timedelta
from pathlib import Path
from airflow.decorators import dag, task
from airflow.providers.postgres.operators.postgres import PostgresOperator
import yaml
import logging

logger = logging.getLogger(__name__)

# Cargar configuración
CONFIG_PATH = Path('/usr/local/airflow/include/config/dag_config.yaml')
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

# Configuración del DAG desde YAML
dag_config = config['dags'].get('setup_sample_database', config['dags'].get('seed_database', {}))
default_config = config['default']


@dag(
    dag_id='setup_sample_database',
    start_date=datetime(2024, 1, 1),
    schedule=dag_config.get('schedule'),
    catchup=False,
    tags=dag_config.get('tags', ['setup', 'database', 'sample-data']),
    description=dag_config.get('description', 'Carga datos de ejemplo en la base de datos'),
    default_args={
        'owner': default_config['owner'],
        'retries': default_config['retries'],
        'retry_delay': timedelta(minutes=default_config['retry_delay_minutes']),
    },
)
def setup_sample_database():
    """
    DAG que inicializa la base de datos con datos de ejemplo.

    Ejecuta en orden:
    1. Crear schema
    2. Crear tablas
    3. Insertar datos de ejemplo
    """

    @task
    def start_seed():
        """Marca el inicio del proceso de seed"""
        logger.info("Iniciando carga de datos de ejemplo...")
        logger.info("Este proceso creará el schema 'sample_data' y cargará datos de prueba")

    # Leer archivo SQL helper function
    def read_sql_file(filename: str) -> str:
        """Lee un archivo SQL desde el directorio de seed"""
        sql_path = Path(f'/usr/local/airflow/{config["paths"]["sql_seed"]}/{filename}')
        logger.info(f"Leyendo archivo SQL: {sql_path}")
        with open(sql_path) as f:
            return f.read()

    # Task 1: Crear schema
    create_schema = PostgresOperator(
        task_id='create_schema',
        postgres_conn_id=default_config['postgres_conn_id'],
        sql=read_sql_file('01_create_schema.sql'),
    )

    # Task 2: Crear tablas
    create_tables = PostgresOperator(
        task_id='create_tables',
        postgres_conn_id=default_config['postgres_conn_id'],
        sql=read_sql_file('02_create_tables.sql'),
    )

    # Task 3: Insertar datos
    insert_data = PostgresOperator(
        task_id='insert_sample_data',
        postgres_conn_id=default_config['postgres_conn_id'],
        sql=read_sql_file('03_insert_sample_data.sql'),
    )

    @task
    def verify_data():
        """Verifica que los datos se cargaron correctamente"""
        from airflow.providers.postgres.hooks.postgres import PostgresHook

        logger.info("Verificando datos cargados...")
        pg_hook = PostgresHook(postgres_conn_id=default_config['postgres_conn_id'])

        # Verificar counts
        tables = ['customers', 'categories', 'products', 'orders', 'order_items']
        results = {}

        for table in tables:
            count_sql = f"SELECT COUNT(*) FROM sample_data.{table};"
            result = pg_hook.get_first(count_sql)
            count = result[0] if result else 0
            results[table] = count
            logger.info(f"  ✓ {table}: {count} registros")

        # Validar que hay datos
        if all(count > 0 for count in results.values()):
            logger.info("✓ Todos los datos se cargaron correctamente")
        else:
            raise ValueError("Algunas tablas no tienen datos")

        return results

    @task
    def complete_seed(verification_results: dict):
        """Marca el proceso como completado"""
        total_records = sum(verification_results.values())
        logger.info("=" * 50)
        logger.info("✓ SEED COMPLETADO EXITOSAMENTE")
        logger.info(f"Total de registros cargados: {total_records}")
        logger.info("=" * 50)
        logger.info("La base de datos está lista para usar en otros DAGs")

    # Definir flujo
    start = start_seed()
    verification = verify_data()
    complete = complete_seed(verification)

    start >> create_schema >> create_tables >> insert_data >> verification >> complete


setup_sample_database()
