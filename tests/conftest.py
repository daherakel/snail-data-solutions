"""
Configuración de pytest para tests de Airflow
"""
import os
from pathlib import Path
import pytest
from airflow.models import DagBag

# Paths importantes
# Usar AIRFLOW_HOME si está definido (dentro del contenedor), sino usar path relativo
AIRFLOW_HOME = os.getenv('AIRFLOW_HOME', '/usr/local/airflow')
PROJECT_ROOT = Path(AIRFLOW_HOME)
DAGS_DIR = PROJECT_ROOT / "dags"
INCLUDE_DIR = PROJECT_ROOT / "include"


@pytest.fixture(scope="session")
def dagbag():
    """
    Fixture que carga todos los DAGs una sola vez por sesión de tests.
    Esto es más eficiente que cargar los DAGs en cada test.
    """
    return DagBag(dag_folder=str(DAGS_DIR), include_examples=False)


@pytest.fixture(scope="session")
def dags_dir():
    """Path al directorio de DAGs"""
    return DAGS_DIR


@pytest.fixture(scope="session")
def include_dir():
    """Path al directorio include"""
    return INCLUDE_DIR
