-- Resumen de ventas por categoría y período
SELECT
    c.category_name,
    DATE_TRUNC('month', o.order_date) as month,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    SUM(oi.quantity) as total_units_sold,
    SUM(oi.subtotal) as total_revenue,
    AVG(oi.subtotal) as avg_order_value
FROM sample_data.orders o
JOIN sample_data.order_items oi ON o.order_id = oi.order_id
JOIN sample_data.products p ON oi.product_id = p.product_id
JOIN sample_data.categories c ON p.category_id = c.category_id
WHERE o.status IN ('shipped', 'delivered')
GROUP BY c.category_name, DATE_TRUNC('month', o.order_date)
ORDER BY month DESC, total_revenue DESC;
