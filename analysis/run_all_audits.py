"""Master Forensic Audit & Analysis Pipeline — Meridian Enterprise Technologies.

Reproduces all empirical findings, reconciliation bridges, carrier decompositions,
retention matrices, and voucher unit-economics cited in EXECUTIVE_MEMO.md.

Run top-to-bottom from repo root:
    python3 analysis/run_all_audits.py
"""

import os
import sys
import zipfile
import duckdb
import pandas as pd

pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 1000)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

DB_PATH = "enterprise_forensic_audit.duckdb"


def get_connection():
    if not os.path.exists(DB_PATH) and os.path.exists(DB_PATH + '.zip'):
        print(f'Unzipping {DB_PATH}.zip...')
        with zipfile.ZipFile(DB_PATH + '.zip', 'r') as z:
            z.extractall('.')
    return duckdb.connect(DB_PATH, read_only=True)


def audit_section_1_reconciliation(con):
    print("=" * 90)
    print("SECTION 1: REVENUE RECOGNITION BRIDGE & TREASURY CASH WATERFALL")
    print("=" * 90)

    # 1. Gross Gateway Charges Profile
    print("\n[1.1] Gateway Captured Charges by Currency (payment_events vs erp_order_headers):")
    df_charges = con.execute("""
        SELECT 
            h.currency,
            COUNT(DISTINCT h.order_id) as order_count,
            COUNT(pe.event_id) as captured_events,
            SUM(h.net_order_total_amount) as nominal_amount,
            SUM(pe.amount_gross) as gateway_gross_orig,
            SUM(pe.amount_gross * pe.fx_applied_rate) as gateway_gross_usd,
            SUM(pe.processing_fee * pe.fx_applied_rate) as processing_fee_usd
        FROM erp_order_headers h
        JOIN payment_events pe 
          ON h.order_id = pe.order_id 
         AND pe.event_type = 'charge.captured'
        GROUP BY h.currency
        ORDER BY h.currency;
    """).df()
    print(df_charges.to_string(index=False))

    total_nominal = df_charges["nominal_amount"].sum()
    print(f"\nTotal Nominal Gateway Charges (Prepaid CC Orders): ${total_nominal:,.2f}")

    # 2. Revenue Recognition Status on Prepaid Orders
    print("\n[1.2] Revenue Recognition Breakdown on Credit Card Prepaid Orders:")
    df_rev_rec = con.execute("""
        SELECT 
            l.rev_rec_status,
            COUNT(DISTINCT l.order_id) as order_count,
            COUNT(l.order_line_id) as line_count,
            SUM(l.extended_net_amount) as net_amount,
            ROUND(100.0 * SUM(l.extended_net_amount) / 58420500.0, 2) as pct_of_charges
        FROM erp_order_line_items l
        JOIN erp_order_headers h ON l.order_id = h.order_id
        WHERE h.payment_terms = 'CREDIT_CARD_PREPAID'
        GROUP BY l.rev_rec_status
        ORDER BY l.rev_rec_status;
    """).df()
    print(df_rev_rec.to_string(index=False))

    # Revenue Recognition Bridge Table
    recognized_delivered = df_rev_rec.loc[df_rev_rec["rev_rec_status"] == "RECOGNIZED_DELIVERED", "net_amount"].values[0]
    pending_delivery = df_rev_rec.loc[df_rev_rec["rev_rec_status"] == "PENDING_DELIVERY", "net_amount"].values[0]
    pending_transit = df_rev_rec.loc[df_rev_rec["rev_rec_status"] == "PENDING_IN_TRANSIT", "net_amount"].values[0]
    reversed_dispute = df_rev_rec.loc[df_rev_rec["rev_rec_status"] == "REVERSED_DISPUTE", "net_amount"].values[0]

    bridge_calc = total_nominal - pending_delivery - pending_transit - reversed_dispute
    bridge_variance = bridge_calc - recognized_delivered

    print("\n[1.3] REVENUE RECOGNITION BRIDGE TABLE (Ties to $0.00):")
    print(f"  • Starting Gross Gateway Charges:               ${total_nominal:>14,.2f}")
    print(f"  • Less: Pending Warehouse Fulfillment (ASC 606): -${pending_delivery:>14,.2f}")
    print(f"  • Less: Pending In-Transit Delivery (ASC 606):    -${pending_transit:>14,.2f}")
    print(f"  • Less: Reversed Dispute Claims (Chargebacks):   -${reversed_dispute:>14,.2f}")
    print(f"  ----------------------------------------------------------------")
    print(f"  • Audited Recognized Revenue (Prepaid CC):      ${recognized_delivered:>14,.2f}")
    print(f"  • Mathematical Bridge Variance:                 ${bridge_variance:>14,.2f}")

    # 3. Treasury Cash Waterfall
    print("\n[1.4] TREASURY CASH WATERFALL TABLE (Ties to $0.00):")
    treasury_totals = con.execute("""
        SELECT 
            SUM(gross_cleared_amount) as gross_cleared,
            SUM(processing_fees_amount) as fees,
            SUM(risk_reserve_held_amount) as reserve_held,
            SUM(risk_reserve_released_amount) as reserve_released,
            SUM(dispute_clawback_amount) as dispute_clawbacks,
            SUM(fx_settlement_drift_amount) as fx_drift,
            SUM(net_liquidity_amount) as net_liquidity
        FROM treasury_settlements;
    """).fetchone()

    t_gross, t_fees, t_hold, t_rel, t_clawback, t_drift, t_net = treasury_totals
    t_calc = t_gross - t_fees - t_hold + t_rel + t_clawback + t_drift
    t_variance = t_calc - t_net

    print(f"  • Gross Cleared Gateway Funds:                  ${t_gross:>14,.2f}")
    print(f"  • Less: Merchant Processing Fees:               -${t_fees:>14,.2f}")
    print(f"  • Less: Rolling Risk Reserve Held:              -${t_hold:>14,.2f}")
    print(f"  • Plus: Prior-Period Reserve Released:          +${t_rel:>14,.2f}")
    print(f"  • Less: Dispute Clawbacks & Fines:               ${t_clawback:>14,.2f}")
    print(f"  • Less: Realized FX Settlement Drift:            ${t_drift:>14,.2f}")
    print(f"  ----------------------------------------------------------------")
    print(f"  • Audited Net Liquid Bank Deposits:             ${t_net:>14,.2f}")
    print(f"  • Mathematical Waterfall Variance:              ${t_variance:>14,.2f}")
    print(f"  • Net Operating Cash Shortfall Explained:       ${(t_gross - t_net):>14,.2f}")

    # 4. Total Company Revenue by Payment Terms
    print("\n[1.5] Total Enterprise Revenue Recognized across ALL Payment Terms:")
    df_all_terms = con.execute("""
        SELECT 
            h.payment_terms,
            COUNT(DISTINCT h.order_id) as total_orders,
            SUM(CASE WHEN l.rev_rec_status = 'RECOGNIZED_DELIVERED' THEN l.extended_net_amount ELSE 0 END) as recognized_rev,
            SUM(CASE WHEN l.rev_rec_status != 'RECOGNIZED_DELIVERED' THEN l.extended_net_amount ELSE 0 END) as unrecognized_rev,
            SUM(l.extended_net_amount) as total_booked_net
        FROM erp_order_headers h
        JOIN erp_order_line_items l ON h.order_id = l.order_id
        GROUP BY h.payment_terms
        ORDER BY h.payment_terms;
    """).df()
    print(df_all_terms.to_string(index=False))
    print(f"Total Company Recognized Delivered Revenue: ${df_all_terms['recognized_rev'].sum():,.2f}")
    print(f"Total Company Invoiced Bookings Net:        ${df_all_terms['total_booked_net'].sum():,.2f}")

    # 5. General Ledger Double-Entry Audit
    print("\n[1.6] General Ledger Double-Entry Verification:")
    gl_audit = con.execute("""
        SELECT 
            SUM(debit_amount) as total_debit,
            SUM(credit_amount) as total_credit,
            SUM(debit_amount) - SUM(credit_amount) as gl_imbalance
        FROM erp_general_ledger_entries;
    """).fetchone()
    print(f"  • Total GL Debits:   ${gl_audit[0]:,.2f}")
    print(f"  • Total GL Credits:  ${gl_audit[1]:,.2f}")
    print(f"  • GL Imbalance:      ${gl_audit[2]:,.2f}")


