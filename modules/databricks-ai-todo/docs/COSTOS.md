# Opciones de arquitectura y costos estimados – Agente AI TODO Databricks (Pampa)

Supuestos: 3–5 usuarios, español, carga semanal pequeña, uso moderado diario. Rangos referenciales y sujetos a región/contrato.

## Perfil ahorro (recomendado POC)
- Compute: 1 SQL Warehouse pequeño (serverless si está) auto-stop 60 min, sin Model Serving dedicado, sin Vector Search (Delta + embeddings).
- Jobs: ingesta semanal en cluster spot CPU 10–15 min.
- LLM: modelo económico (mistral-7b/mixtral-lite u open-source en Mosaic). Embeddings económicos.
- Pros: costo mínimo, zero infra extra; menos riesgo operativo. Con 1–2 h/día, costo bajo.  
- Contras: warm start si el warehouse se duerme; sin VS, el recall depende de filtros/embeddings simples; no hay endpoint always-on para apps externas.
- Costos estimados/mes:  
  - Warehouse con 1–2 h/día: ~USD 15–40.  
  - LLM + embeddings: ~USD 5–10 (pocas preguntas/día, <1K filas/semana).  
  - Jobs ingesta: ~USD 2–5.  
  - Total aproximado: **USD 25–55**.
- Latencia: 2–3 s si el warehouse está despierto; 5–15 s al reanudarse tras idle.

## Perfil baja latencia (sin VS)
- Compute: mismo warehouse Small/X-Small serverless, auto-stop alto (ej. 120) o always-on según presupuesto. Sin Vector Search.
- Serving: no endpoint dedicado; la app/Notebook usa el warehouse.
- LLM: modelo de mayor calidad (dbrx-instruct/mixtral-8x7b).
- Pros: mejor latencia media (menos warm-start), queries más rápidas; sigue sin pagar Serving ni VS.  
- Contras: mayor uptime del warehouse sube el costo; sigue habiendo warm-start si se duerme; sin VS, el retrieval puede ser más básico.
- Costos estimados/mes:  
  - Warehouse con mayor uptime: ~USD 50–120 (según horas activas/always-on).  
  - LLM + embeddings: ~USD 10–30.  
  - Jobs: ~USD 2–5.  
  - Total aproximado: **USD 60–155**.
- Latencia: 1–2 s cuando el warehouse está despierto; warm-start ocasional al reanudar.

## Perfil baja latencia con Serving siempre encendido (sin VS)
- Compute: warehouse pequeño (para SQL/tablas) + endpoint de Model Serving Small, `scale_to_zero=false`.
- Vector: no VS; retrieval con Delta + embeddings dentro del serving o via warehouse.
- LLM: modelo medio/alto (dbrx-instruct/mixtral-8x7b).
- Pros: latencia estable (sin cold-start), surface lista para apps/servicios; separación de compute (serving vs warehouse).  
- Contras: costo base del endpoint (~USD 120–180/mes) aunque no haya tráfico; sigue sin VS.
- Costos estimados/mes:  
  - Warehouse (uso moderado): ~USD 30–80.  
  - Serving Small always-on: ~USD 120–180 base, más tokens (sumados en LLM).  
  - LLM + embeddings: ~USD 10–30.  
  - Jobs: ~USD 2–5.  
  - Total aproximado: **USD 160–295**.
- Latencia: estable y baja (evita cold-start).

## Perfil con Vector Search serverless (solo si el dataset crece o se necesita mejor recall)
- Compute: igual al perfil de Serving (warehouse + endpoint).  
- Vector Search: índice pequeño en VS serverless.
- Pros: mejor recall/latencia de retrieval cuando crece el volumen; gestión automática de index/replicas.  
- Contras: costo extra mensual por storage/throughput (USD 30–80+); más complejidad de despliegue; innecesario en datasets chicos.
- Costos estimados/mes:  
  - Base perfil Serving: ~USD 160–295.  
  - VS pequeño: +~USD 30–80.  
  - Total aproximado: **USD 190–375**.
- Latencia: mejor para retrieval, más consistente con crecimiento de datos.

## Modelos sugeridos
- Dev/POC: modelo económico (mistral-7b/mixtral-lite en Mosaic) + embeddings económicos.  
- Prod ligero: dbrx-instruct o mixtral-8x7b en Mosaic; embeddings “large” o el más reciente de Mosaic.  
- Separar secretos/scopes para dev/prod; si no hay egress, usar solo Mosaic AI.

## Defaults en el módulo
- `enable_serving=false`, `enable_serverless_warehouse=true`, `warehouse_size="2X-Small"`, `warehouse_auto_stop_mins=60`, sin Vector Search.  
- Se crea catálogo `pampa_ai_todo`, schemas `raw` y `serving`, volume `uploads`, job de ingesta semanal pausado.  
- Para activar serving: `enable_serving=true` y setear `agent_foundation_model` (ej. `databricks-dbrx-instruct`).
