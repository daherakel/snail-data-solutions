# Plan e IaC blueprint – Agente AI TODO en Databricks (Pampa Energía)

## Alcance y supuestos
- Datos: CSV/Excel en español con descripciones en la misma fuente; carga semanal; volumen pequeño.
- Usuarios: 3 de negocio, uso moderado.
- Latencia: agente siempre encendido (sin cold-start) y costo-eficiente.
- Seguridad: sin PII confirmada, pero contemplar controles; principio de mínimo privilegio y secretos fuera de código.

## Arquitectura propuesta (alto nivel)
- **Ingesta**: carga a UC Volume/External Location dedicada → job semanal que limpia y escribe Delta con comentarios de columnas.
- **Enriquecimiento**: generar embeddings con modelo económico y guardarlos en Delta; si se habilita, publicar índice en Vector Search serverless. Fallback barato: solo Delta + embeddings y consultas filtradas.
- **Serving**: endpoint de Model Serving serverless para el agente (retrieval + LLM) y, si se prefiere, otro endpoint para embeddings. SQL Warehouse pequeño (serverless o X-Small) para consultas/tablas.
- **Superficie**: app ligera dentro del workspace (p. ej. Lakehouse App/Notebook/SQL Dashboard) o un mini-frontend sobre el endpoint de Model Serving; evita infra extra.
- **Governance/observabilidad**: catálogo/espacio dedicados, secret scopes, logging a storage corporativo y auditoría del workspace.

## IaC con Terraform (recursos objetivo)
- Provider `databricks` configurado con SP/PAT/identity federation (host del workspace, account ID si aplica).
- Catálogo y schemas: `pampa_ai_todo` (`raw`, `serving`), Volume o External Location para cargas.
- Permisos: grants mínimos para rol de negocio (cargar archivos/consultar) y rol técnico (administrar recursos); opcional policies de cluster/warehouse para acotar tamaños.
- Compute:
  - SQL Warehouse pequeño (`serverless` preferido; si no, clásico X-Small con auto-stop alto para evitar cold-start).
  - Model Serving endpoint para el agente (Mosaic AI o LLM externo) con configuración de scale-to-1 min; opcional endpoint separado para embeddings.
  - Job cluster autoscaling CPU para ingesta semanal y generación de embeddings; se apaga tras correr.
- Vector:
  - Si habilitado: `databricks_vector_search_index` sobre la tabla con embeddings.
  - Si no, usar consultas Delta + UDF de similaridad en el job/serving.
- Secretos: `databricks_secret_scope` y secrets para llaves de LLM externo, storage (si external) y webhooks.
- Jobs:
  - Ingesta semanal: lee CSV/Excel, aplica comentarios de columnas, escribe Delta (`raw`/`serving`).
  - Embeddings: calcula/actualiza embeddings; opcional publica a VS.
  - Opcional: job de mantenimiento (vacuum/optimize) mensual.
- Observabilidad: dashboards SQL básicos (costos/latencia), logs de jobs y serving a storage; alertas simples.

### Esqueleto Terraform sugerido (referencial)
```hcl
provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}

resource "databricks_catalog" "pampa" {
  name    = "pampa_ai_todo"
  comment = "Catálogo AI TODO Pampa Energía"
}

resource "databricks_schema" "raw" {
  catalog_name = databricks_catalog.pampa.name
  name         = "raw"
}

resource "databricks_schema" "serving" {
  catalog_name = databricks_catalog.pampa.name
  name         = "serving"
}

resource "databricks_volume" "uploads" {
  catalog_name = databricks_catalog.pampa.name
  schema_name  = databricks_schema.raw.name
  name         = "uploads"
  comment      = "Uploads CSV/Excel del agente AI TODO"
}

resource "databricks_sql_warehouse" "agent_wh" {
  name          = "wh_ai_todo"
  cluster_size  = "2X-Small" # usar "Serverless" si habilitado
  auto_stop_mins = 120
}

resource "databricks_model_serving_endpoint" "agent" {
  name = "agent_ai_todo"
  config {
    served_models {
      name    = "agent-rt"
      model_name = var.agent_model_name # ej. DBRX/Mixtral/Claude en Mosaic AI
      scale_to_zero_enabled = false # siempre encendido
      workload_size = "Small"
    }
  }
}
```

## Costeo estimado (referencial, ajustar según región y precios del workspace)
- **Dev**: warehouse X-Small/serverless con auto-stop alto; model serving Small con scale-to-1; job cluster spot CPU para ingesta semanal; Vector Search opcional desactivado inicialmente.
- **Prod**: warehouse Small con auto-stop alto o always-on según latencia objetivo; model serving Small/Medium según calidad de LLM; VS serverless si se necesita mejor recall/latencia; mantener jobs puntuales.
- **LLM**: dev con modelo barato (open-source pequeño en Mosaic AI o endpoint económico); prod con modelo mejor en español (DBRX/Mixtral/Claude). Separar scopes para ambos.

## Pasos siguientes (orden propuesto)
1) Confirmar disponibilidad de Serverless (Warehouse y Model Serving) y Vector Search; egress permitido para LLM externo si se requiere.  
2) Definir LLM dev/prod y modelo de embeddings (económico) aprobado.  
3) Acordar ubicación de cargas (Volume vs External Location) y permisos/grupos para negocio vs técnico.  
4) Ajustar IaC: completar variables, tamaños y políticas de costo; agregar jobs y scripts de ingesta/embeddings.  
5) Probar con dataset ejemplo en español; validar latencia y costo; decidir si activar Vector Search o quedarnos con Delta + embeddings.  
6) Documentar operaciones (cómo subir CSV, cómo monitorear y apagar/ajustar recursos).
