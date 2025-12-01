output "catalog_name" {
  description = "Catalogo creado para el agente"
  value       = databricks_catalog.pampa.name
}

output "raw_schema" {
  description = "Schema raw"
  value       = databricks_schema.raw.name
}

output "serving_schema" {
  description = "Schema serving"
  value       = databricks_schema.serving.name
}

output "uploads_path" {
  description = "Ruta en DBFS/Volumes para subir CSV"
  value       = local.uploads_path
}

output "warehouse_id" {
  description = "SQL Warehouse para queries y jobs"
  value       = databricks_sql_endpoint.agent.id
}

output "ingest_job_id" {
  description = "Job de ingesta semanal (si se habilito)"
  value       = var.enable_jobs ? databricks_job.ingest[0].id : null
}

output "serving_endpoint_name" {
  description = "Endpoint de serving (si se habilito)"
  value       = var.enable_serving && length(databricks_serving_endpoint.agent) > 0 ? databricks_serving_endpoint.agent[0].name : null
}
