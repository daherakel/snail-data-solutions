"""
Tests para archivos externos (SQL, YAML, etc.)

Verifica que todos los archivos referenciados por los DAGs existen
y tienen el formato correcto.
"""
import yaml
from pathlib import Path
import pytest


class TestExternalFiles:
    """Tests para archivos SQL y de configuración"""

    def test_sql_seed_files_exist(self, include_dir):
        """Verifica que existen todos los archivos SQL de seed"""
        sql_seed_dir = include_dir / "sql" / "seed"

        required_files = [
            "01_create_schema.sql",
            "02_create_tables.sql",
            "03_insert_sample_data.sql",
        ]

        for filename in required_files:
            file_path = sql_seed_dir / filename
            assert file_path.exists(), \
                f"Archivo SQL de seed faltante: {filename}"

            # Verificar que no está vacío
            assert file_path.stat().st_size > 0, \
                f"Archivo SQL vacío: {filename}"

    def test_sql_etl_files_exist(self, include_dir):
        """Verifica que existen archivos SQL de ETL"""
        sql_etl_dir = include_dir / "sql" / "etl"

        # Debe tener al menos un archivo SQL
        sql_files = list(sql_etl_dir.glob("*.sql"))
        assert len(sql_files) > 0, \
            "No se encontraron archivos SQL en include/sql/etl/"

    def test_sql_analytics_files_exist(self, include_dir):
        """Verifica que existen archivos SQL de analytics"""
        sql_analytics_dir = include_dir / "sql" / "analytics"

        # Debe tener al menos un archivo SQL
        sql_files = list(sql_analytics_dir.glob("*.sql"))
        assert len(sql_files) > 0, \
            "No se encontraron archivos SQL en include/sql/analytics/"

    def test_dag_config_yaml_exists(self, include_dir):
        """Verifica que existe el archivo de configuración"""
        config_file = include_dir / "config" / "dag_config.yaml"
        assert config_file.exists(), \
            "Archivo dag_config.yaml no encontrado"

    def test_dag_config_yaml_valid(self, include_dir):
        """Verifica que el YAML de configuración es válido"""
        config_file = include_dir / "config" / "dag_config.yaml"

        with open(config_file) as f:
            config = yaml.safe_load(f)

        # Verificar estructura básica
        assert 'default' in config, "Falta sección 'default' en config"
        assert 'dags' in config, "Falta sección 'dags' en config"
        assert 'paths' in config, "Falta sección 'paths' en config"

        # Verificar campos en default
        assert 'owner' in config['default'], \
            "Falta 'owner' en configuración default"
        assert 'postgres_conn_id' in config['default'], \
            "Falta 'postgres_conn_id' en configuración default"

    def test_dag_config_has_all_dags(self, include_dir):
        """Verifica que todos los DAGs importantes están en la config"""
        config_file = include_dir / "config" / "dag_config.yaml"

        with open(config_file) as f:
            config = yaml.safe_load(f)

        expected_dags = [
            'seed_database',
            'etl_taskflow_example',
            'postgres_example',
            'conditional_example',
        ]

        for dag_id in expected_dags:
            assert dag_id in config['dags'], \
                f"DAG '{dag_id}' no está en dag_config.yaml"

    def test_sql_files_have_valid_syntax(self, include_dir):
        """
        Verifica que los archivos SQL no tienen errores de sintaxis obvios.
        Test básico: verifica que no están vacíos y tienen keywords SQL.
        """
        sql_dir = include_dir / "sql"

        for sql_file in sql_dir.rglob("*.sql"):
            content = sql_file.read_text()

            # Verificar que no está vacío
            assert len(content.strip()) > 0, \
                f"Archivo SQL vacío: {sql_file.name}"

            # Verificar que contiene al menos un keyword SQL común
            sql_keywords = ['SELECT', 'INSERT', 'CREATE', 'UPDATE', 'DELETE']
            has_keyword = any(keyword in content.upper() for keyword in sql_keywords)
            assert has_keyword, \
                f"Archivo SQL sin keywords SQL válidos: {sql_file.name}"

    def test_dbt_project_exists(self, include_dir):
        """Verifica que existe el proyecto dbt"""
        dbt_dir = include_dir / "dbt"
        assert dbt_dir.exists(), "Directorio dbt no existe"

        # Verificar archivos importantes
        assert (dbt_dir / "dbt_project.yml").exists(), \
            "dbt_project.yml no existe"
        assert (dbt_dir / "profiles.yml").exists(), \
            "profiles.yml no existe"

    def test_dbt_project_yaml_valid(self, include_dir):
        """Verifica que dbt_project.yml es válido"""
        dbt_project_file = include_dir / "dbt" / "dbt_project.yml"

        with open(dbt_project_file) as f:
            dbt_config = yaml.safe_load(f)

        # Verificar campos requeridos
        assert 'name' in dbt_config, "Falta 'name' en dbt_project.yml"
        assert 'version' in dbt_config, "Falta 'version' en dbt_project.yml"
        assert 'profile' in dbt_config, "Falta 'profile' en dbt_project.yml"
