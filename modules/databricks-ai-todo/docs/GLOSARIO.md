# Glosario rápido – Servicios y componentes (Databricks AI TODO)

- **Unity Catalog (UC)**: catálogo central para gobernar datos y permisos. Aquí creamos `catalog/schema/volume` y tablas Delta del agente.
- **Volume**: almacenamiento gestionado en UC para subir archivos (CSV/Excel). Ruta: `/Volumes/<catalog>/<schema>/<volume>/...`.
- **External Location**: alternativa a Volume usando storage externo (S3/ADLS/GCS) con control de permisos UC.
- **Delta Table**: formato de tabla transaccional con esquema y comentarios; base para consultas y embeddings.
- **SQL Warehouse (serverless o clásico)**: motor SQL para consultas y jobs. Serverless reduce ops y arranca rápido; clásico requiere elegir nodos. En este POC es el compute principal.
- **Model Serving (Mosaic AI)**: endpoints serverless para LLM/embeddings. Útil para latencia estable y apps externas; tiene costo base si se deja siempre encendido.
- **Vector Search (VS)**: servicio para índices de embeddings y búsquedas semánticas rápidas. Mejora recall/latencia cuando el dataset crece; añade costo de index/storage.
- **Jobs**: orquestación de pipelines (ingesta, embeddings, mantenimiento). Pueden usar warehouse o clusters de job.
- **Clusters de Job**: clusters de Spark efímeros para tareas (ingesta/embeddings). Se apagan al terminar; en el POC usamos SQL Warehouse para ingesta ligera.
- **Secret Scope**: almacén seguro de secretos (API keys LLM, credenciales de storage). Referenciados desde notebooks/jobs/serving.
- **Mosaic AI / Foundation Models**: modelos gestionados por Databricks (ej. `databricks-dbrx-instruct`). Evita egress y simplifica auth; costo por tokens y, si serving always-on, costo base.
- **Embeddings**: vectores numéricos que representan texto/columnas. Se almacenan en Delta (perfil ahorro) o en VS (perfil alta latencia/recall).
- **Serverless vs clásico**:
  - *Serverless SQL*: menos ops, arranque rápido, paga por uso; costo unitario algo mayor, depende de disponibilidad regional.
  - *Serverless Serving*: baja latencia, sin clusters; costo base si está always-on.
  - *VS serverless*: gestiona índices y réplicas; costo por storage/throughput.
- **Auto-stop**: configuración para pausar el warehouse tras inactividad; ahorra costo a cambio de posibles warm-starts.
- **Scale-to-zero (serving)**: permite apagar el endpoint sin tráfico; ahorra costo pero agrega cold-start. Para latencia estable se usa `scale_to_zero=false`.
