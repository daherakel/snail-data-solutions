# Opción supervisor multi-agente en Databricks One (sin IaC)

Objetivo: Agente de presupuestos con supervisor que enruta entre Genie/Lakehouse IQ (preguntas generales sobre Delta) y una función de matching en Unity Catalog para nombres similares. Todo dentro de la plataforma (sin Terraform).

## Componentes (todo nativo)
- **Tablas Delta en UC**: presupuestos con comentarios de columnas (cargadas desde CSV/Excel con un notebook/job manual).
- **Genie / Lakehouse IQ**: respuestas NL sobre las tablas Delta.
- **Función de matching en UC**: UDF/AI Function para buscar registros similares por nombre (levenshtein/n-gram o embeddings ligeros).
- **Supervisor**: Notebook o Lakehouse App que decide la ruta:
  - Intención “consulta general” → Genie/IQ.
  - Intención “matching” (p.ej. “¿este proveedor coincide con…?”) → función UC de matching.
  - (Opcional) Reglas de calidad: checks de totales, meses faltantes, duplicados.
- **SQL Warehouse**: compute único (serverless si está) para Genie y funciones SQL/AI.

## Flujo
1) Ingesta: subir CSV/Excel a un Volume o External Location. Notebook manual (o job sencillo) escribe Delta y agrega comentarios.  
2) Consulta: usuario pregunta en español; el supervisor clasifica la intención.  
3) Enrutamiento:
   - Genie/IQ responde usando el catálogo UC.  
   - La función UC de matching devuelve top-N coincidencias (por similitud de texto).  
   - Supervisor combina y presenta la respuesta.

## Función de matching (opciones)
- **SQL simple (barato)**: `levenshtein`/`soundex`/trigram; bueno para volúmenes chicos y nombres cortos.  
- **Embeddings ligeros (mejor recall)**: generar embeddings económicos en una columna Delta y computar coseno; sin VS al inicio. Si el volumen crece, migrar a Vector Search.  
- Exponer como UDF en UC o AI Function para usarla desde SQL/Genie.

## Costos estimados (perfil ahorro)
- 1 SQL Warehouse serverless pequeño (auto-stop 60 min, 1–2 h/día): ~USD 15–40/mes.
- LLM vía Genie/AI Functions (modelo económico, pocas preguntas/día): ~USD 5–15/mes.
- Ingesta manual/ocasional: ~USD 2–5/mes (si usas un job corto).
- Sin Model Serving ni Vector Search: **total ~USD 25–60/mes**.
- Si activas embeddings ligeros, el costo de embeddings sigue siendo bajo (<USD 5/mes con <1K filas/semana).

## Pros
- 100% en plataforma, sin despliegue IaC.
- Coste mínimo y un solo compute (warehouse).
- Genie cubre Q&A general; la función UC cubre matching especializado.

## Contras / cuándo escalar
- Menos control fino del chat que un endpoint dedicado.
- Recall de matching limitado con solo SQL; si crece el volumen o los nombres son complejos, pasar a embeddings + (opcional) Vector Search.
- Latencia de warm-start si el warehouse se duerme (5–15 s).

## Próximos pasos sugeridos
- Armar un notebook con:
  - Ingesta CSV → Delta + comentarios.
  - Función SQL de matching (levenshtein/n-gram) y ejemplo de uso.
  - Ejemplo de prompt a Genie y de llamada a la función de matching.
- Configurar Genie con el catálogo de presupuestos y probar en español.
- Si falta recall, añadir columna de embeddings y cálculo de coseno en SQL; evaluar VS si crece el dataset.
