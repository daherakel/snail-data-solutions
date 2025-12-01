-- Demo POC AI TODO - Pampa Energia
-- Requiere haber corrido el job de ingesta o cargar el CSV en el Volume.

-- 1) Seleccionar catalogo/schema y revisar la tabla
USE CATALOG pampa_ai_todo;
USE SCHEMA serving;

SELECT * FROM operacion_unidades LIMIT 10;

-- 2) Produccion total y disponibilidad promedio por planta
SELECT
  planta,
  ROUND(SUM(produccion_mwh), 2) AS produccion_mwh_total,
  ROUND(AVG(disponibilidad_pct), 2) AS disponibilidad_promedio
FROM operacion_unidades
GROUP BY planta
ORDER BY produccion_mwh_total DESC;

-- 3) Disponibilidad promedio por unidad
SELECT
  planta,
  unidad,
  ROUND(AVG(disponibilidad_pct), 2) AS disponibilidad_promedio
FROM operacion_unidades
GROUP BY planta, unidad
ORDER BY disponibilidad_promedio DESC;

-- 4) Observaciones mas frecuentes (para notas operativas)
SELECT
  observaciones,
  COUNT(*) AS veces
FROM operacion_unidades
GROUP BY observaciones
ORDER BY veces DESC;

-- 5) Rango temporal (si hay mas fechas en el dataset real)
SELECT MIN(fecha) AS fecha_min, MAX(fecha) AS fecha_max FROM operacion_unidades;
