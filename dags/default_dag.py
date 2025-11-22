"""Default DAG for Snail Data Solutions"""
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator

@dag(
    dag_id='default_dag',
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=['default', 'snail-data'],
    description='Default DAG for Snail Data Solutions',
    default_args={
        'owner': 'snail-data',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
)
def default_dag():
    """Simple default DAG demonstrating basic Airflow 3 structure"""

    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    start >> end

default_dag()
