# Demo rápida – POC Databricks AI TODO (Pampa)

## Objetivo
Mostrar de punta a punta: CSV cargado en Volume, tabla Delta con comentarios de columnas y consultas básicas desde un Notebook/SQL Dashboard (sin Model Serving ni Vector Search).

## Preparación
1) Subí `data/sample_pampa.csv` a `Volumes/pampa_ai_todo/raw/uploads/`.  
2) Asegúrate de haber corrido `terraform plan/apply` del módulo para crear catálogo, schemas, volume y warehouse.  
3) En Databricks, asigna el warehouse al Notebook/SQL y selecciona catálogo `pampa_ai_todo`.

## Pasos de demo (Notebook/SQL)
Usa el notebook `modules/databricks-ai-todo/notebooks/demo_poc.sql`:
- Set del catálogo/schema y preview de la tabla `serving.operacion_unidades`.
- Métricas simples: producción total por planta, disponibilidad promedio, top observaciones.
- Prompt en español usando el modelo económico (si habilitado) o simplemente muestra las métricas calculadas.

## Qué resaltar en la reunión
- Latencia: ~2–3 s cuando el warehouse está despierto (perfil ahorro).
- Costos: perfil ahorro sin Model Serving ni Vector Search (~USD 25–55/mes estimado).
- Flexibilidad: se puede activar Model Serving y/o Vector Search más adelante con los toggles de Terraform.
- Seguridad: catálogo dedicado, volume controlado, secretos fuera del código.
