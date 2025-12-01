provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

locals {
  uploads_path          = "dbfs:/Volumes/${var.catalog_name}/${var.raw_schema_name}/${var.volume_name}"
  ingest_workspace_path = "${var.workspace_path_base}/ingest.py"
}

resource "databricks_catalog" "pampa" {
  name    = var.catalog_name
  comment = "Catalogo AI TODO Pampa Energia"
}

resource "databricks_schema" "raw" {
  catalog_name = databricks_catalog.pampa.name
  name         = var.raw_schema_name
  comment      = "Datos crudos subidos por negocio"
}

resource "databricks_schema" "serving" {
  catalog_name = databricks_catalog.pampa.name
  name         = var.serving_schema_name
  comment      = "Tablas listas para el agente"
}

resource "databricks_volume" "uploads" {
  catalog_name = databricks_catalog.pampa.name
  schema_name  = databricks_schema.raw.name
  name         = var.volume_name
  comment      = "Uploads CSV/Excel para AI TODO"
}

resource "databricks_secret_scope" "pampa" {
  name                     = "${var.catalog_name}-secrets"
  initial_manage_principal = "users"
}

resource "databricks_secret" "llm_dev" {
  count     = var.llm_dev_api_key == null ? 0 : 1
  key       = "llm-dev-api-key"
  string_value = var.llm_dev_api_key
  scope     = databricks_secret_scope.pampa.name
}

resource "databricks_secret" "llm_prod" {
  count     = var.llm_prod_api_key == null ? 0 : 1
  key       = "llm-prod-api-key"
  string_value = var.llm_prod_api_key
  scope     = databricks_secret_scope.pampa.name
}

resource "databricks_workspace_file" "ingest" {
  source    = "${path.module}/../jobs/ingest.py"
  path      = local.ingest_workspace_path
  overwrite = true
}

resource "databricks_sql_endpoint" "agent" {
  name                      = var.warehouse_name
  cluster_size              = var.warehouse_size
  auto_stop_mins            = var.warehouse_auto_stop_mins
  enable_serverless_compute = var.enable_serverless_warehouse
  max_num_clusters          = 1
  min_num_clusters          = 1
}

resource "databricks_job" "ingest" {
  count = var.enable_jobs ? 1 : 0
  name  = "pampa-ai-todo-ingest"

  task {
    task_key = "ingest_csv"
    sql_task {
      warehouse_id = databricks_sql_endpoint.agent.id

      query {
        query_text = <<SQL
USE CATALOG ${var.catalog_name};
USE SCHEMA ${var.serving_schema_name};

CREATE OR REPLACE TABLE ${var.catalog_name}.${var.serving_schema_name}.operacion_unidades AS
SELECT *
FROM csv.`${local.uploads_path}/${var.sample_file_name}`
OPTIONS (header "true", inferSchema "true");

COMMENT ON TABLE ${var.catalog_name}.${var.serving_schema_name}.operacion_unidades IS 'POC AI TODO Pampa Energia';
COMMENT ON COLUMN ${var.catalog_name}.${var.serving_schema_name}.operacion_unidades.fecha IS 'Fecha de registro';
COMMENT ON COLUMN ${var.catalog_name}.${var.serving_schema_name}.operacion_unidades.planta IS 'Nombre de la planta';
COMMENT ON COLUMN ${var.catalog_name}.${var.serving_schema_name}.operacion_unidades.unidad IS 'Unidad o bloque generador';
COMMENT ON COLUMN ${var.catalog_name}.${var.serving_schema_name}.operacion_unidades.produccion_mwh IS 'Energia generada en MWh';
COMMENT ON COLUMN ${var.catalog_name}.${var.serving_schema_name}.operacion_unidades.disponibilidad_pct IS 'Disponibilidad porcentual de la unidad';
COMMENT ON COLUMN ${var.catalog_name}.${var.serving_schema_name}.operacion_unidades.observaciones IS 'Notas operativas';
SQL
      }
    }
  }

  schedule {
    quartz_cron_expression = var.ingest_cron
    timezone_id            = "UTC"
    pause_status           = "PAUSED"
  }
}

resource "databricks_serving_endpoint" "agent" {
  count = var.enable_serving && var.agent_foundation_model != null ? 1 : 0
  name  = var.agent_endpoint_name

  config {
    served_entities {
      name                  = "agent-foundation"
      scale_to_zero_enabled = false
      workload_size         = "Small"

      foundation_model {
        name = var.agent_foundation_model
      }
    }
  }
}
