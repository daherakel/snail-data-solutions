"""
Tests de validación básica de DAGs

Verifica que todos los DAGs se pueden importar correctamente
y no tienen errores de sintaxis.
"""
import pytest
from airflow.models import DagBag


class TestDagValidation:
    """Tests de validación básica de DAGs"""

    def test_no_import_errors(self, dagbag):
        """
        Verifica que no hay errores de importación en ningún DAG.
        Este es el test más importante - si falla, nada más funcionará.
        """
        assert not dagbag.import_errors, \
            f"DAG import errors: {dagbag.import_errors}"

    def test_dagbag_has_dags(self, dagbag):
        """Verifica que se encontraron DAGs en el directorio"""
        assert len(dagbag.dags) > 0, "No se encontraron DAGs"

    def test_all_dags_have_tags(self, dagbag):
        """Verifica que todos los DAGs tienen tags para organización"""
        dags_without_tags = [
            dag_id for dag_id, dag in dagbag.dags.items()
            if not dag.tags
        ]
        assert not dags_without_tags, \
            f"DAGs sin tags: {dags_without_tags}"

    def test_all_dags_have_owner(self, dagbag):
        """Verifica que todos los DAGs tienen owner definido"""
        for dag_id, dag in dagbag.dags.items():
            assert dag.default_args.get('owner'), \
                f"DAG {dag_id} no tiene owner definido"

    def test_all_dags_have_retries(self, dagbag):
        """Verifica que todos los DAGs tienen retries configurado"""
        for dag_id, dag in dagbag.dags.items():
            retries = dag.default_args.get('retries')
            assert retries is not None, \
                f"DAG {dag_id} no tiene retries configurado"
            assert retries >= 0, \
                f"DAG {dag_id} tiene retries negativo"

    def test_no_duplicate_dag_ids(self, dagbag):
        """Verifica que no hay IDs de DAG duplicados"""
        dag_ids = list(dagbag.dags.keys())
        assert len(dag_ids) == len(set(dag_ids)), \
            "Hay DAG IDs duplicados"

    def test_all_dags_pausable(self, dagbag):
        """Verifica que todos los DAGs se pueden pausar"""
        for dag_id, dag in dagbag.dags.items():
            assert dag.is_paused_upon_creation is not None, \
                f"DAG {dag_id} no tiene is_paused_upon_creation definido"

    @pytest.mark.parametrize("expected_dag", [
        "default_dag",
        "dbt_example_dag",
        "seed_database",
        "etl_taskflow_example",
        "etl_taskflow_refactored",
        "postgres_example",
        "conditional_example",
    ])
    def test_expected_dag_exists(self, dagbag, expected_dag):
        """Verifica que los DAGs esperados existen"""
        assert expected_dag in dagbag.dags, \
            f"DAG esperado '{expected_dag}' no encontrado"

    def test_all_dags_have_description(self, dagbag):
        """Verifica que todos los DAGs tienen descripción"""
        dags_without_description = [
            dag_id for dag_id, dag in dagbag.dags.items()
            if not dag.description
        ]
        assert not dags_without_description, \
            f"DAGs sin descripción: {dags_without_description}"
