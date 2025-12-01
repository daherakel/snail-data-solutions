variable "databricks_host" {
  description = "Databricks workspace URL (https://<workspace>)"
  type        = string
}

variable "databricks_token" {
  description = "Personal access token o client secret para el provider"
  type        = string
  sensitive   = true
}

variable "catalog_name" {
  description = "Nombre del catalogo principal"
  type        = string
  default     = "pampa_ai_todo"
}

variable "raw_schema_name" {
  description = "Schema para datos crudos"
  type        = string
  default     = "raw"
}

variable "serving_schema_name" {
  description = "Schema para tablas listas para el agente"
  type        = string
  default     = "serving"
}

variable "volume_name" {
  description = "Volume para uploads de CSV/Excel"
  type        = string
  default     = "uploads"
}

variable "sample_file_name" {
  description = "Nombre del archivo CSV de ejemplo en el Volume"
  type        = string
  default     = "sample_pampa.csv"
}

variable "workspace_path_base" {
  description = "Ruta base en el workspace para archivos del job"
  type        = string
  default     = "/Shared/pampa-ai-todo"
}

variable "warehouse_name" {
  description = "SQL Warehouse para consultas y tareas SQL"
  type        = string
  default     = "wh_ai_todo"
}

variable "warehouse_size" {
  description = "Tamaño del warehouse (Small/2X-Small/etc.)"
  type        = string
  default     = "2X-Small"
}

variable "warehouse_auto_stop_mins" {
  description = "Minutos para auto-pause del warehouse"
  type        = number
  default     = 60
}

variable "enable_serverless_warehouse" {
  description = "Intentar usar serverless en el warehouse"
  type        = bool
  default     = true
}

variable "enable_jobs" {
  description = "Crear jobs de ingesta/refresh"
  type        = bool
  default     = true
}

variable "ingest_cron" {
  description = "Cron Quartz para la ingesta semanal (UTC)"
  type        = string
  default     = "0 7 * * 1"
}

variable "enable_serving" {
  description = "Crear endpoint de serving para el agente"
  type        = bool
  default     = false
}

variable "agent_endpoint_name" {
  description = "Nombre del endpoint de serving"
  type        = string
  default     = "agent-ai-todo"
}

variable "agent_foundation_model" {
  description = "Modelo foundation de Mosaic AI (ej. databricks-dbrx-instruct). Necesario si enable_serving=true."
  type        = string
  default     = null
}

variable "llm_dev_api_key" {
  description = "API key para modelo externo en dev (opcional)"
  type        = string
  default     = null
  sensitive   = true
}

variable "llm_prod_api_key" {
  description = "API key para modelo externo en prod (opcional)"
  type        = string
  default     = null
  sensitive   = true
}
