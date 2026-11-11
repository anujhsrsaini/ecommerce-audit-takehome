"""Automated Invariant & Mathematical Proof Verification Suite.

Validates that all cross-system relations, accounting balances, and operational
invariants hold to $0.00 variance without exception.

Run with:
    python3 analysis/verify_invariants.py
"""

import os
import sys
import zipfile
import duckdb

DB_PATH = "enterprise_forensic_audit.duckdb"


def run_checks():
    if not os.path.exists(DB_PATH) and os.path.exists(DB_PATH + '.zip'):
        print(f'Unzipping {DB_PATH}.zip...')
        with zipfile.ZipFile(DB_PATH + '.zip', 'r') as z:
            z.extractall('.')
    con = duckdb.connect(DB_PATH, read_only=True)
    failures = []
    passed = 0

    def assert_eq(name, actual, expected, tol=1e-4):
        nonlocal passed
        diff = abs(actual - expected)
        if diff > tol:
            msg = f"FAIL: {name} — Actual: {actual}, Expected: {expected}, Diff: {diff}"
            failures.append(msg)
            print(f"❌ {msg}")
        else:
            passed += 1
            print(f"✅ PASS: {name} (Value: {actual:,.2f})")

    print("=" * 80)
    print("MERIDIAN ENTERPRISE FORENSIC AUDIT — MATHEMATICAL INVARIANT VERIFIER")
    print("=" * 80)

    # 1. GL Double-Entry Invariant
    gl = con.execute("""
        SELECT 
            SUM(debit_amount) as debits,
            SUM(credit_amount) as credits,
            SUM(debit_amount) - SUM(credit_amount) as diff
        FROM erp_general_ledger_entries;
    """).fetchone()
    assert_eq("GL Total Debits == Total Credits (Zero Imbalance)", gl[2], 0.0)

    unbalanced_vouchers = con.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT journal_voucher_id
            FROM erp_general_ledger_entries
            GROUP BY journal_voucher_id
            HAVING ABS(SUM(debit_amount) - SUM(credit_amount)) > 0.001
        );
    """).fetchone()[0]
    assert_eq("Unbalanced GL Journal Vouchers Count == 0", unbalanced_vouchers, 0)

    # 2. Revenue Recognition Bridge Invariant
    cc_lines = con.execute("""
        SELECT 
            SUM(CASE WHEN l.rev_rec_status = 'RECOGNIZED_DELIVERED' THEN l.extended_net_amount ELSE 0 END) as recognized,
            SUM(CASE WHEN l.rev_rec_status = 'PENDING_DELIVERY' THEN l.extended_net_amount ELSE 0 END) as pending_delivery,
            SUM(CASE WHEN l.rev_rec_status = 'PENDING_IN_TRANSIT' THEN l.extended_net_amount ELSE 0 END) as pending_transit,
            SUM(CASE WHEN l.rev_rec_status = 'REVERSED_DISPUTE' THEN l.extended_net_amount ELSE 0 END) as reversed_dispute
        FROM erp_order_line_items l
        JOIN erp_order_headers h ON l.order_id = h.order_id
        WHERE h.payment_terms = 'CREDIT_CARD_PREPAID';
    """).fetchone()
    rec, pend_del, pend_trn, rev_disp = cc_lines
    cc_gross_orders = con.execute("""
        SELECT SUM(net_order_total_amount) 
        FROM erp_order_headers 
        WHERE payment_terms = 'CREDIT_CARD_PREPAID';
    """).fetchone()[0]
    assert_eq("Gross Prepaid CC Orders == $58,420,500.00", cc_gross_orders, 58420500.00)

    bridge_calc = cc_gross_orders - pend_del - pend_trn - rev_disp
    assert_eq("Revenue Bridge: Charges - Unfulfilled - Disputes == Recognized Revenue", bridge_calc, rec)
    assert_eq("Revenue Recognition Bridge Variance == $0.00", bridge_calc - rec, 0.0)

    # 3. Treasury Cash Waterfall Invariant
    ts = con.execute("""
        SELECT 
            SUM(gross_cleared_amount) as gross,
            SUM(processing_fees_amount) as fees,
            SUM(risk_reserve_held_amount) as hold,
            SUM(risk_reserve_released_amount) as rel,
            SUM(dispute_clawback_amount) as clawbacks,
            SUM(fx_settlement_drift_amount) as fx,
            SUM(net_liquidity_amount) as net
        FROM treasury_settlements;
    """).fetchone()
    ts_gross, ts_fees, ts_hold, ts_rel, ts_clawbacks, ts_fx, ts_net = ts
    assert_eq("Treasury Gross Cleared Amount == $58,420,500.00", ts_gross, 58420500.00)
    assert_eq("Treasury Net Liquid Deposits == $56,126,000.00", ts_net, 56126000.00)

    waterfall_calc = ts_gross - ts_fees - ts_hold + ts_rel + ts_clawbacks + ts_fx
    assert_eq("Treasury Waterfall Equation == Net Liquid Deposits", waterfall_calc, ts_net)
    assert_eq("Treasury Waterfall Variance == $0.00", waterfall_calc - ts_net, 0.0)

    # Cash shortfall matches exactly
    shortfall = ts_gross - ts_net
    deductions_sum = ts_fees + (ts_hold - ts_rel) + abs(ts_clawbacks) + abs(ts_fx)
    assert_eq("Cash Shortfall ($2,294,500.00) == Sum of Contractual Deductions", shortfall, deductions_sum)

    # 4. GL Cash in Transit matches Treasury Net Liquidity
    gl_cash = con.execute("""
        SELECT SUM(debit_amount) - SUM(credit_amount)
        FROM erp_general_ledger_entries
        WHERE account_code = '1010';
    """).fetchone()[0]
    assert_eq("GL 1010 Cash in Transit Net Debit == Treasury Net Liquid Deposits", gl_cash, ts_net)

    # 5. Row-Count Invariants
    total_orders = con.execute("SELECT COUNT(*) FROM erp_order_headers").fetchone()[0]
    assert_eq("Total ERP Orders == 125,130", total_orders, 125130)

    cc_orders = con.execute("SELECT COUNT(*) FROM erp_order_headers WHERE payment_terms = 'CREDIT_CARD_PREPAID'").fetchone()[0]
    captured_pe = con.execute("SELECT COUNT(*) FROM payment_events WHERE event_type = 'charge.captured'").fetchone()[0]
    assert_eq("Prepaid CC Orders Count == Captured Payment Events Count (108,231)", cc_orders, captured_pe)

    # 6. Carrier Scan Decomposition Invariant
    dhl_faults = con.execute("""
        WITH consignment_faults AS (
            SELECT 
                c.consignment_id,
                MAX(CASE WHEN s.exception_code IS NOT NULL THEN 1 ELSE 0 END) as has_exc,
                MAX(CASE WHEN s.exception_code IN ('ERR_CARRIER_LOST', 'ERR_CARRIER_DAMAGED') THEN 1 ELSE 0 END) as carrier_fault,
                MAX(CASE WHEN s.exception_code IN ('ERR_POSTCODE_TRUNCATED', 'ERR_CUSTOMS_EORI_MISSING') THEN 1 ELSE 0 END) as merchant_bug
            FROM wms_fulfillment_consignments c
            LEFT JOIN carrier_telematics_scans s ON c.consignment_id = s.consignment_id
            WHERE c.carrier_code = 'DHL'
            GROUP BY c.consignment_id
        )
        SELECT 
            COUNT(*) as total,
            SUM(has_exc) as headline_exc,
            SUM(carrier_fault) as carrier_fault,
            SUM(merchant_bug) as merchant_bug
        FROM consignment_faults;
    """).fetchone()
    assert_eq("DHL Total Consignments == 20,000", dhl_faults[0], 20000)
    assert_eq("DHL Headline Exceptions == 3,836 (19.18%)", dhl_faults[1], 3836)
    assert_eq("DHL Internal Merchant Bugs == 3,566 (17.83%)", dhl_faults[3], 3566)
    assert_eq("DHL Genuine Carrier Faults == 270 (1.35%)", dhl_faults[2], 270)
    assert_eq("DHL Headline Exceptions == Carrier Faults + Merchant Bugs", dhl_faults[1], dhl_faults[2] + dhl_faults[3])

    # 7. Post-Pack Cancellation Leakage Invariant
    post_pack = con.execute("""
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
            COUNT(DISTINCT h.order_id) as cnt,
            SUM(h.net_order_total_amount) as order_val,
            SUM(c.cogs) as cogs_lost,
            SUM(f.freight) as freight_eaten,
            SUM(c.cogs + f.freight) as total_leakage
        FROM erp_order_headers h
        JOIN order_cogs c ON h.order_id = c.order_id
        JOIN order_freight f ON h.order_id = f.order_id
        WHERE h.cancellation_reason = 'CUSTOMER_REQUEST_POST_PACK';
    """).fetchone()
    assert_eq("Post-Pack Cancelled Orders Count == 640", post_pack[0], 640)
    assert_eq("Post-Pack Cancelled Invoiced Value == $1,920,000.00", post_pack[1], 1920000.00)
    assert_eq("Post-Pack Inventory COGS Lost == $1,472,000.00", post_pack[2], 1472000.00)
    assert_eq("Post-Pack Carrier Freight Paid == $98,560.00", post_pack[3], 98560.00)
    assert_eq("Post-Pack Direct P&L Leakage == $1,570,560.00", post_pack[4], 1570560.00)

    # 8. Customer Hierarchy & Retention Invariants
    parent_cnt = con.execute("SELECT COUNT(*) FROM corporate_tax_entities").fetchone()[0]
    assert_eq("Total Ultimate Parent Tax Entities == 650", parent_cnt, 650)
    retained_parents = con.execute("SELECT COUNT(*) FROM corporate_tax_entities WHERE is_retained_period").fetchone()[0]
    assert_eq("Retained Parent Entities == 615 (94.62% Logo Retention)", retained_parents, 615)

    base_rev = con.execute("SELECT SUM(base_period_recurring_revenue) FROM corporate_tax_entities").fetchone()[0]
    curr_rev = con.execute("SELECT SUM(current_period_recurring_revenue) FROM corporate_tax_entities").fetchone()[0]
    assert_eq("Corporate Base Recurring Revenue == $40,000,000.00", base_rev, 40000000.00)
    assert_eq("Corporate Current Recurring Revenue == $49,920,000.00", curr_rev, 49920000.00)
    assert_eq("Corporate Net Revenue Retention == 124.80%", 100.0 * curr_rev / base_rev, 124.80)

    # 9. Voucher Unit Economics Invariant
    stacked = con.execute("""
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
            COUNT(h.order_id) as cnt,
            SUM(h.promo_voucher_amount) as voucher_disc,
            SUM(h.net_order_total_amount - c.cogs - f.freight) as cm_loss
        FROM erp_order_headers h
        JOIN order_cogs c ON h.order_id = c.order_id
        JOIN order_freight f ON h.order_id = f.order_id
        WHERE h.voucher_code = 'STACKED20-MSA';
    """).fetchone()
    assert_eq("STACKED20-MSA Orders Count == 1,200", stacked[0], 1200)
    assert_eq("STACKED20-MSA Promo Discount Handed Out == $6,840,000.00", stacked[1], 6840000.00)
    assert_eq("STACKED20-MSA Total EBITDA Contribution Margin Loss == -$7,710,000.00", stacked[2], -7710000.00)

    con.close()
    print("=" * 80)
    if failures:
        print(f"FAILED: {len(failures)} invariants failed verification!")
        sys.exit(1)
    else:
        print(f"ALL {passed} MATHEMATICAL INVARIANTS PERFECTLY VERIFIED (0.00 VARIANCE)!")
        print("=" * 80)


if __name__ == "__main__":
    run_checks()