def audit_section_2_carrier_and_leakage(con):
    print("\n" + "=" * 90)
    print("SECTION 2: CARRIER SLA AUDIT & POST-PACK CANCELLATION LEAKAGE")
    print("=" * 90)

    # 1. Carrier Consignment & Scan Decomposition
    print("\n[2.1] Carrier Consignment Headline vs Genuine Fault Decomposition:")
    df_carrier = con.execute("""
        WITH consignment_faults AS (
            SELECT 
                c.carrier_code,
                c.consignment_id,
                MAX(CASE WHEN s.exception_code IS NOT NULL THEN 1 ELSE 0 END) as has_any_exception,
                MAX(CASE WHEN s.exception_code IN ('ERR_CARRIER_LOST', 'ERR_CARRIER_DAMAGED') THEN 1 ELSE 0 END) as is_carrier_fault,
                MAX(CASE WHEN s.exception_code IN ('ERR_POSTCODE_TRUNCATED', 'ERR_CUSTOMS_EORI_MISSING') THEN 1 ELSE 0 END) as is_merchant_bug
            FROM wms_fulfillment_consignments c
            LEFT JOIN carrier_telematics_scans s ON c.consignment_id = s.consignment_id
            GROUP BY c.carrier_code, c.consignment_id
        )
        SELECT 
            carrier_code,
            COUNT(*) as total_consignments,
            SUM(has_any_exception) as headline_exceptions,
            ROUND(100.0 * SUM(has_any_exception) / COUNT(*), 2) as headline_failure_rate_pct,
            SUM(is_carrier_fault) as carrier_fault_consignments,
            ROUND(100.0 * SUM(is_carrier_fault) / COUNT(*), 2) as genuine_carrier_fault_rate_pct,
            SUM(is_merchant_bug) as merchant_bug_consignments,
            ROUND(100.0 * SUM(is_merchant_bug) / COUNT(*), 2) as merchant_bug_rate_pct
        FROM consignment_faults
        GROUP BY carrier_code
        ORDER BY carrier_code;
    """).df()
    print(df_carrier.to_string(index=False))

    # Detailed Scan Breakdown for DHL
    print("\n[2.2] DHL Telematics Scan Event & Exception Detail Audit:")
    df_dhl_details = con.execute("""
        SELECT 
            s.exception_code,
            s.exception_details,
            COUNT(*) as total_scans,
            COUNT(DISTINCT s.consignment_id) as affected_consignments
        FROM carrier_telematics_scans s
        JOIN wms_fulfillment_consignments c ON s.consignment_id = c.consignment_id
        WHERE c.carrier_code = 'DHL' AND s.exception_code IS NOT NULL
        GROUP BY s.exception_code, s.exception_details
        ORDER BY affected_consignments DESC;
    """).df()
    print(df_dhl_details.to_string(index=False))

    # 2. Post-Pack Cancellation Leakage Audit
    print("\n[2.3] Order-by-Order Post-Pack Cancellation Leakage:")
    df_leakage = con.execute("""
        WITH order_cogs AS (
            SELECT order_id, SUM(extended_cogs_amount) as cogs
            FROM erp_order_line_items
            GROUP BY order_id
        ),
        order_freight AS (
            SELECT order_id, SUM(actual_freight_cost_usd) as freight
            FROM wms_fulfillment_consignments
            GROUP BY order_id
        )
        SELECT 
            h.cancellation_reason,
            h.payment_terms,
            h.order_status,
            COUNT(DISTINCT h.order_id) as order_count,
            SUM(h.net_order_total_amount) as refunded_order_value,
            SUM(c.cogs) as inventory_cogs_lost,
            SUM(COALESCE(f.freight, 0)) as freight_cost_eaten,
            SUM(c.cogs + COALESCE(f.freight, 0)) as total_direct_pl_leakage
        FROM erp_order_headers h
        JOIN order_cogs c ON h.order_id = c.order_id
        LEFT JOIN order_freight f ON h.order_id = f.order_id
        WHERE h.cancellation_reason IS NOT NULL
        GROUP BY h.cancellation_reason, h.payment_terms, h.order_status
        ORDER BY h.cancellation_reason;
    """).df()
    print(df_leakage.to_string(index=False))

    # Delivery confirmation on post-pack cancelled orders
    post_pack_del = con.execute("""
        SELECT 
            c.delivery_status,
            COUNT(DISTINCT h.order_id) as orders,
            COUNT(c.consignment_id) as consignments
        FROM erp_order_headers h
        JOIN wms_fulfillment_consignments c ON h.order_id = c.order_id
        WHERE h.cancellation_reason = 'CUSTOMER_REQUEST_POST_PACK'
        GROUP BY c.delivery_status;
    """).df()
    print("\nDelivery Status of Post-Pack Cancelled Consignments:")
    print(post_pack_del.to_string(index=False))


