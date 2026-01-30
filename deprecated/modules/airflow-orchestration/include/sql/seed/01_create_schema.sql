-- Crear schema para datos de ejemplo
CREATE SCHEMA IF NOT EXISTS sample_data;

-- Configurar search_path para facilitar queries
COMMENT ON SCHEMA sample_data IS 'Schema con datos de ejemplo para DAGs de Airflow';
