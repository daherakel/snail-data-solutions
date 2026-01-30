-- Tabla de clientes
CREATE TABLE IF NOT EXISTS sample_data.customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(50),
    city VARCHAR(50),
    registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de categorías de productos
CREATE TABLE IF NOT EXISTS sample_data.categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos
CREATE TABLE IF NOT EXISTS sample_data.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category_id INTEGER REFERENCES sample_data.categories(category_id),
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de órdenes
CREATE TABLE IF NOT EXISTS sample_data.orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES sample_data.customers(customer_id),
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
    total_amount NUMERIC(10,2) DEFAULT 0 CHECK (total_amount >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de items de orden (detalle)
CREATE TABLE IF NOT EXISTS sample_data.order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES sample_data.orders(order_id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES sample_data.products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    subtotal NUMERIC(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON sample_data.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON sample_data.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON sample_data.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON sample_data.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON sample_data.products(category_id);