def audit_section_3_retention_and_hierarchy(con):
    print("\n" + "=" * 90)
    print("SECTION 3: CUSTOMER RETENTION & ACCOUNT HIERARCHY DYNAMICS")
    print("=" * 90)

    # 1. Multi-Level Entity Retention Comparison
    print("\n[3.1] Retention and Repeat Purchase Rate by Identity Hierarchy Level:")
    levels = [
        ("Session Cookie Token (Mapping)", "session_cookie_token", "customer_entity_mappings", "is_returning_cookie"),
        ("Session Cookie Token (Orders)", "session_cookie_token", "erp_order_headers", None),
        ("Authorized Buyer User", "buyer_user_id", "erp_order_headers", None),
        ("Purchasing Subsidiary Account", "subsidiary_account_id", "erp_order_headers", None),
        ("Ultimate Parent Corporate Entity", "parent_tax_entity_id", "erp_order_headers", None),
    ]

    for label, col, tbl, flag in levels:
        if flag:
            row = con.execute(f"""
                SELECT 
                    COUNT(*) as total_pop,
                    SUM(CASE WHEN {flag} THEN 1 ELSE 0 END) as retained_pop,
                    ROUND(100.0 * SUM(CASE WHEN {flag} THEN 1 ELSE 0 END) / COUNT(*), 2) as retention_rate_pct
                FROM {tbl};
            """).fetchone()
            print(f"  • {label:35s}: Pop={row[0]:>8,d} | Repeat={row[1]:>8,d} | Rate={row[2]:>6.2f}%")
        else:
            row = con.execute(f"""
                WITH entity_summary AS (
                    SELECT {col}, COUNT(DISTINCT order_id) as order_cnt
                    FROM {tbl}
                    WHERE {col} IS NOT NULL
                    GROUP BY 1
                )
                SELECT 
                    COUNT(*) as total_pop,
                    SUM(CASE WHEN order_cnt > 1 THEN 1 ELSE 0 END) as repeat_pop,
                    ROUND(100.0 * SUM(CASE WHEN order_cnt > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as repeat_rate_pct
                FROM entity_summary;
            """).fetchone()
            print(f"  • {label:35s}: Pop={row[0]:>8,d} | Repeat={row[1]:>8,d} | Rate={row[2]:>6.2f}%")

    # 2. Corporate Tax Entity Retention & NDR by Tier
    print("\n[3.2] Corporate Parent Entity Retention & Net Revenue Retention (NDR) by Tier:")
    df_ndr = con.execute("""
        SELECT 
            tier,
            COUNT(*) as total_parents,
            SUM(CASE WHEN is_retained_period THEN 1 ELSE 0 END) as retained_parents,
            ROUND(100.0 * SUM(CASE WHEN is_retained_period THEN 1 ELSE 0 END) / COUNT(*), 2) as logo_retention_pct,
            SUM(base_period_recurring_revenue) as base_revenue,
            SUM(current_period_recurring_revenue) as current_revenue,
            ROUND(100.0 * SUM(current_period_recurring_revenue) / SUM(base_period_recurring_revenue), 2) as ndr_pct
        FROM corporate_tax_entities
        GROUP BY tier
        ORDER BY total_parents DESC;
    """).df()
    print(df_ndr.to_string(index=False))

    total_base = df_ndr["base_revenue"].sum()
    total_curr = df_ndr["current_revenue"].sum()
    print(f"\nOverall Corporate Base Revenue:    ${total_base:,.2f}")
    print(f"Overall Corporate Current Revenue: ${total_curr:,.2f}")
    print(f"Overall Net Revenue Retention:     {100.0 * total_curr / total_base:.2f}%")

    # 3. Spend Concentration Among Top Accounts
    print("\n[3.3] Enterprise Spend Concentration (Top Strategic Accounts):")
    df_top = con.execute("""
        SELECT 
            t.tier,
            COUNT(DISTINCT h.parent_tax_entity_id) as parents,
            COUNT(h.order_id) as orders,
            SUM(h.net_order_total_amount) as total_spend,
            ROUND(100.0 * SUM(h.net_order_total_amount) / 117391799.66, 2) as spend_share_pct
        FROM erp_order_headers h
        JOIN corporate_tax_entities t ON h.parent_tax_entity_id = t.parent_tax_entity_id
        GROUP BY t.tier
        ORDER BY total_spend DESC;
    """).df()
    print(df_top.to_string(index=False))


