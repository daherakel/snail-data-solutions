import os
from pyspark.sql import SparkSession


def main():
  catalog = os.getenv("CATALOG_NAME", "pampa_ai_todo")
  raw_schema = os.getenv("RAW_SCHEMA_NAME", "raw")
  serving_schema = os.getenv("SERVING_SCHEMA_NAME", "serving")
  volume_name = os.getenv("VOLUME_NAME", "uploads")
  table_name = os.getenv("TABLE_NAME", "operacion_unidades")
  input_file = os.getenv(
    "INPUT_FILE",
    f"/Volumes/{catalog}/{raw_schema}/{volume_name}/sample_pampa.csv",
  )

  spark = SparkSession.builder.getOrCreate()
  spark.sql(f"USE CATALOG {catalog}")
  spark.sql(f"USE {serving_schema}")

  df = (
    spark.read.option("header", True)
    .option("inferSchema", True)
    .option("mode", "FAILFAST")
    .csv(input_file)
  )

  comments = {
    "fecha": "Fecha de registro",
    "planta": "Nombre de la planta",
    "unidad": "Unidad o bloque generador",
    "produccion_mwh": "Energia generada en MWh",
    "disponibilidad_pct": "Disponibilidad porcentual de la unidad",
    "observaciones": "Notas operativas",
  }

  full_table = f"{catalog}.{serving_schema}.{table_name}"
  (
    df.write.mode("overwrite")
    .format("delta")
    .option("overwriteSchema", True)
    .saveAsTable(full_table)
  )

  spark.sql(f"COMMENT ON TABLE {full_table} IS 'POC AI TODO Pampa Energia'")
  for col, text in comments.items():
    spark.sql(f"COMMENT ON COLUMN {full_table}.`{col}` IS '{text}'")


if __name__ == "__main__":
  main()
