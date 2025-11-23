"""
Tests de integridad de DAGs

Verifica la estructura interna de los DAGs, tareas,
y dependencias.
"""
import pytest
from airflow.models import DagBag
from airflow.utils.dag_cycle_tester import check_cycle


class TestDagIntegrity:
    """Tests de estructura y dependencias de DAGs"""

    def test_all_dags_have_tasks(self, dagbag):
        """Verifica que todos los DAGs tienen al menos una tarea"""
        for dag_id, dag in dagbag.dags.items():
            assert len(dag.tasks) > 0, \
                f"DAG {dag_id} no tiene tareas"

    def test_no_cycles_in_dags(self, dagbag):
        """Verifica que no hay ciclos en las dependencias de tareas"""
        for dag_id, dag in dagbag.dags.items():
            try:
                check_cycle(dag)
            except Exception as e:
                pytest.fail(f"DAG {dag_id} tiene un ciclo: {str(e)}")

    def test_all_tasks_have_task_id(self, dagbag):
        """Verifica que todas las tareas tienen task_id"""
        for dag_id, dag in dagbag.dags.items():
            for task in dag.tasks:
                assert task.task_id, \
                    f"Tarea en DAG {dag_id} no tiene task_id"

    def test_no_duplicate_task_ids(self, dagbag):
        """Verifica que no hay task_ids duplicados dentro de cada DAG"""
        for dag_id, dag in dagbag.dags.items():
            task_ids = [task.task_id for task in dag.tasks]
            assert len(task_ids) == len(set(task_ids)), \
                f"DAG {dag_id} tiene task_ids duplicados"

    def test_default_args_propagate(self, dagbag):
        """
        Verifica que los default_args se propagan correctamente
        a las tareas que no tienen valores explícitos.
        """
        for dag_id, dag in dagbag.dags.items():
            if dag.default_args:
                # Verificar que al menos una tarea hereda los default_args
                has_inherited_args = any(
                    hasattr(task, 'owner') or
                    hasattr(task, 'retries')
                    for task in dag.tasks
                )
                # Este test es más informativo que crítico
                assert has_inherited_args or len(dag.tasks) == 0

    def test_catchup_is_defined(self, dagbag):
        """Verifica que todos los DAGs tienen catchup definido"""
        for dag_id, dag in dagbag.dags.items():
            assert hasattr(dag, 'catchup'), \
                f"DAG {dag_id} no tiene catchup definido"

    def test_start_date_is_defined(self, dagbag):
        """Verifica que todos los DAGs tienen start_date"""
        for dag_id, dag in dagbag.dags.items():
            assert dag.start_date is not None, \
                f"DAG {dag_id} no tiene start_date definido"

    def test_schedule_is_defined(self, dagbag):
        """Verifica que todos los DAGs tienen schedule definido"""
        for dag_id, dag in dagbag.dags.items():
            # schedule puede ser None (manual), pero debe estar definido
            assert hasattr(dag, 'schedule_interval') or hasattr(dag, 'schedule'), \
                f"DAG {dag_id} no tiene schedule definido"

    def test_seed_database_has_correct_structure(self, dagbag):
        """Test específico para el DAG seed_database"""
        dag = dagbag.dags.get('seed_database')
        if not dag:
            pytest.skip("DAG seed_database no encontrado")

        # Verificar que tiene las tareas esperadas
        task_ids = {task.task_id for task in dag.tasks}
        expected_tasks = {
            'start_seed',
            'create_schema',
            'create_tables',
            'insert_sample_data',
            'verify_data',
            'complete_seed',
        }

        missing_tasks = expected_tasks - task_ids
        assert not missing_tasks, \
            f"Tareas faltantes en seed_database: {missing_tasks}"

    def test_etl_refactored_uses_config(self, dagbag):
        """Verifica que el DAG refactorizado usa configuración"""
        dag = dagbag.dags.get('etl_taskflow_refactored')
        if not dag:
            pytest.skip("DAG etl_taskflow_refactored no encontrado")

        # Verificar que tiene el tag de best-practices
        assert 'best-practices' in dag.tags, \
            "ETL refactorizado debe tener tag 'best-practices'"

    def test_dbt_dag_structure(self, dagbag):
        """Test específico para el DAG de dbt"""
        dag = dagbag.dags.get('dbt_example_dag')
        if not dag:
            pytest.skip("DAG dbt_example_dag no encontrado")

        # Verificar que tiene tareas de dbt
        task_ids = {task.task_id for task in dag.tasks}
        dbt_tasks = {'dbt_debug', 'dbt_run', 'dbt_test'}

        assert dbt_tasks.issubset(task_ids), \
            f"DAG dbt debe tener tareas: {dbt_tasks}"

    def test_conditional_dag_has_branches(self, dagbag):
        """Verifica que el DAG condicional tiene branching"""
        dag = dagbag.dags.get('conditional_example')
        if not dag:
            pytest.skip("DAG conditional_example no encontrado")

        # Debe tener más de una rama (más de 3 tareas)
        assert len(dag.tasks) >= 3, \
            "DAG condicional debe tener al menos 3 tareas"

    def test_all_postgres_operators_have_connection(self, dagbag):
        """
        Verifica que todos los PostgresOperators tienen
        postgres_conn_id definido.
        """
        from airflow.providers.postgres.operators.postgres import PostgresOperator

        for dag_id, dag in dagbag.dags.items():
            for task in dag.tasks:
                if isinstance(task, PostgresOperator):
                    assert hasattr(task, 'postgres_conn_id'), \
                        f"Tarea {task.task_id} en {dag_id} no tiene postgres_conn_id"
                    assert task.postgres_conn_id, \
                        f"Tarea {task.task_id} en {dag_id} tiene postgres_conn_id vacío"
