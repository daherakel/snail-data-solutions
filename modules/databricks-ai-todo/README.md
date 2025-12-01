# Databricks AI TODO Agent (Pampa Energía)

Agente conversacional en Databricks para consumir CSV/Excel con descripciones de columnas y responder preguntas de negocio en español. Diseñado para bajo costo, siempre encendido vía Model Serving/SQL Warehouse, y gestionado con Terraform.

## Qué incluye este módulo
- Terraform para catálogo, schemas y Volume de carga (`pampa_ai_todo`), warehouse pequeño (serverless si está disponible), jobs de ingesta semanal y scaffolding de serving.
- Ejemplo de CSV pequeño para la POC (`data/sample_pampa.csv`).
- Blueprint de serving/embeddings para activarlo cuando haya modelo aprobado.

## Requisitos previos
- Workspace Databricks con Unity Catalog y (ideal) Serverless SQL/Model Serving habilitado.
- Service Principal con permisos para crear catálogo/schema/volume, warehouses, jobs y secret scopes.
- `terraform` >= 1.5 y provider `databricks` >= 1.50.
- Variables sensibles (token, llaves LLM) provistas vía `terraform.tfvars` o `-var-file`, nunca en código.

## Documentación
- Costos y perfiles: `modules/databricks-ai-todo/docs/COSTOS.md`
- Permisos y recursos: `modules/databricks-ai-todo/docs/PERMISOS.md`
- Plan e IaC blueprint: `modules/databricks-ai-todo/docs/PLAN.md`
- Glosario: `modules/databricks-ai-todo/docs/GLOSARIO.md`
- Demo y reunión: `modules/databricks-ai-todo/docs/DEMO.md`, `modules/databricks-ai-todo/docs/REUNION_PAMPA.md`

## Estructura
```
modules/databricks-ai-todo/
├── README.md
├── docs/
│   ├── COSTOS.md
│   ├── DEMO.md
│   ├── GLOSARIO.md
│   ├── PERMISOS.md
│   ├── PLAN.md
│   └── REUNION_PAMPA.md
├── data/
│   └── sample_pampa.csv
├── jobs/
│   └── ingest.py           # Job de ingesta CSV -> Delta con comentarios
├── notebooks/
│   └── demo_poc.sql        # Notebook SQL para la demo
└── terraform/
    ├── main.tf
    ├── outputs.tf
    ├── variables.tf
    └── versions.tf
```

## Uso rápido (plan)
```bash
cd modules/databricks-ai-todo/terraform
terraform init
terraform plan \
  -var databricks_host="https://<workspace>" \
  -var databricks_token="..." \
  -var node_type_id="..." \
  -var spark_version="13.3.x-scala2.12"
```
- Sube `data/sample_pampa.csv` a `Volumes/pampa_ai_todo/raw/uploads/` (UI o `dbfs cp`) antes de correr el job de ingesta.
- Activa el endpoint de serving cambiando `enable_serving = true` y seteando `agent_foundation_model` o un modelo registrado.

## Jobs incluidos
- `pampa-ai-todo-ingest`: ejecuta semanalmente (pausado por defecto) un SQL que carga el CSV desde el Volume, crea/actualiza la tabla Delta y aplica comentarios de columnas.

## Superficie sugerida
- POC: Notebook/SQL Dashboard usando el warehouse siempre encendido. Para latencia menor, habilitar Model Serving serverless y apuntar un frontend ligero al endpoint.

## Costos recomendados
- Warehouse: X-Small/Small serverless con auto-stop 60 min (perfil ahorro). Si no hay serverless, usa clásico con auto-resume.
- Jobs: job cluster spot o serverless SQL para la ingesta semanal; se apaga tras correr.
- Serving: endpoint Small con `scale_to_zero_enabled = false` cuando se habilite; en dev usar modelo económico, en prod uno de mayor calidad en español.
- Vector Search: iniciar con Delta + embeddings (sin índice) para minimizar costo; habilitar VS si se necesita mejor recall/latencia.

## Pendientes para producción
- Definir modelo de embeddings y LLM dev/prod permitidos en el workspace.
- Configurar secret scope con llaves de LLM externo (si aplica) y permisos finos para roles de negocio/técnico.
- (Opcional) Habilitar Vector Search serverless y dashboards de monitoreo de latencia/costo.