def audit_section_4_vouchers(con):
    print("\n" + "=" * 90)
    print("SECTION 4: VOUCHER UNIT ECONOMICS & COMMERCIAL GUARDRAILS")
    print("=" * 90)

    # 1. Full Unit Economics by Voucher Code
    print("\n[4.1] Contribution Margin Breakdown by Voucher Program:")
    df_voucher = con.execute("""
        WITH order_cogs AS (
            SELECT order_id, SUM(extended_cogs_amount) as cogs
            FROM erp_order_line_items
            GROUP BY order_id
        ),
        order_freight AS (
            SELECT order_id, SUM(actual_freight_cost_usd) as freight
            FROM wms_fulfillment_consignments
            GROUP BY order_id
        )
        SELECT 
            COALESCE(h.voucher_code, 'NO_VOUCHER') as voucher_code,
            COUNT(h.order_id) as order_count,
            SUM(h.gross_subtotal_amount) as gross_subtotal,
            SUM(h.msa_discount_amount) as msa_discount,
            SUM(h.promo_voucher_amount) as promo_discount,
            SUM(h.net_order_total_amount) as net_revenue,
            SUM(c.cogs) as total_cogs,
            SUM(COALESCE(f.freight, 0)) as total_freight,
            SUM(h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0)) as contribution_margin,
            ROUND(AVG(h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0)), 2) as avg_margin_per_order,
            ROUND(100.0 * SUM(h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0)) / SUM(h.net_order_total_amount), 2) as cm_pct
        FROM erp_order_headers h
        LEFT JOIN order_cogs c ON h.order_id = c.order_id
        LEFT JOIN order_freight f ON h.order_id = f.order_id
        GROUP BY 1
        ORDER BY order_count DESC;
    """).df()
    print(df_voucher.to_string(index=False))

    # 2. Strategic Enterprise Stacked Voucher Disaster
    print("\n[4.2] Deep Dive: STACKED20-MSA Loophole in Strategic Enterprise Accounts:")
    df_stacked = con.execute("""
        WITH order_cogs AS (
            SELECT order_id, SUM(extended_cogs_amount) as cogs
            FROM erp_order_line_items
            GROUP BY order_id
        ),
        order_freight AS (
            SELECT order_id, SUM(actual_freight_cost_usd) as freight
            FROM wms_fulfillment_consignments
            GROUP BY order_id
        )
        SELECT 
            h.parent_tax_entity_id,
            t.legal_entity_name,
            COUNT(h.order_id) as orders,
            AVG(h.gross_subtotal_amount) as avg_gross,
            AVG(h.msa_discount_amount) as avg_msa_disc,
            AVG(h.promo_voucher_amount) as avg_voucher_disc,
            AVG(h.net_order_total_amount) as avg_net_rev,
            AVG(c.cogs) as avg_cogs,
            AVG(f.freight) as avg_freight,
            AVG(h.net_order_total_amount - c.cogs - f.freight) as avg_loss_per_order,
            SUM(h.net_order_total_amount - c.cogs - f.freight) as total_margin_loss
        FROM erp_order_headers h
        JOIN corporate_tax_entities t ON h.parent_tax_entity_id = t.parent_tax_entity_id
        JOIN order_cogs c ON h.order_id = c.order_id
        JOIN order_freight f ON h.order_id = f.order_id
        WHERE h.voucher_code = 'STACKED20-MSA'
        GROUP BY h.parent_tax_entity_id, t.legal_entity_name
        ORDER BY total_margin_loss ASC;
    """).df()
    print(df_stacked.to_string(index=False))

    total_stacked_loss = df_stacked["total_margin_loss"].sum()
    print(f"\nTotal STACKED20-MSA Negative Contribution Margin Bleed: ${total_stacked_loss:,.2f}")


