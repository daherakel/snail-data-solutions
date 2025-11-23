"""
ETL Example usando TaskFlow API

Demuestra el patrón moderno de Airflow con @task decorators
para extraer, transformar y cargar datos.
"""
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
import logging

logger = logging.getLogger(__name__)


@dag(
    dag_id='etl_taskflow_example',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['etl', 'example', 'taskflow'],
    description='ETL básico usando TaskFlow API',
    default_args={
        'owner': 'snail-data',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
)
def etl_taskflow_example():
    """
    DAG que demuestra un ETL básico:
    1. Extraer datos de una fuente simulada
    2. Transformar los datos
    3. Cargar a PostgreSQL
    """

    @task
    def extract():
        """Extrae datos de una fuente (simulado)"""
        logger.info("Extrayendo datos...")

        # Simula datos extraídos
        data = [
            {'id': 1, 'name': 'Product A', 'price': 100},
            {'id': 2, 'name': 'Product B', 'price': 200},
            {'id': 3, 'name': 'Product C', 'price': 300},
        ]

        logger.info(f"Extraídos {len(data)} registros")
        return data

    @task
    def transform(data: list) -> list:
        """Transforma los datos agregando descuento"""
        logger.info("Transformando datos...")

        transformed = []
        for item in data:
            item['discount'] = item['price'] * 0.1
            item['final_price'] = item['price'] - item['discount']
            transformed.append(item)

        logger.info(f"Transformados {len(transformed)} registros")
        return transformed

    @task
    def load(data: list):
        """Carga los datos a PostgreSQL"""
        logger.info("Cargando datos a PostgreSQL...")

        # Conexión a PostgreSQL
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')

        # Crear tabla si no existe
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS etl_products (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            price NUMERIC(10,2),
            discount NUMERIC(10,2),
            final_price NUMERIC(10,2),
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        pg_hook.run(create_table_sql)

        # Insertar datos
        for item in data:
            insert_sql = f"""
            INSERT INTO etl_products (id, name, price, discount, final_price)
            VALUES ({item['id']}, '{item['name']}', {item['price']},
                    {item['discount']}, {item['final_price']})
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                price = EXCLUDED.price,
                discount = EXCLUDED.discount,
                final_price = EXCLUDED.final_price,
                loaded_at = CURRENT_TIMESTAMP;
            """
            pg_hook.run(insert_sql)

        logger.info(f"Cargados {len(data)} registros a etl_products")

    @task
    def validate(data: list):
        """Valida que los datos se cargaron correctamente"""
        logger.info("Validando datos...")

        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        result = pg_hook.get_first("SELECT COUNT(*) FROM etl_products;")

        count = result[0] if result else 0
        logger.info(f"Total de registros en etl_products: {count}")

        if count >= len(data):
            logger.info("✓ Validación exitosa")
        else:
            raise ValueError(f"Validación falló: esperados {len(data)}, encontrados {count}")

    # Definir flujo del DAG
    raw_data = extract()
    transformed_data = transform(raw_data)
    load(transformed_data)
    validate(transformed_data)


etl_taskflow_example()
