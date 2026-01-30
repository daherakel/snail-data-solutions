-- Tabla para almacenar productos procesados por ETL
CREATE TABLE IF NOT EXISTS sample_data.etl_products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    price NUMERIC(10,2),
    discount NUMERIC(10,2),
    final_price NUMERIC(10,2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
