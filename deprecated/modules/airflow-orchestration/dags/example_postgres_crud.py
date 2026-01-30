"""
PostgreSQL Operations Example

Demuestra diferentes formas de trabajar con PostgreSQL en Airflow
usando PostgresOperator y PostgresHook.
"""
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import logging

logger = logging.getLogger(__name__)


@dag(
    dag_id='example_postgres_crud',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['postgres', 'example', 'sql'],
    description='Ejemplos de operaciones con PostgreSQL',
    default_args={
        'owner': 'snail-data',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
)
def example_postgres_crud():
    """
    DAG que demuestra operaciones con PostgreSQL:
    1. Crear tabla con PostgresOperator
    2. Insertar datos con PostgresOperator
    3. Consultar datos con PostgresHook (@task)
    4. Ejecutar transformaciones SQL
    """

    # Crear tabla de usuarios
    create_users_table = PostgresOperator(
        task_id='create_users_table',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS users_example (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        """,
    )

    # Insertar datos de ejemplo
    insert_users = PostgresOperator(
        task_id='insert_users',
        postgres_conn_id='postgres_default',
        sql="""
        INSERT INTO users_example (username, email)
        VALUES
            ('user1', 'user1@example.com'),
            ('user2', 'user2@example.com'),
            ('user3', 'user3@example.com')
        ON CONFLICT (username) DO NOTHING;
        """,
    )

    @task
    def query_users():
        """Consulta usuarios usando PostgresHook"""
        logger.info("Consultando usuarios...")

        pg_hook = PostgresHook(postgres_conn_id='postgres_default')

        # Obtener todos los usuarios
        sql = "SELECT id, username, email, is_active FROM users_example ORDER BY id;"
        records = pg_hook.get_records(sql)

        logger.info(f"Usuarios encontrados: {len(records)}")
        for record in records:
            logger.info(f"  - ID: {record[0]}, User: {record[1]}, Email: {record[2]}, Active: {record[3]}")

        return len(records)

    @task
    def update_users():
        """Actualiza usuarios usando PostgresHook"""
        logger.info("Actualizando usuarios...")

        pg_hook = PostgresHook(postgres_conn_id='postgres_default')

        # Desactivar usuario específico
        update_sql = """
        UPDATE users_example
        SET is_active = FALSE
        WHERE username = 'user2';
        """
        pg_hook.run(update_sql)

        logger.info("Usuario 'user2' desactivado")

    # Crear tabla de estadísticas
    create_stats = PostgresOperator(
        task_id='create_stats',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS user_stats (
            stat_date DATE PRIMARY KEY,
            total_users INTEGER,
            active_users INTEGER,
            inactive_users INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    )

    # Generar estadísticas
    generate_stats = PostgresOperator(
        task_id='generate_stats',
        postgres_conn_id='postgres_default',
        sql="""
        INSERT INTO user_stats (stat_date, total_users, active_users, inactive_users)
        SELECT
            CURRENT_DATE,
            COUNT(*),
            COUNT(*) FILTER (WHERE is_active = TRUE),
            COUNT(*) FILTER (WHERE is_active = FALSE)
        FROM users_example
        ON CONFLICT (stat_date) DO UPDATE SET
            total_users = EXCLUDED.total_users,
            active_users = EXCLUDED.active_users,
            inactive_users = EXCLUDED.inactive_users,
            created_at = CURRENT_TIMESTAMP;
        """,
    )

    @task
    def show_stats():
        """Muestra estadísticas generadas"""
        logger.info("Mostrando estadísticas...")

        pg_hook = PostgresHook(postgres_conn_id='postgres_default')

        sql = """
        SELECT stat_date, total_users, active_users, inactive_users
        FROM user_stats
        ORDER BY stat_date DESC
        LIMIT 1;
        """
        result = pg_hook.get_first(sql)

        if result:
            logger.info(f"Estadísticas del {result[0]}:")
            logger.info(f"  - Total usuarios: {result[1]}")
            logger.info(f"  - Usuarios activos: {result[2]}")
            logger.info(f"  - Usuarios inactivos: {result[3]}")
        else:
            logger.warning("No se encontraron estadísticas")

    # Definir flujo del DAG
    create_users_table >> insert_users >> query_users() >> update_users()
    create_stats >> generate_stats >> show_stats()

    # Ejecutar stats después de update
    update_users() >> generate_stats


example_postgres_crud()
