"""
DAG que ejecuta modelos de dbt usando Astronomer Cosmos
"""
from datetime import datetime
from pathlib import Path

from airflow.decorators import dag
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping


@dag(
    dag_id='dbt_example_dag',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['dbt', 'example'],
    description='Ejemplo de ejecución de dbt con Cosmos',
)
def dbt_example_dag():
    """DAG que ejecuta los modelos de dbt de ejemplo"""

    # Configuración del proyecto dbt
    dbt_project_path = Path("/usr/local/airflow/include/dbt")

    # Configuración del perfil de conexión
    profile_config = ProfileConfig(
        profile_name="snail_data_solutions",
        target_name="dev",
        profile_mapping=PostgresUserPasswordProfileMapping(
            conn_id="postgres_default",
            profile_args={
                "schema": "public",
            },
        ),
    )

    # Configuración del proyecto
    project_config = ProjectConfig(
        dbt_project_path=dbt_project_path,
    )

    # Configuración de ejecución
    execution_config = ExecutionConfig(
        dbt_executable_path="/usr/local/bin/dbt",
    )

    # Task Group que ejecuta todos los modelos dbt
    dbt_tg = DbtTaskGroup(
        group_id="dbt_transform",
        project_config=project_config,
        profile_config=profile_config,
        execution_config=execution_config,
        default_args={"retries": 2},
    )

    dbt_tg


dbt_example_dag()
