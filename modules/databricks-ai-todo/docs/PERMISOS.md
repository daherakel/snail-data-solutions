# Permisos y recursos necesarios – Agente AI TODO en Databricks (Pampa Energía)

## Objetivo
Habilitar un agente conversacional que ingiera archivos CSV/Excel, interprete columnas con descripciones breves y responda preguntas sobre esos datos dentro de Databricks.

## Supuestos actuales (Pampa)
- Datos de entrada: CSV/Excel en español; las descripciones de columnas vienen en la misma fuente.
- Volumen y uso: carga semanal, tamaño pequeño, 3 usuarios de negocio con uso moderado.
- Sensibilidad: no hay PII confirmada ahora, pero preparar opción de controles.

## Roles y accesos iniciales
- **Service Principal** dedicado (p. ej. `snail-ai-agent`) con acceso al workspace y generación de tokens/PAT/identity federation.
- **Rol de datos** para equipo de negocio con permiso de carga a un volumen/ubicación controlada.
- **Rol técnico** con permisos para crear y administrar recursos del flujo (clusters/warehouses, catálogos, endpoints).

## Permisos requeridos en Databricks
- **Workspace/Compute**
  - Crear y usar: all-purpose clusters, job clusters y SQL Warehouses (idealmente Serverless si está habilitado).
  - Usar Model Serving/Endpoints (Serverless) y Mosaic AI Model Endpoints si están disponibles.
  - Crear y gestionar Jobs/Schedules para pipelines de ingesta y refresco.
- **Unity Catalog**
  - `USE CATALOG`, `USE SCHEMA`, `CREATE SCHEMA`, `CREATE TABLE/VIEW`, `CREATE VOLUME`, `SELECT` y `WRITE` sobre un catálogo dedicado (sugerido `pampa_ai_todo`).
  - `GRANT`/`MANAGE GRANTS` sobre dicho catálogo para delegar accesos mínimos.
  - Crear External Locations si el almacenamiento vive fuera del managed storage.
- **Almacenamiento para uploads**
  - Ruta en UC Volumes o External Location (S3/ADLS/GCS) con permisos de `READ/WRITE/DELETE` para el service principal y el rol de carga.
  - Si se usa Auto Loader, permisos para crear/listar en el bucket y, opcionalmente, topic de notificaciones (SQS/Event Grid/PubSub) si se quiere ingesta continua.
- **Vector / Search**
  - Habilitar Mosaic AI Vector Search (o Feature/Vector Store disponible) con permisos para crear índices, escribir embeddings y consultar.
- **LLM/Integraciones**
  - Acceso a Foundation Models gestionados por Databricks (Mosaic AI) **o** permiso de egress a endpoints externos (OpenAI/Azure/otro) más creación de Secret Scopes/Secrets para API keys.
  - Permiso para registrar y consumir modelos en MLflow Model Registry si se versiona el agente.
- **Observabilidad y seguridad**
  - Acceso a audit logs del workspace o envío a SIEM de Pampa.
  - Permisos para configurar dashboards de monitoreo (SQL/Photon) y alertas básicas.

## Recursos a solicitar
- Workspace de Databricks con Unity Catalog habilitado en la región aprobada por Pampa.
- Catálogo/Schema dedicados para el agente (`pampa_ai_todo.raw`, `pampa_ai_todo.serving`) y un Volume/External Location para las cargas de Excel/CSV.
- Presupuesto de cómputo inicial: 1 SQL Warehouse pequeño (serverless si es posible) y 1 job cluster autoscaling (nodos CPU, posibilidad de GPU opcional para embeddings/finetuning).
- Habilitar Mosaic AI Model Serving/Vector Search en el workspace, o bien confirmar la alternativa aprobada de LLM externo.
- Secret Scope gestionado por seguridad para llaves de LLM externo, webhooks, y credenciales de almacenamiento (si aplica External Location).
- Canal de logging/auditoría (workspace logs en storage corporativo o forwarding a SIEM).

## Requerimientos para agente siempre encendido (sin cold-start)
- Model Serving/Endpoint serverless habilitado (Mosaic AI o endpoints administrados) para el agente y embeddings; evita spin-up de clusters.
- SQL Warehouse serverless pequeño (o clásico con auto-resume rápido) dedicado al agente; configurar auto-pause alto o siempre-on según presupuesto.
- Opcional: cluster liviano siempre-on solo si no hay serverless (tradeoff costo vs latencia).

## Costos y modo costo-eficiente (borrador)
- **Compute**: 1 SQL Warehouse pequeño (serverless o clásico X-Small) y 1 job cluster autoscaling CPU para ingesta/embeddings; apagar tras uso. Para carga semanal, ejecutar jobs puntuales y parar compute automáticamente.
- **LLM**: en dev usar modelo económico (Mosaic AI open-source pequeño o endpoint barato); en prod un modelo de mayor calidad (p. ej. DBRX/Mixtral/Claude) según presupuesto. Pedir scopes para ambos endpoints.
- **Vector Search**: si el costo de VS es alto, opción 1) VS serverless con índice pequeño (paga por uso + storage), opción 2) fallback barato con tabla Delta + embeddings y consultas SQL filtradas (menor costo, más latencia).
- **Superficie**: para 3 usuarios, usar app ligera dentro del workspace (Notebook/SQL Dashboard) o un frontend mínimo sobre Model Serving; evita infra extra.
- **Almacenamiento**: usar UC Volumes o External Location; purgar archivos históricos para reducir storage y mantener tablas Delta compactadas (vacuum).
- **Observabilidad**: logging a storage ya existente; sin nuevos servicios pagos salvo necesidad de alertas básicas en SQL.

## IaC solicitado
- Permisos para usar Terraform con provider de Databricks (service principal con PAT/identity federation) y acceso al workspace backend (workspace URL, workspace ID, host token endpoint).
- Policies de cluster/warehouse definidas para controlar tamaños y costos; ability para crear resources vía Terraform (warehouses, jobs, model endpoints, secret scopes, volumes, vector indexes).
- Acceso a storage backend para state remoto si se usa (S3/ADLS/GCS) y a resource group/proyecto correspondiente.

## Datos y cumplimiento
- Confirmar clasificación del Excel/CSV (¿PII/confidencial?) para decidir encriptado, masking y retention.
- Si se requiere data residency, validar región y que los endpoints de LLM cumplan ese requisito.
- Definir SLA de retención/borrado para archivos subidos y tablas derivadas.

## Opcionales útiles
- Conector de identidad (SCIM/SCIM groups) para mapear roles de negocio al catálogo.
- IP allowlisting o private link para acceso a storage y/o endpoints de LLM.
- Topic de notificaciones para ingesta incremental si se automatizan subidas recurrentes.
