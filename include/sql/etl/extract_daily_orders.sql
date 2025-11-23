-- Extraer órdenes del día actual para procesamiento
SELECT
    o.order_id,
    o.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    o.order_date,
    o.status,
    o.total_amount,
    COUNT(oi.order_item_id) as item_count
FROM sample_data.orders o
JOIN sample_data.customers c ON o.customer_id = c.customer_id
LEFT JOIN sample_data.order_items oi ON o.order_id = oi.order_id
WHERE o.order_date = CURRENT_DATE
GROUP BY o.order_id, o.customer_id, c.first_name, c.last_name, c.email, o.order_date, o.status, o.total_amount
ORDER BY o.order_id;
