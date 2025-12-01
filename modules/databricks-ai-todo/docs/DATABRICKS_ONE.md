# Opción Databricks One (Lakehouse IQ / Genie) – Pampa AI TODO

## Idea
Usar capacidades nativas de Databricks One (Lakehouse IQ/Genie + AI Functions) para consultas NL sobre el catálogo, minimizando infra extra.

## Qué se necesita
- Tablas Delta en UC con buenos comentarios de columnas (`pampa_ai_todo.serving.operacion_unidades`).
- Lakehouse IQ/Genie habilitado en el workspace y autorizado a leer el catálogo `pampa_ai_todo`.
- AI Functions (`ai_query`, `ai_generate_text`) disponibles en el warehouse.
- Un SQL Warehouse (serverless si está) como compute único; opcional Dashboard/Notebook/Lakehouse App.

## Flujo propuesto
1) Ingesta: igual que el POC ahorro (Volume + job SQL).  
2) Gobernanza: catálogo UC con comentarios bien descriptivos.  
3) Consulta:  
   - Genie (Lakehouse IQ) sobre el catálogo, en español.  
   - AI Functions en SQL para respuestas rápidas (`ai_query` con contexto de tabla).  
   - Dashboard/Notebook como superficie; opcional Lakehouse App ligera.  
4) Sin Model Serving ni Vector Search al inicio. Si la calidad no alcanza, se puede añadir un endpoint de Serving + embeddings.

## Costos estimados (perfil ahorro con Lakehouse IQ)
- Warehouse serverless pequeño (auto-stop 60 min, 1–2 h/día): ~USD 15–40/mes.
- LLM vía AI Functions/Genie (modelo económico, pocas preguntas/día): ~USD 5–15/mes.
- Jobs ingesta (spot 10–15 min/semana): ~USD 2–5/mes.
- Total aproximado: **USD 25–60/mes**.

## Pros
- Sin infra extra: no Model Serving ni Vector Search; solo warehouse.
- Experiencia nativa (Genie/IQ) con gobernanza UC.
- Menos operación; paga por uso del warehouse.

## Contras / límites
- Control limitado del prompting/RAG; chat menos personalizable que un endpoint propio.
- Sin VS, el recall depende de la comprensión de IQ y las descripciones de columnas.
- Latencia: warm start si el warehouse se duerme (5–15 s); estable si está despierto.

## Cómo escalar si falta calidad
- Activar Model Serving Small (sin scale-to-zero) y consumirlo desde una Lakehouse App o IQ como acción personalizada.
- Añadir embeddings + Vector Search si crece el dataset o se requiere mejor recall.
