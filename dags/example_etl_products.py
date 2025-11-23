"""
ETL Example usando TaskFlow API - Versión Refactorizada

Demuestra buenas prácticas:
- SQL externalizado en archivos .sql
- Configuración en YAML
- Código limpio y mantenible
"""
from datetime import datetime, timedelta
from pathlib import Path
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
import yaml
import logging

logger = logging.getLogger(__name__)

# Cargar configuración desde YAML
CONFIG_PATH = Path('/usr/local/airflow/include/config/dag_config.yaml')
with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

dag_config = config['dags']['example_etl_products']
default_config = config['default']


def read_sql_file(filepath: str) -> str:
    """Utilitario para leer archivos SQL"""
    path = Path(f'/usr/local/airflow/{filepath}')
    with open(path) as f:
        return f.read()


@dag(
    dag_id='example_etl_products',
    start_date=datetime(2024, 1, 1),
    schedule=dag_config['schedule'],
    catchup=False,
    tags=dag_config['tags'] + ['refactored', 'best-practices'],
    description=f"{dag_config['description']} - Versión refactorizada con SQL externo",
    default_args={
        'owner': default_config['owner'],
        'retries': default_config['retries'],
        'retry_delay': timedelta(minutes=default_config['retry_delay_minutes']),
    },
)
def example_etl_products():
    """
    DAG que demuestra un ETL con buenas prácticas:
    1. Configuración externalizada en YAML
    2. SQL en archivos separados
    3. Código limpio y mantenible
    """

    # Crear tabla usando SQL externo
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id=default_config['postgres_conn_id'],
        sql=read_sql_file('include/sql/etl/create_etl_products_table.sql'),
    )

    @task
    def extract():
        """
        Extrae datos de la base de datos sample_data.
        En un caso real, esto podría ser una API, archivo, etc.
        """
        logger.info("Extrayendo datos desde sample_data.products...")

        pg_hook = PostgresHook(postgres_conn_id=default_config['postgres_conn_id'])

        # Extraer productos de la BD de ejemplo
        extract_sql = """
        SELECT
            product_id as id,
            product_name as name,
            price
        FROM sample_data.products
        WHERE is_available = TRUE
        LIMIT 10;
        """

        records = pg_hook.get_records(extract_sql)

        # Convertir a lista de dicts
        data = [
            {'id': r[0], 'name': r[1], 'price': float(r[2])}
            for r in records
        ]

        logger.info(f"✓ Extraídos {len(data)} productos")
        return data

    @task
    def transform(data: list) -> list:
        """
        Transforma los datos aplicando lógica de negocio.
        Calcula descuentos basados en precio.
        """
        logger.info(f"Transformando {len(data)} registros...")

        transformed = []
        for item in data:
            # Lógica de negocio: descuento basado en precio
            if item['price'] > 100:
                discount_rate = 0.15  # 15% para productos caros
            elif item['price'] > 50:
                discount_rate = 0.10  # 10% para productos medios
            else:
                discount_rate = 0.05  # 5% para productos económicos

            item['discount'] = round(item['price'] * discount_rate, 2)
            item['final_price'] = round(item['price'] - item['discount'], 2)
            transformed.append(item)

        logger.info(f"✓ Transformados {len(transformed)} registros")
        return transformed

    @task
    def load(data: list):
        """Carga los datos transformados a la tabla de destino"""
        logger.info(f"Cargando {len(data)} registros...")

        pg_hook = PostgresHook(postgres_conn_id=default_config['postgres_conn_id'])

        # Usar parámetros para evitar SQL injection
        insert_sql = """
        INSERT INTO sample_data.etl_products (id, name, price, discount, final_price)
        VALUES (%(id)s, %(name)s, %(price)s, %(discount)s, %(final_price)s)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            price = EXCLUDED.price,
            discount = EXCLUDED.discount,
            final_price = EXCLUDED.final_price,
            loaded_at = CURRENT_TIMESTAMP;
        """

        for item in data:
            pg_hook.run(insert_sql, parameters=item)

        logger.info(f"✓ Cargados {len(data)} registros a sample_data.etl_products")

    @task
    def validate(expected_count: int):
        """Valida que los datos se cargaron correctamente"""
        logger.info("Validando datos cargados...")

        pg_hook = PostgresHook(postgres_conn_id=default_config['postgres_conn_id'])

        # Obtener count
        result = pg_hook.get_first("SELECT COUNT(*) FROM sample_data.etl_products;")
        actual_count = result[0] if result else 0

        logger.info(f"Registros esperados: {expected_count}")
        logger.info(f"Registros encontrados: {actual_count}")

        if actual_count >= expected_count:
            logger.info("✓ Validación exitosa")
        else:
            raise ValueError(
                f"Validación falló: esperados al menos {expected_count}, "
                f"encontrados {actual_count}"
            )

        return {'expected': expected_count, 'actual': actual_count}

    @task
    def log_summary(validation_result: dict):
        """Log del resumen final"""
        logger.info("=" * 50)
        logger.info("ETL COMPLETADO")
        logger.info(f"Registros procesados: {validation_result['actual']}")
        logger.info("=" * 50)

    # Definir flujo del DAG
    raw_data = extract()
    transformed_data = transform(raw_data)

    # Flujo: crear tabla -> cargar datos -> validar
    create_table >> raw_data
    load_task = load(transformed_data)
    validation = validate(len(transformed_data))
    summary = log_summary(validation)

    load_task >> validation >> summary


example_etl_products()
