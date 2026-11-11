-- Starter Query: Aura Enterprise Technologies Database Audit
-- Run with: duckdb enterprise_audit.duckdb -f analysis/starter_query.sql

-- 1. Inspect table inventories and overall record counts
SELECT 'billing_events' AS system_table, COUNT(*) AS total_records FROM billing_events
UNION ALL
SELECT 'erp_orders', COUNT(*) FROM erp_orders
UNION ALL
SELECT 'erp_order_lines', COUNT(*) FROM erp_order_lines
UNION ALL
SELECT 'wms_fulfillment', COUNT(*) FROM wms_fulfillment
UNION ALL
SELECT 'wms_package_scans', COUNT(*) FROM wms_package_scans
UNION ALL
SELECT 'customer_accounts', COUNT(*) FROM customer_accounts
UNION ALL
SELECT 'buyer_profiles', COUNT(*) FROM buyer_profiles
UNION ALL
SELECT 'customer_identity_mappings', COUNT(*) FROM customer_identity_mappings;

-- 2. Preliminary financial totals by domain
SELECT 
    'Stripe Settled Captures' AS metric,
    ROUND(SUM(amount_gross), 2) AS total_amount_usd
FROM billing_events
WHERE event_type = 'charge.captured'
UNION ALL
SELECT 
    'NetSuite Booked Invoices',
    ROUND(SUM(net_order_total_amount), 2)
FROM erp_orders
WHERE order_status != 'CANCELLED'
UNION ALL
SELECT 
    'NetSuite Recognized GAAP Revenue (Delivered)',
    ROUND(SUM(extended_net_amount), 2)
FROM erp_order_lines
WHERE rev_rec_status = 'RECOGNIZED_DELIVERED';
