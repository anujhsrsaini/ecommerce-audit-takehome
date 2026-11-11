"""Starter Python Analysis Script — Aura Enterprise Technologies Audit.

Run from repository root:
    python analysis/starter_query.py
"""

import duckdb
import pandas as pd

DB_PATH = "enterprise_audit.duckdb"


def main():
    con = duckdb.connect(DB_PATH, read_only=True)
    print("=" * 70)
    print("Aura Enterprise Technologies — Database Inventory Audit")
    print("=" * 70)

    tables = con.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'main'
        ORDER BY table_name;
    """).fetchall()

    print(f"Total Tables in Database: {len(tables)}\n")
    for (tbl,) in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  • {tbl:30s} {count:>10,d} rows")

    print("\n" + "=" * 70)
    print("High-Level Financial Totals Across Decoupled Systems")
    print("=" * 70)

    df_financials = con.execute("""
        SELECT 
            'Gross Stripe Captures' AS source,
            ROUND(SUM(amount_gross), 2) AS total_usd
        FROM billing_events
        WHERE event_type = 'charge.captured'
        UNION ALL
        SELECT 
            'NetSuite ERP Booked Orders',
            ROUND(SUM(net_order_total_amount), 2)
        FROM erp_orders
        WHERE order_status != 'CANCELLED'
        UNION ALL
        SELECT 
            'GAAP ASC 606 Recognized (Delivered Lines)',
            ROUND(SUM(extended_net_amount), 2)
        FROM erp_order_lines
        WHERE rev_rec_status = 'RECOGNIZED_DELIVERED';
    """).df()

    print(df_financials.to_string(index=False))
    print("\nNext step: Investigate the cross-system discrepancies detailed in STAKEHOLDER_NOTES.md")
    con.close()


if __name__ == "__main__":
    main()
