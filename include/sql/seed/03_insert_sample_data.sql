-- Insertar categorías
INSERT INTO sample_data.categories (category_name, description) VALUES
    ('Electronics', 'Electronic devices and accessories'),
    ('Books', 'Physical and digital books'),
    ('Clothing', 'Apparel and fashion items'),
    ('Home & Garden', 'Home improvement and garden supplies'),
    ('Sports', 'Sports equipment and fitness gear')
ON CONFLICT (category_name) DO NOTHING;

-- Insertar productos
INSERT INTO sample_data.products (product_name, category_id, price, stock_quantity) VALUES
    -- Electronics
    ('Laptop Pro 15"', 1, 1299.99, 25),
    ('Wireless Mouse', 1, 29.99, 150),
    ('USB-C Cable', 1, 12.99, 200),
    ('Bluetooth Headphones', 1, 89.99, 75),
    ('Smartphone Stand', 1, 19.99, 100),
    -- Books
    ('Data Engineering Handbook', 2, 49.99, 50),
    ('Python for Data Analysis', 2, 39.99, 60),
    ('SQL Mastery', 2, 34.99, 45),
    ('Cloud Architecture Patterns', 2, 54.99, 30),
    ('Machine Learning Basics', 2, 44.99, 40),
    -- Clothing
    ('Cotton T-Shirt', 3, 19.99, 200),
    ('Denim Jeans', 3, 59.99, 100),
    ('Running Shoes', 3, 89.99, 80),
    ('Winter Jacket', 3, 129.99, 50),
    ('Baseball Cap', 3, 24.99, 120),
    -- Home & Garden
    ('LED Desk Lamp', 4, 34.99, 90),
    ('Plant Pot Set', 4, 29.99, 110),
    ('Kitchen Knife Set', 4, 79.99, 45),
    ('Vacuum Cleaner', 4, 149.99, 30),
    ('Coffee Maker', 4, 69.99, 55),
    -- Sports
    ('Yoga Mat', 5, 29.99, 100),
    ('Dumbbell Set', 5, 99.99, 40),
    ('Tennis Racket', 5, 79.99, 35),
    ('Basketball', 5, 24.99, 70),
    ('Fitness Tracker', 5, 49.99, 85)
ON CONFLICT DO NOTHING;

-- Insertar clientes (usando generate_series para crear muchos)
INSERT INTO sample_data.customers (first_name, last_name, email, country, city, registration_date)
SELECT
    'Customer' || i,
    'User' || i,
    'customer' || i || '@example.com',
    CASE (i % 5)
        WHEN 0 THEN 'USA'
        WHEN 1 THEN 'Canada'
        WHEN 2 THEN 'UK'
        WHEN 3 THEN 'Germany'
        ELSE 'France'
    END,
    CASE (i % 5)
        WHEN 0 THEN 'New York'
        WHEN 1 THEN 'Toronto'
        WHEN 2 THEN 'London'
        WHEN 3 THEN 'Berlin'
        ELSE 'Paris'
    END,
    CURRENT_DATE - (random() * 365)::INTEGER
FROM generate_series(1, 100) i
ON CONFLICT (email) DO NOTHING;

-- Insertar órdenes (múltiples por algunos clientes)
INSERT INTO sample_data.orders (customer_id, order_date, status, total_amount)
SELECT
    (random() * 99 + 1)::INTEGER,
    CURRENT_DATE - (random() * 180)::INTEGER,
    CASE (random() * 4)::INTEGER
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'processing'
        WHEN 2 THEN 'shipped'
        ELSE 'delivered'
    END,
    0  -- Se calculará después con los items
FROM generate_series(1, 200)
ON CONFLICT DO NOTHING;

-- Insertar items de orden (1-5 productos por orden)
INSERT INTO sample_data.order_items (order_id, product_id, quantity, unit_price)
SELECT
    o.order_id,
    (random() * 24 + 1)::INTEGER,
    (random() * 3 + 1)::INTEGER,
    p.price
FROM sample_data.orders o
CROSS JOIN LATERAL (
    SELECT price
    FROM sample_data.products
    WHERE product_id = (random() * 24 + 1)::INTEGER
    LIMIT 1
) p
WHERE NOT EXISTS (
    SELECT 1 FROM sample_data.order_items
    WHERE order_id = o.order_id
)
LIMIT 300
ON CONFLICT DO NOTHING;

-- Actualizar totales de órdenes
UPDATE sample_data.orders o
SET total_amount = (
    SELECT COALESCE(SUM(subtotal), 0)
    FROM sample_data.order_items oi
    WHERE oi.order_id = o.order_id
);
