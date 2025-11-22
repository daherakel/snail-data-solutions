"""
DAG que ejecuta modelos de dbt usando BashOperator
"""
from datetime import datetime
from airflow.decorators import dag
from airflow.operators.bash import BashOperator


@dag(
    dag_id='dbt_example_dag',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['dbt', 'example'],
    description='Ejemplo de ejecución de dbt',
    default_args={
        'owner': 'snail-data',
        'retries': 1,
    },
)
def dbt_example_dag():
    """DAG que ejecuta los modelos de dbt de ejemplo"""

    dbt_debug = BashOperator(
        task_id='dbt_debug',
        bash_command='cd /usr/local/airflow/include/dbt && dbt debug',
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /usr/local/airflow/include/dbt && dbt run',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /usr/local/airflow/include/dbt && dbt test',
    )

    # Flujo: debug -> run -> test
    dbt_debug >> dbt_run >> dbt_test


dbt_example_dag()
