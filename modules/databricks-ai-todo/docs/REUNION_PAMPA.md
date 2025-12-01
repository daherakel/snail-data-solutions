# Guía de reunión con Pampa Energía – Agente AI TODO Databricks

## Objetivo de la reunión
- Alinear alcance, costos y permisos para habilitar el agente con el perfil ahorro (warehouse serverless pequeño, sin Model Serving ni Vector Search al inicio).
- Confirmar viabilidad técnica (Serverless SQL, egress/LLM, seguridad) y siguientes pasos.

## Preguntas clave
- Workspace/servicios: ¿Serverless SQL y Model Serving están habilitados en la región? ¿Vector Search disponible? ¿Hay restricciones de egress a Internet (solo Mosaic vs externo)?
- Datos: ¿Algún PII/confidencial esperado? ¿Retención requerida para CSV y tablas? ¿Necesitamos masking o borrado programado?
- Identidad/permisos: ¿Grupos SCIM/SSO disponibles para mapear rol negocio vs técnico? ¿Podemos crear un service principal dedicado (tokens/identity federation)?
- Almacenamiento: ¿Prefieren UC Volume gestionado o External Location? ¿Hay bucket/contenedor corporativo ya aprobado?
- Superficie: ¿Se sienten cómodos con Notebook/SQL Dashboard para POC? (sin frontend extra). ¿Necesitan embed o app ligera más adelante?
- Modelos: ¿Mosaic AI permitido? Si no, ¿qué proveedor externo está aprobado? (OpenAI/Azure/otro) ¿Requisitos de residencia?
- Operación: ¿Ventana de ingesta semanal? ¿Quién sube los CSV? ¿Necesitan validaciones (schema/duplicados) y alertas si falla el job?
- Auditoría/monitoreo: ¿Dónde mandar logs (storage corporativo/SIEM)? ¿Alertas por email/Slack existentes?
- Costos: ¿Tope mensual objetivo? (para fijar auto-stop y tamaño del warehouse).

## Pedidos concretos
- Habilitar (o confirmar) Serverless SQL Warehouse en el workspace y acceso a Unity Catalog.
- Service Principal `snail-ai-agent` con permisos para: catálogo/schema/volume, warehouse, jobs, secret scopes.
- Aprobar provider Terraform con ese SP (host + PAT/identity federation).
- Ruta de carga: Volume `pampa_ai_todo.raw.uploads` (o External Location aprobada) con permisos de escritura para el rol de negocio.
- Secret scope gestionado para llaves de LLM externo (si aplica) y credenciales de storage (si external).
- Logs/auditoría: acceso a audit logs del workspace o forwarding a storage/SIEM.

## Demo/POC a mostrar
- CSV de ejemplo cargado en Volume.
- Job de ingesta crea tabla Delta con comentarios de columnas.
- Consulta en SQL Warehouse (Notebook/Dashboard) demostrando entendimiento de columnas y respuestas simples.
- Si hay tiempo: prompt usando modelo económico en español (sin serving dedicado) y mostrar latencia/costo estimado.