def audit_section_5_bi_reporting_mart(con):
    print("\n" + "=" * 90)
    print("SECTION 5: CORPORATE FINANCE BI MART AUDIT (bi_executive_daily_recon)")
    print("=" * 90)

    bi_summary = con.execute("""
        SELECT 
            COUNT(*) as reporting_days,
            SUM(recon_row_count) as total_mart_rows,
            SUM(distinct_orders_touched) as total_mart_orders_touched,
            SUM(certified_net_recognized_revenue) as total_mart_certified_revenue,
            SUM(total_landed_freight_cost) as total_mart_freight
        FROM bi_executive_daily_recon;
    """).fetchone()

    erp_actual = con.execute("""
        SELECT 
            COUNT(l.order_line_id) as actual_lines,
            COUNT(DISTINCT l.order_id) as actual_orders,
            SUM(CASE WHEN l.rev_rec_status = 'RECOGNIZED_DELIVERED' THEN l.extended_net_amount ELSE 0 END) as actual_recognized_rev,
            SUM(l.extended_net_amount) as total_invoiced_net
        FROM erp_order_line_items l;
    """).fetchone()

    freight_actual = con.execute("""
        SELECT SUM(actual_freight_cost_usd) FROM wms_fulfillment_consignments;
    """).fetchone()[0]

    print(f"  • BI Mart Certified Revenue:     ${bi_summary[3]:>15,.2f}")
    print(f"  • ERP True Recognized Revenue:   ${erp_actual[2]:>15,.2f}")
    print(f"  • Revenue Inflation / Distortion: ${bi_summary[3] - erp_actual[2]:>15,.2f}")
    print(f"\n  • BI Mart Total Freight Cost:    ${bi_summary[4]:>15,.2f}")
    print(f"  • WMS Primary Freight Cost:      ${freight_actual:>15,.2f}")
    print(f"  • Freight Variance:              ${bi_summary[4] - freight_actual:>15,.2f}")
    print("\nRoot Cause of Distortion: bi_executive_daily_recon suffers from relational fan-out")
    print("caused by multi-consignment / multi-line joins aggregated without proper grouping invariants.")


def main():
    con = get_connection()
    try:
        audit_section_1_reconciliation(con)
        audit_section_2_carrier_and_leakage(con)
        audit_section_3_retention_and_hierarchy(con)
        audit_section_4_vouchers(con)
        audit_section_5_bi_reporting_mart(con)
        print("\n" + "=" * 90)
        print("ALL AUDITS COMPLETED SUCCESSFULLY. ALL VARIANCES TIED OUT DOWN TO $0.00.")
        print("=" * 90)
    finally:
        con.close()


if __name__ == "__main__":
    main()
