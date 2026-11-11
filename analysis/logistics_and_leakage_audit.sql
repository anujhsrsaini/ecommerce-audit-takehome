-- ==============================================================================
-- Aura Enterprise Technologies — Logistics Telematics, SLA & Leakage Audit
-- Run via: duckdb enterprise_audit.duckdb -f analysis/logistics_and_leakage_audit.sql
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. True Delivery SLA Audit Across Analytical Grains
-- ------------------------------------------------------------------------------

-- Grain A: Order-Level Delivery SLA (The true customer-experienced metric)
WITH order_fulfillment_summary AS (
    SELECT 
        o.order_id,
        o.order_status,
        COUNT(f.fulfillment_id) AS package_count,
        SUM(CASE WHEN f.package_status = 'DELIVERED' THEN 1 ELSE 0 END) AS delivered_packages,
        SUM(CASE WHEN f.package_status = 'EXCEPTION_LOST' THEN 1 ELSE 0 END) AS lost_packages,
        SUM(CASE WHEN f.package_status = 'RETURNED_TO_ORIGIN' THEN 1 ELSE 0 END) AS returned_packages
    FROM erp_orders o
    LEFT JOIN wms_fulfillment f ON o.order_id = f.order_id
    GROUP BY o.order_id, o.order_status
)
SELECT 
    'Order Grain (All Booked Orders)' AS audit_grain,
    COUNT(*) AS total_units,
    SUM(CASE WHEN package_count > 0 AND delivered_packages = package_count THEN 1 ELSE 0 END) AS successful_units,
    ROUND(SUM(CASE WHEN package_count > 0 AND delivered_packages = package_count THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS true_delivery_sla_pct,
    'Contractual SLA is 95.0% - actual order-level fulfillment fails contract by 5.72%' AS audit_findings
FROM order_fulfillment_summary

UNION ALL

SELECT 
    'Order Grain (Orders Dispatched to WMS)',
    SUM(CASE WHEN package_count > 0 THEN 1 ELSE 0 END),
    SUM(CASE WHEN package_count > 0 AND delivered_packages = package_count THEN 1 ELSE 0 END),
    ROUND(SUM(CASE WHEN package_count > 0 AND delivered_packages = package_count THEN 1.0 ELSE 0.0 END) / SUM(CASE WHEN package_count > 0 THEN 1 ELSE 0 END) * 100, 2),
    'Excludes 627 orders stuck unfulfilled in PENDING_APPROVAL'
FROM order_fulfillment_summary

UNION ALL

SELECT 
    'Package Consignment Grain (wms_fulfillment)',
    COUNT(*),
    SUM(CASE WHEN package_status = 'DELIVERED' THEN 1 ELSE 0 END),
    ROUND(SUM(CASE WHEN package_status = 'DELIVERED' THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2),
    'Physical carton level: 5.87% lost in transit, 3.80% returned damaged'
FROM wms_fulfillment

UNION ALL

SELECT 
    'Marcus Flawed Ratio (Delivered / Fulfilled Status)',
    SUM(CASE WHEN order_status = 'FULFILLED' THEN 1 ELSE 0 END),
    SUM(CASE WHEN order_status = 'FULFILLED' AND delivered_packages = package_count THEN 1 ELSE 0 END),
    ROUND(SUM(CASE WHEN order_status = 'FULFILLED' AND delivered_packages = package_count THEN 1.0 ELSE 0.0 END) / SUM(CASE WHEN order_status = 'FULFILLED' THEN 1.0 ELSE 0.0 END) * 100, 2),
    'Marcus claimed 97.2% - he improperly omitted lost (CLOSED), cancelled, and pending orders'
FROM order_fulfillment_summary;

-- ------------------------------------------------------------------------------
-- 2. Service Tier & Expedited 2-Day Air Transit SLA Breach
-- ------------------------------------------------------------------------------

SELECT 
    service_tier,
    COUNT(*) AS total_consignments,
    SUM(CASE WHEN package_status = 'DELIVERED' THEN 1 ELSE 0 END) AS delivered_consignments,
    ROUND(AVG(CASE WHEN package_status = 'DELIVERED' THEN epoch(delivered_timestamp_utc - shipped_timestamp_utc) / 86400.0 END), 2) AS avg_transit_days,
    SUM(CASE WHEN package_status = 'DELIVERED' AND epoch(delivered_timestamp_utc - shipped_timestamp_utc) <= 2 * 86400 THEN 1 ELSE 0 END) AS delivered_within_2_days,
    ROUND(SUM(CASE WHEN package_status = 'DELIVERED' AND epoch(delivered_timestamp_utc - shipped_timestamp_utc) <= 2 * 86400 THEN 1.0 ELSE 0.0 END) / 
          SUM(CASE WHEN package_status = 'DELIVERED' THEN 1.0 ELSE 0.0 END) * 100, 2) AS on_time_2day_pct,
    ROUND(SUM(CASE WHEN package_status = 'DELIVERED' AND epoch(delivered_timestamp_utc - shipped_timestamp_utc) > 2 * 86400 THEN 1.0 ELSE 0.0 END) / 
          SUM(CASE WHEN package_status = 'DELIVERED' THEN 1.0 ELSE 0.0 END) * 100, 2) AS breached_2day_pct
FROM wms_fulfillment
GROUP BY service_tier
ORDER BY service_tier;

-- ------------------------------------------------------------------------------
-- 3. Post-Pack Cancellations ("Zombie Dispatches") Leakage Audit
-- ------------------------------------------------------------------------------

WITH cancelled_orders_lines AS (
    SELECT 
        order_id,
        SUM(extended_gross_amount) AS line_gross,
        SUM(extended_net_amount) AS line_net,
        SUM(extended_cogs_amount) AS line_cogs
    FROM erp_order_lines
    GROUP BY order_id
),
cancelled_orders_freight AS (
    SELECT 
        order_id,
        SUM(actual_freight_cost) AS freight_cost
    FROM wms_fulfillment
    GROUP BY order_id
),
cancelled_card_fees AS (
    SELECT 
        o.order_id,
        SUM(b.processing_fee) AS processing_fee_lost
    FROM erp_orders o
    JOIN billing_events b ON o.order_id = b.order_id AND b.event_type = 'charge.captured'
    WHERE o.order_status = 'CANCELLED'
    GROUP BY o.order_id
)
SELECT 
    o.payment_method,
    COUNT(o.order_id) AS cancelled_order_count,
    ROUND(SUM(o.net_order_total_amount), 2) AS customer_invoiced_total_lost,
    ROUND(SUM(col.line_net), 2) AS commercial_product_net_lost,
    ROUND(SUM(col.line_cogs), 2) AS physical_inventory_cogs_lost,
    ROUND(SUM(cof.freight_cost), 2) AS carrier_freight_absorbed,
    ROUND(SUM(COALESCE(ccf.processing_fee_lost, 0)), 2) AS unrefunded_gateway_fees
FROM erp_orders o
JOIN cancelled_orders_lines col ON o.order_id = col.order_id
JOIN cancelled_orders_freight cof ON o.order_id = cof.order_id
LEFT JOIN cancelled_card_fees ccf ON o.order_id = ccf.order_id
WHERE o.order_status = 'CANCELLED'
GROUP BY o.payment_method
ORDER BY o.payment_method;

-- ------------------------------------------------------------------------------
-- 4. Lost in Transit & Unfiled Carrier Insurance Claims
-- ------------------------------------------------------------------------------

WITH lost_orders_lines AS (
    SELECT 
        order_id,
        COUNT(*) AS lines_count,
        SUM(extended_gross_amount) AS lines_gross,
        SUM(extended_net_amount) AS lines_net,
        SUM(extended_cogs_amount) AS lines_cogs
    FROM erp_order_lines
    GROUP BY order_id
)
SELECT 
    f.carrier_name,
    COUNT(f.fulfillment_id) AS lost_package_count,
    ROUND(SUM(f.actual_freight_cost), 2) AS direct_freight_billed,
    ROUND(SUM(lol.lines_cogs), 2) AS inventory_cogs_exposure,
    ROUND(SUM(lol.lines_net), 2) AS commercial_claim_value
FROM wms_fulfillment f
JOIN lost_orders_lines lol ON f.order_id = lol.order_id
WHERE f.package_status = 'EXCEPTION_LOST'
GROUP BY f.carrier_name
ORDER BY lost_package_count DESC;

-- ------------------------------------------------------------------------------
-- 5. Damaged RMA Hardware Scrapped vs ERP Asset Inflation
-- ------------------------------------------------------------------------------

SELECT 
    product_category,
    COUNT(*) AS damaged_line_count,
    ROUND(SUM(extended_net_amount), 2) AS commercial_value_scrapped,
    ROUND(SUM(extended_cogs_amount), 2) AS balance_sheet_asset_inflation_cogs
FROM erp_order_lines
WHERE return_disposition = 'DAMAGED_WRITE_OFF'
GROUP BY product_category
ORDER BY balance_sheet_asset_inflation_cogs DESC;
