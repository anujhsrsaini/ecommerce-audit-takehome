# AI Coding Session Transcript & Analytical Direction Log

**Assistant:** Antigravity / DeepMind Advanced Coding Agent
**Role:** Lead Analytics Engineer & Forensic Data Auditor
**Session Context:** Meridian Enterprise Technologies — Forensic Audit & Adversarial Challenge
**Raw Files:** `ai_sessions/transcript_full.jsonl`, `ai_sessions/transcript.jsonl`

---

## Summary of Analytical Steering & Defensive Hypothesis Testing

### 1. Elena Vance (CFO) — Revenue Gap & Cash Shortfall
- **Initial Hypothesis:** Suspected processor withholds, dropped transactions, or merchant fraud causing >$4M gap and ~$2.3M cash shortfall.
- **Analytical Steering & Discovery:** Joined `payment_events` captures with `erp_order_line_items` by `rev_rec_status`. Proved the $4,041,497.57 gap is 100% ASC 606 delivery timing ($1,821,953.84 pending warehouse + $1,777,293.73 in-transit) and reversed disputes ($442,250.00).
- **Treasury Reconciliation:** Tied out the $2,294,500.00 cash difference across fees ($1,582,450.00), net reserves ($160,000.00), disputes ($465,500.00), and FX drift ($86,550.00) down to $0.00 variance.

### 2. Marcus Carvalho (VP Logistics) — DHL Breach & Post-Pack Leakage
- **Initial Hypothesis:** DHL failing 19.18% of deliveries; breach of 95% SLA; demand termination for cause.
- **Analytical Steering & Discovery:** Decomposed 621,849 scans across 20,000 DHL consignments. Revealed 3,566 failures were caused by Meridian internal IT deployment `DEP-2025-07-02-ADDR-V2` (postcode truncation and omitted customs EORI). Genuine carrier fault was only 1.35% (270 pkgs). DHL is actually the top performing carrier.
- **Contract Penalty Risk:** Proved wrongful termination would trigger an $8.5M penalty against Meridian.
- **Leakage Audit:** Verified 640 post-pack cancelled orders were 100% delivered, causing $1,570,560.00 in direct P&L leakage ($1,472,000.00 COGS + $98,560.00 freight).

### 3. Lucas Ferreira (VP Growth) — Retention Collapse
- **Initial Hypothesis:** Retention collapsed to 3.8% across 385,000 tokens.
- **Analytical Steering & Discovery:** Identified identity resolution hierarchy mismatch. Lucas analyzed raw browser session cookies (`customer_entity_mappings.session_cookie_token`). When audited at the Ultimate Parent Entity level (`corporate_tax_entities`), logo retention is 94.62% and Net Revenue Retention is 124.80% ($40M to $49.92M).

### 4. Sarah Lin (VP CX) — Voucher Unit Economics
- **Initial Hypothesis:** Expand appeasements across all escalated tickets.
- **Analytical Steering & Discovery:** Uncovered `STACKED20-MSA` loophole where 1,200 enterprise server orders stacked a 20% promo voucher on a 20% contracted MSA discount, burning -$7,710,000.00 EBITDA (-$6,425/order). Established strict anti-stacking and $300 minimum order guardrails.

---

## Chronological Tool Execution & Query Verification

#### Step 1: List files in starter repo (`run_command`)
```bash
ls -la
```

#### Step 2: read_file (`read_file`)
```bash
/home/anuj/Downloads/starter-repo/README.md
```

#### Step 3: read_file (`read_file`)
```bash
/home/anuj/Downloads/starter-repo/STAKEHOLDER_NOTES.md
```

#### Step 4: read_file (`read_file`)
```bash
/home/anuj/Downloads/starter-repo/EXECUTIVE_MEMO.md
```

#### Step 5: read_file (`read_file`)
```bash
/home/anuj/Downloads/starter-repo/schema_dictionary.md
```

#### Step 6: read_file (`read_file`)
```bash
/home/anuj/Downloads/starter-repo/schema_dictionary.md
```

#### Step 7: List files in analysis (`run_command`)
```bash
ls -la analysis/
```

#### Step 8: read_file (`read_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/starter_query.sql
```

#### Step 9: read_file (`read_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/starter_query.py
```

#### Step 10: read_file (`read_file`)
```bash
/home/anuj/Downloads/starter-repo/requirements.txt
```

#### Step 11: Run starter python script (`run_command`)
```bash
python3 analysis/starter_query.py
```

#### Step 12: Check git status (`run_command`)
```bash
git status
```

#### Step 13: Check available CLI tools (`run_command`)
```bash
which git gh python3 duckdb
```

#### Step 14: Check gh auth status (`run_command`)
```bash
gh auth status
```

#### Step 15: Check for .gitignore (`run_command`)
```bash
ls -la .gitignore .git
```

#### Step 16: Read devcontainer.json (`run_command`)
```bash
cat .devcontainer/devcontainer.json
```

#### Step 17: Check ai_sessions directory (`run_command`)
```bash
ls -la ai_sessions/
```

#### Step 18: Describe all tables in database (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)
for t in con.execute('SHOW TABLES').fetchall():
    t_name = t[0]
    print(f'=== {t_name} ===')
    print(con.execute(f'DESCRIBE {t_name}').df()[['column_name', 'column_type']])
    print()
"
```

#### Step 19: Inspect payments and treasury summaries (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('--- Payment Events Summary by event_type ---')
print(con.execute('''
    SELECT event_type, currency, COUNT(*), SUM(amount_gross) as total_gross, SUM(processing_fee) as total_fee, SUM(amount_net) as total_net
    FROM payment_events
    GROUP BY event_type, currency
    ORDER BY event_type, currency
''').df())

print('\n--- Total Payment Events by Currency (charge.captured) ---')
print(con.execute('''
    SELECT currency, COUNT(*), SUM(amount_gross), SUM(processing_fee), SUM(amount_net)
    FROM payment_events
    WHERE event_type = 'charge.captured'
    GROUP BY currency
''').df())

print('\n--- FX Rates check ---')
print(con.execute('''
    SELECT currency_code, MIN(spot_rate_to_usd), AVG(spot_rate_to_usd), MAX(spot_rate_to_usd),
           AVG(corporate_budget_rate_to_usd), AVG(realized_settlement_rate_to_usd)
    FROM foreign_exchange_rates
    GROUP BY currency_code
''').df())

print('\n--- Treasury Settlements Summary ---')
print(con.execute('''
    SELECT COUNT(*),
           SUM(gross_cleared_amount) as gross_cleared,
           SUM(processing_fees_amount) as fees,
           SUM(risk_reserve_held_amount) as reserve_held,
           SUM(risk_reserve_released_amount) as reserve_released,
           SUM(dispute_clawback_amount) as disputes,
           SUM(fx_settlement_drift_amount) as fx_drift,
           SUM(net_liquidity_amount) as net_liquidity
    FROM treasury_settlements
''').df())
"
```

#### Step 20: Check treasury settlements equation (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== TREASURY SETTLEMENTS TOTALS ===')
res = con.execute('''
    SELECT 
        SUM(gross_cleared_amount) as gross_cleared,
        SUM(processing_fees_amount) as fees,
        SUM(risk_reserve_held_amount) as reserve_held,
        SUM(risk_reserve_released_amount) as reserve_released,
        SUM(dispute_clawback_amount) as dispute_clawback,
        SUM(fx_settlement_drift_amount) as fx_drift,
        SUM(net_liquidity_amount) as net_liquidity
    FROM treasury_settlements
''').fetchone()
cols = ['gross_cleared', 'fees', 'reserve_held', 'reserve_released', 'dispute_clawback', 'fx_drift', 'net_liquidity']
for c, v in zip(cols, res):
    print(f'{c}: {v:,.2f}')

print('\nCheck equation: gross - fees - reserve_held + reserve_released + dispute_clawback + fx_drift = net_liquidity?')
# dispute_clawback is negative in table? Let's check:
print('Calc:', res[0] - res[1] - res[2] + res[3] + res[4] + res[5], 'vs Net:', res[6])
"
```

#### Step 21: Inspect payment events USD conversion (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== PAYMENT EVENTS: charge.captured by currency & USD conversion ===')
df_pe = con.execute('''
    SELECT 
        currency,
        COUNT(*) as cnt,
        SUM(amount_gross) as sum_gross_orig,
        SUM(amount_gross * fx_applied_rate) as sum_gross_usd,
        SUM(processing_fee) as sum_fee_orig,
        SUM(processing_fee * fx_applied_rate) as sum_fee_usd,
        SUM(risk_reserve_hold_amount) as sum_reserve_orig,
        SUM(risk_reserve_hold_amount * fx_applied_rate) as sum_reserve_usd
    FROM payment_events
    WHERE event_type = 'charge.captured'
    GROUP BY currency
''').df()
print(df_pe)
print('Total Gross USD from captures:', df_pe['sum_gross_usd'].sum())
print('Total Fee USD from captures:', df_pe['sum_fee_usd'].sum())
print('Total Reserve USD from captures:', df_pe['sum_reserve_usd'].sum())

print('\n=== ALL PAYMENT EVENTS EVENT TYPES ===')
print(con.execute('''
    SELECT event_type, currency, COUNT(*), 
           SUM(amount_gross), SUM(amount_gross * fx_applied_rate) as gross_usd,
           SUM(processing_fee), SUM(processing_fee * fx_applied_rate) as fee_usd
    FROM payment_events
    GROUP BY event_type, currency
    ORDER BY event_type, currency
''').df())
"
```

#### Step 22: Check settlement_status in payment_events (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('--- settlement_batch_id in payment_events ---')
print(con.execute('''
    SELECT 
        settlement_status,
        COUNT(*),
        COUNT(DISTINCT settlement_batch_id),
        MIN(settlement_date_utc),
        MAX(settlement_date_utc),
        MIN(event_timestamp_utc),
        MAX(event_timestamp_utc)
    FROM payment_events
    WHERE event_type = 'charge.captured'
    GROUP BY settlement_status
''').df())

print('\n--- Unsettled / Pending Clearing ---')
print(con.execute('''
    SELECT 
        settlement_status,
        currency,
        COUNT(*),
        SUM(amount_gross),
        SUM(amount_gross * fx_applied_rate) as gross_usd
    FROM payment_events
    WHERE event_type = 'charge.captured'
    GROUP BY settlement_status, currency
''').df())
"
```

#### Step 23: Compare payment_events by batch vs treasury_settlements (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('--- Compare payment_events aggregated by settlement_batch_id vs treasury_settlements ---')
df = con.execute('''
    WITH pe_batch AS (
        SELECT 
            settlement_batch_id,
            COUNT(*) as pe_count,
            SUM(amount_gross * fx_applied_rate) as pe_gross_usd,
            SUM(processing_fee * fx_applied_rate) as pe_fee_usd,
            SUM(risk_reserve_hold_amount * fx_applied_rate) as pe_reserve_hold_usd
        FROM payment_events
        WHERE event_type = 'charge.captured'
        GROUP BY settlement_batch_id
    )
    SELECT 
        COUNT(ts.settlement_batch_id) as ts_count,
        COUNT(pe.settlement_batch_id) as pe_matched_count,
        SUM(ts.gross_cleared_amount) as ts_gross,
        SUM(pe.pe_gross_usd) as pe_gross,
        SUM(ts.processing_fees_amount) as ts_fee,
        SUM(pe.pe_fee_usd) as pe_fee,
        SUM(ts.risk_reserve_held_amount) as ts_reserve_held,
        SUM(pe.pe_reserve_hold_usd) as pe_reserve_held
    FROM treasury_settlements ts
    FULL OUTER JOIN pe_batch pe ON ts.settlement_batch_id = pe.settlement_batch_id
''').df()
print(df)
"
```

#### Step 24: Find missing settlement batches (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('--- Batches in treasury_settlements not in payment_events (charge.captured) ---')
df_diff = con.execute('''
    WITH pe_batch AS (
        SELECT settlement_batch_id, COUNT(*) as cnt, SUM(amount_gross) as s
        FROM payment_events
        WHERE event_type = 'charge.captured'
        GROUP BY settlement_batch_id
    )
    SELECT ts.*
    FROM treasury_settlements ts
    LEFT JOIN pe_batch pe ON ts.settlement_batch_id = pe.settlement_batch_id
    WHERE pe.settlement_batch_id IS NULL
    ORDER BY ts.settlement_date_utc
''').df()
print(df_diff)

print('\n--- Batches in payment_events not in treasury_settlements ---')
df_diff2 = con.execute('''
    WITH pe_batch AS (
        SELECT settlement_batch_id, COUNT(*) as cnt
        FROM payment_events
        WHERE event_type = 'charge.captured'
        GROUP BY settlement_batch_id
    )
    SELECT pe.*
    FROM pe_batch pe
    LEFT JOIN treasury_settlements ts ON ts.settlement_batch_id = pe.settlement_batch_id
    WHERE ts.settlement_batch_id IS NULL
''').df()
print(df_diff2)
"
```

#### Step 25: Compare batch id formatting (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT ts.settlement_batch_id as ts_id, pe.settlement_batch_id as pe_id
    FROM treasury_settlements ts
    LIMIT 5
''').df())

print(con.execute('''
    SELECT DISTINCT settlement_batch_id
    FROM payment_events
    LIMIT 5
''').df())
"
```

#### Step 26: Check settlement_batch_id format in both tables (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT settlement_batch_id
    FROM treasury_settlements
    LIMIT 5
''').df())

print(con.execute('''
    SELECT DISTINCT settlement_batch_id
    FROM payment_events
    LIMIT 5
''').df())
"
```

#### Step 27: Join normalised batch ids (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

df = con.execute('''
    WITH ts_norm AS (
        SELECT 
            'stl_' || SUBSTRING(settlement_batch_id, 5) AS batch_id,
            *
        FROM treasury_settlements
    ),
    pe_norm AS (
        SELECT 
            settlement_batch_id AS batch_id,
            COUNT(*) as pe_count,
            SUM(amount_gross * fx_applied_rate) as pe_gross_usd,
            SUM(processing_fee * fx_applied_rate) as pe_fee_usd,
            SUM(risk_reserve_hold_amount * fx_applied_rate) as pe_reserve_hold_usd
        FROM payment_events
        WHERE event_type = 'charge.captured'
        GROUP BY settlement_batch_id
    )
    SELECT 
        COUNT(ts.batch_id) as ts_count,
        COUNT(pe.batch_id) as pe_matched_count,
        SUM(ts.gross_cleared_amount) as ts_gross,
        SUM(pe.pe_gross_usd) as pe_gross,
        SUM(ts.processing_fees_amount) as ts_fee,
        SUM(pe.pe_fee_usd) as pe_fee,
        SUM(ts.risk_reserve_held_amount) as ts_reserve_held,
        SUM(pe.pe_reserve_hold_usd) as pe_reserve_held
    FROM ts_norm ts
    FULL OUTER JOIN pe_norm pe ON ts.batch_id = pe.batch_id
''').df()
print(df)
"
```

#### Step 28: Check unmatched batches in treasury settlements (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

df_diff = con.execute('''
    WITH ts_norm AS (
        SELECT 
            'stl_' || SUBSTRING(settlement_batch_id, 5) AS batch_id,
            *
        FROM treasury_settlements
    ),
    pe_norm AS (
        SELECT 
            settlement_batch_id AS batch_id,
            COUNT(*) as pe_count
        FROM payment_events
        WHERE event_type = 'charge.captured'
        GROUP BY settlement_batch_id
    )
    SELECT ts.settlement_batch_id, ts.settlement_date_utc, ts.gross_cleared_amount, ts.net_liquidity_amount
    FROM ts_norm ts
    LEFT JOIN pe_norm pe ON ts.batch_id = pe.batch_id
    WHERE pe.batch_id IS NULL
    ORDER BY ts.settlement_date_utc
''').df()
print('Batches in treasury_settlements not matched to payment_events:')
print(df_diff)
"
```

#### Step 29: Inspect the 14 special batches (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

df = con.execute('''
    SELECT *
    FROM treasury_settlements
    WHERE settlement_batch_id IN ('STL-2025-04-01', 'STL-2025-04-02', 'STL-2025-05-02', 'STL-2025-06-01')
''').df()
print(df.T)

print('\nCheck payment_events for any events in these batches (using any event_type):')
df2 = con.execute('''
    SELECT event_type, settlement_batch_id, COUNT(*), SUM(amount_gross)
    FROM payment_events
    WHERE LOWER(REPLACE(settlement_batch_id, '-', '_')) IN ('stl_2025_04_01', 'stl_2025_04_02', 'stl_2025_05_02', 'stl_2025_06_01')
       OR settlement_batch_id IN ('stl_2025-04-01', 'stl_2025-04-02', 'stl_2025-05-02', 'stl_2025-06-01')
    GROUP BY event_type, settlement_batch_id
''').df()
print(df2)
"
```

#### Step 30: Summarize 14 unmatched batches (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

df_all14 = con.execute('''
    WITH ts_norm AS (
        SELECT 
            'stl_' || SUBSTRING(settlement_batch_id, 5) AS batch_id,
            *
        FROM treasury_settlements
    ),
    pe_norm AS (
        SELECT 
            settlement_batch_id AS batch_id,
            COUNT(*) as pe_count
        FROM payment_events
        WHERE event_type = 'charge.captured'
        GROUP BY settlement_batch_id
    )
    SELECT 
        COUNT(*) as cnt,
        SUM(ts.gross_cleared_amount) as gross,
        SUM(ts.processing_fees_amount) as fees,
        SUM(ts.risk_reserve_held_amount) as reserve_held,
        SUM(ts.risk_reserve_released_amount) as reserve_released,
        SUM(ts.dispute_clawback_amount) as dispute_clawback,
        SUM(ts.fx_settlement_drift_amount) as fx_drift,
        SUM(ts.net_liquidity_amount) as net_liquidity
    FROM ts_norm ts
    LEFT JOIN pe_norm pe ON ts.batch_id = pe.batch_id
    WHERE pe.batch_id IS NULL
''').df()
print(df_all14.to_string())
"
```

#### Step 31: Check settlement_batch_id across all event types (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT event_type, 
           COUNT(*), 
           COUNT(settlement_batch_id),
           SUM(amount_gross),
           SUM(amount_net),
           MIN(settlement_batch_id),
           MAX(settlement_batch_id)
    FROM payment_events
    GROUP BY event_type
''').df())
"
```

#### Step 32: Inspect reserve.released events (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT *
    FROM payment_events
    WHERE event_type = 'reserve.released'
''').df().T)
"
```

#### Step 33: Inspect dispute.created events (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        COUNT(*) as cnt,
        SUM(amount_gross) as total_gross,
        SUM(processing_fee) as total_fee,
        SUM(amount_net) as total_net,
        COUNT(DISTINCT order_id) as distinct_orders,
        COUNT(DISTINCT charge_id) as distinct_charges
    FROM payment_events
    WHERE event_type = 'dispute.created'
''').df())
"
```

#### Step 34: Check FX conversions in payment_events (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        pe.currency,
        COUNT(*) as cnt,
        SUM(pe.amount_gross) as gross_orig,
        SUM(pe.amount_gross * pe.fx_applied_rate) as gross_fx_applied,
        SUM(pe.amount_gross * fx.spot_rate_to_usd) as gross_spot,
        SUM(pe.amount_gross * fx.realized_settlement_rate_to_usd) as gross_realized,
        SUM(pe.amount_gross * fx.corporate_budget_rate_to_usd) as gross_budget
    FROM payment_events pe
    JOIN foreign_exchange_rates fx 
      ON pe.currency = fx.currency_code 
     AND CAST(pe.event_timestamp_utc AS DATE) = fx.rate_date
    WHERE pe.event_type = 'charge.captured'
    GROUP BY pe.currency
''').df())
"
```

#### Step 35: Check monthly breakdown of payment events (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        date_trunc('month', event_timestamp_utc) as month,
        COUNT(*),
        SUM(amount_gross)
    FROM payment_events
    WHERE event_type = 'charge.captured'
    GROUP BY 1
    ORDER BY 1
''').df())
"
```

#### Step 36: Check monthly breakdown of treasury settlements (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        date_trunc('month', settlement_date_utc) as month,
        COUNT(*),
        SUM(gross_cleared_amount),
        SUM(net_liquidity_amount)
    FROM treasury_settlements
    GROUP BY 1
    ORDER BY 1
''').df())
"
```

#### Step 37: Check events in early January batches (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        settlement_batch_id,
        MIN(event_timestamp_utc) as min_event,
        MAX(event_timestamp_utc) as max_event,
        COUNT(*) as cnt,
        SUM(amount_gross) as sum_gross
    FROM payment_events
    WHERE settlement_batch_id IN ('stl_2025-01-02', 'stl_2025-01-03', 'stl_2025-01-04', 'stl_2025-01-05')
    GROUP BY settlement_batch_id
    ORDER BY settlement_batch_id
''').df())
"
```

#### Step 38: Check norm_ts_id match (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        ts.settlement_batch_id as ts_id,
        'stl_' || SUBSTRING(ts.settlement_batch_id, 5) as norm_ts_id,
        pe.settlement_batch_id as pe_id
    FROM treasury_settlements ts
    LEFT JOIN (SELECT DISTINCT settlement_batch_id FROM payment_events) pe
      ON 'stl_' || SUBSTRING(ts.settlement_batch_id, 5) = pe.settlement_batch_id
    WHERE ts.settlement_batch_id IN ('STL-2025-01-02', 'STL-2025-01-03')
''').df())
"
```

#### Step 39: Check truly unmatched treasury batches (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

df_unmatched = con.execute('''
    WITH pe_batches AS (
        SELECT DISTINCT settlement_batch_id
        FROM payment_events
        WHERE settlement_batch_id IS NOT NULL
    )
    SELECT ts.*
    FROM treasury_settlements ts
    LEFT JOIN pe_batches pe
      ON 'stl_' || SUBSTRING(ts.settlement_batch_id, 5) = pe.settlement_batch_id
    WHERE pe.settlement_batch_id IS NULL
''').df()
print('Unmatched treasury batches:', len(df_unmatched))
print(df_unmatched[['settlement_batch_id', 'gross_cleared_amount', 'net_liquidity_amount', 'dispute_clawback_amount']])
"
```

#### Step 40: Check unmatched PE batches (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

df_unmatched_pe = con.execute('''
    WITH ts_batches AS (
        SELECT DISTINCT 'stl_' || SUBSTRING(settlement_batch_id, 5) as norm_batch_id
        FROM treasury_settlements
    )
    SELECT pe.settlement_batch_id, COUNT(*) as cnt, SUM(amount_gross) as gross
    FROM payment_events pe
    LEFT JOIN ts_batches ts
      ON pe.settlement_batch_id = ts.norm_batch_id
    WHERE ts.norm_batch_id IS NULL AND pe.settlement_batch_id IS NOT NULL
    GROUP BY pe.settlement_batch_id
''').df()
print('Unmatched PE batches:', len(df_unmatched_pe))
print(df_unmatched_pe)
"
```

#### Step 41: Inspect GL, ERP line items, and BI recon (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== ERP ORDER LINE ITEMS REVENUE RECOGNITION ===')
print(con.execute('''
    SELECT 
        rev_rec_status,
        COUNT(*) as line_count,
        COUNT(DISTINCT order_id) as order_count,
        SUM(extended_gross_amount) as sum_gross,
        SUM(extended_net_amount) as sum_net,
        SUM(extended_cogs_amount) as sum_cogs,
        MIN(rev_rec_date) as min_date,
        MAX(rev_rec_date) as max_date
    FROM erp_order_line_items
    GROUP BY rev_rec_status
    ORDER BY rev_rec_status
''').df())

print('\n=== ERP GENERAL LEDGER ENTRIES BY ACCOUNT ===')
print(con.execute('''
    SELECT 
        account_code,
        account_name,
        COUNT(*) as entries,
        SUM(debit_amount) as total_debit,
        SUM(credit_amount) as total_credit,
        SUM(debit_amount) - SUM(credit_amount) as net_debit
    FROM erp_general_ledger_entries
    GROUP BY account_code, account_name
    ORDER BY account_code
''').df())

print('\n=== BI EXECUTIVE DAILY RECON ===')
print(con.execute('''
    SELECT 
        COUNT(*) as days,
        MIN(recon_date) as min_date,
        MAX(recon_date) as max_date,
        SUM(recon_row_count) as total_rows,
        SUM(distinct_orders_touched) as total_orders_touched,
        SUM(certified_net_recognized_revenue) as total_certified_rev,
        SUM(total_landed_freight_cost) as total_freight,
        AVG(blended_gross_margin_pct) as avg_margin_pct
    FROM bi_executive_daily_recon
''').df())
"
```

#### Step 42: Print formatted GL, ERP line items, and BI recon (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== ERP ORDER LINE ITEMS REVENUE RECOGNITION ===')
rows = con.execute('''
    SELECT 
        rev_rec_status,
        COUNT(*) as line_count,
        COUNT(DISTINCT order_id) as order_count,
        SUM(extended_gross_amount) as sum_gross,
        SUM(extended_net_amount) as sum_net,
        SUM(extended_cogs_amount) as sum_cogs
    FROM erp_order_line_items
    GROUP BY rev_rec_status
    ORDER BY rev_rec_status
''').fetchall()
for r in rows:
    print(f'{r[0]:25s} lines:{r[1]:8,d} orders:{r[2]:8,d} gross:{r[3]:15,.2f} net:{r[4]:15,.2f} cogs:{r[5]:15,.2f}')

print('\n=== ERP GENERAL LEDGER ENTRIES BY ACCOUNT ===')
rows = con.execute('''
    SELECT 
        account_code,
        account_name,
        COUNT(*) as entries,
        SUM(debit_amount) as total_debit,
        SUM(credit_amount) as total_credit,
        SUM(debit_amount) - SUM(credit_amount) as net_debit
    FROM erp_general_ledger_entries
    GROUP BY account_code, account_name
    ORDER BY account_code
''').fetchall()
for r in rows:
    print(f'{r[0]} {r[1]:28s} entries:{r[2]:8,d} debit:{r[3]:15,.2f} credit:{r[4]:15,.2f} net:{r[5]:15,.2f}')

print('\n=== BI EXECUTIVE DAILY RECON ===')
r = con.execute('''
    SELECT 
        COUNT(*) as days,
        MIN(recon_date) as min_date,
        MAX(recon_date) as max_date,
        SUM(recon_row_count) as total_rows,
        SUM(distinct_orders_touched) as total_orders_touched,
        SUM(certified_net_recognized_revenue) as total_certified_rev,
        SUM(total_landed_freight_cost) as total_freight,
        AVG(blended_gross_margin_pct) as avg_margin_pct
    FROM bi_executive_daily_recon
''').fetchone()
print(f'days: {r[0]}, min_date: {r[1]}, max_date: {r[2]}')
print(f'total_certified_rev: {r[5]:,.2f}, total_freight: {r[6]:,.2f}, avg_margin: {r[7]:.4f}%')
"
```

#### Step 43: Check orders and payments by payment terms (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== ERP ORDER HEADERS BY PAYMENT TERMS ===')
print(con.execute('''
    SELECT 
        payment_terms,
        COUNT(*) as order_count,
        SUM(gross_subtotal_amount) as gross_subtotal,
        SUM(msa_discount_amount) as msa_discount,
        SUM(promo_voucher_amount) as voucher_discount,
        SUM(net_order_total_amount) as net_order_total,
        SUM(shipping_charged_amount) as shipping_charged
    FROM erp_order_headers
    GROUP BY payment_terms
    ORDER BY payment_terms
''').df())

print('\n=== PAYMENT EVENTS BY PAYMENT TERMS (JOINED ON ORDER_ID) ===')
print(con.execute('''
    SELECT 
        h.payment_terms,
        COUNT(DISTINCT h.order_id) as erp_orders,
        COUNT(DISTINCT pe.order_id) as orders_with_pe,
        COUNT(pe.event_id) as total_events,
        SUM(CASE WHEN pe.event_type = 'charge.captured' THEN pe.amount_gross * pe.fx_applied_rate ELSE 0 END) as gross_captured_usd
    FROM erp_order_headers h
    LEFT JOIN payment_events pe ON h.order_id = pe.order_id
    GROUP BY h.payment_terms
    ORDER BY h.payment_terms
''').df())
"
```

#### Step 44: Check rev_rec for credit card prepaid orders (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== REVENUE RECOGNITION STATUS FOR CREDIT_CARD_PREPAID ORDERS ===')
print(con.execute('''
    SELECT 
        l.rev_rec_status,
        COUNT(*) as line_count,
        COUNT(DISTINCT l.order_id) as order_count,
        SUM(l.extended_gross_amount) as sum_gross,
        SUM(l.extended_net_amount) as sum_net,
        SUM(l.extended_cogs_amount) as sum_cogs
    FROM erp_order_line_items l
    JOIN erp_order_headers h ON l.order_id = h.order_id
    WHERE h.payment_terms = 'CREDIT_CARD_PREPAID'
    GROUP BY l.rev_rec_status
    ORDER BY l.rev_rec_status
''').df())
"
```

#### Step 45: Compare captured payment events and ERP orders by currency (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== PAYMENT EVENTS CAPTURES vs ORDERS ===')
print(con.execute('''
    SELECT 
        h.currency,
        COUNT(DISTINCT h.order_id) as orders,
        SUM(h.net_order_total_amount) as erp_net_usd,
        SUM(pe.amount_gross) as pe_gross_orig,
        SUM(pe.amount_gross * pe.fx_applied_rate) as pe_gross_usd,
        SUM(pe.processing_fee) as pe_fee_orig,
        SUM(pe.processing_fee * pe.fx_applied_rate) as pe_fee_usd
    FROM erp_order_headers h
    JOIN payment_events pe ON h.order_id = pe.order_id AND pe.event_type = 'charge.captured'
    GROUP BY h.currency
''').df())
"
```

#### Step 46: Calculate FX drift (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== FX DRIFT CALCULATION ===')
df = con.execute('''
    SELECT 
        h.currency,
        SUM(h.net_order_total_amount) as nominal_amount,
        SUM(pe.amount_gross * pe.fx_applied_rate) as fx_applied_usd,
        SUM(pe.amount_gross * fx.realized_settlement_rate_to_usd) as realized_usd,
        SUM(pe.amount_gross * fx.spot_rate_to_usd) as spot_usd,
        SUM(pe.amount_gross * fx.corporate_budget_rate_to_usd) as budget_usd
    FROM erp_order_headers h
    JOIN payment_events pe ON h.order_id = pe.order_id AND pe.event_type = 'charge.captured'
    JOIN foreign_exchange_rates fx ON h.currency = fx.currency_code AND CAST(pe.event_timestamp_utc AS DATE) = fx.rate_date
    GROUP BY h.currency
''').df()
print(df)
"
```

#### Step 47: Inspect GL account 6200 entries (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT *
    FROM erp_general_ledger_entries
    WHERE account_code = '6200'
''').df().T)
"
```

#### Step 48: Inspect JV-AGG-FX voucher (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT *
    FROM erp_general_ledger_entries
    WHERE journal_voucher_id = 'JV-AGG-FX'
''').df())
"
```

#### Step 49: Inspect JV-AGG-FX details (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

for col in ['journal_voucher_id', 'journal_line_id', 'account_code', 'account_name', 'debit_amount', 'credit_amount', 'memo']:
    print(con.execute('SELECT ' + col + ' FROM erp_general_ledger_entries WHERE journal_voucher_id = \'JV-AGG-FX\'').fetchall())
"
```

#### Step 50: Inspect GL account 1150 entries (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT journal_voucher_id, journal_line_id, account_code, account_name, debit_amount, credit_amount, memo
    FROM erp_general_ledger_entries
    WHERE account_code = '1150'
''').df())
"
```

#### Step 51: Inspect reserve vouchers (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT journal_voucher_id, journal_line_id, account_code, account_name, debit_amount, credit_amount, memo
    FROM erp_general_ledger_entries
    WHERE journal_voucher_id IN ('JV-AGG-RES-HOLD', 'JV-AGG-RES-REL')
''').df())
"
```

#### Step 52: Print details of reserve vouchers (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

df = con.execute('''
    SELECT journal_voucher_id, journal_line_id, account_code, account_name, debit_amount, credit_amount, memo
    FROM erp_general_ledger_entries
    WHERE journal_voucher_id IN ('JV-AGG-RES-HOLD', 'JV-AGG-RES-REL')
''').df()
for i, r in df.iterrows():
    print(dict(r))
"
```

#### Step 53: Compare BI recon and ERP line items (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== BI RECON vs ERP LINE ITEMS ===')
print('BI total_certified_rev:', con.execute('SELECT SUM(certified_net_recognized_revenue) FROM bi_executive_daily_recon').fetchone()[0])
print('ERP RECOGNIZED_DELIVERED net:', con.execute(\"SELECT SUM(extended_net_amount) FROM erp_order_line_items WHERE rev_rec_status = 'RECOGNIZED_DELIVERED'\").fetchone()[0])
print('ERP RECOGNIZED_DELIVERED gross:', con.execute(\"SELECT SUM(extended_gross_amount) FROM erp_order_line_items WHERE rev_rec_status = 'RECOGNIZED_DELIVERED'\").fetchone()[0])
print('ERP all lines net:', con.execute('SELECT SUM(extended_net_amount) FROM erp_order_line_items').fetchone()[0])
print('ERP all lines gross:', con.execute('SELECT SUM(extended_gross_amount) FROM erp_order_line_items').fetchone()[0])

print('\nCheck daily comparison between BI and ERP:')
df_cmp = con.execute('''
    WITH erp_daily AS (
        SELECT 
            CAST(rev_rec_date AS DATE) as d,
            COUNT(*) as erp_lines,
            COUNT(DISTINCT order_id) as erp_orders,
            SUM(extended_net_amount) as erp_rec_rev
        FROM erp_order_line_items
        WHERE rev_rec_status = 'RECOGNIZED_DELIVERED'
        GROUP BY 1
    )
    SELECT 
        b.recon_date,
        b.recon_row_count,
        e.erp_lines,
        b.distinct_orders_touched,
        e.erp_orders,
        b.certified_net_recognized_revenue,
        e.erp_rec_rev,
        b.certified_net_recognized_revenue - e.erp_rec_rev as rev_diff
    FROM bi_executive_daily_recon b
    LEFT JOIN erp_daily e ON b.recon_date = e.d
    WHERE b.certified_net_recognized_revenue != e.erp_rec_rev OR e.d IS NULL
    LIMIT 10
''').df()
print(df_cmp)
"
```

#### Step 54: Compare freight and row counts between BI and WMS (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== TOTAL COUNTS ===')
print('bi recon rows total:', con.execute('SELECT SUM(recon_row_count) FROM bi_executive_daily_recon').fetchone()[0])
print('bi orders touched total:', con.execute('SELECT SUM(distinct_orders_touched) FROM bi_executive_daily_recon').fetchone()[0])
print('consignments count:', con.execute('SELECT COUNT(*) FROM wms_fulfillment_consignments').fetchone()[0])
print('consignments freight sum:', con.execute('SELECT SUM(actual_freight_cost_usd) FROM wms_fulfillment_consignments').fetchone()[0])
print('bi total freight sum:', con.execute('SELECT SUM(total_landed_freight_cost) FROM bi_executive_daily_recon').fetchone()[0])
"
```

#### Step 55: Check fanout on join (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('--- Check fanout if joining orders, line items, and consignments ---')
print(con.execute('''
    SELECT 
        COUNT(*) as joined_rows,
        SUM(l.extended_net_amount) as sum_line_net,
        SUM(c.actual_freight_cost_usd) as sum_freight
    FROM erp_order_line_items l
    JOIN wms_fulfillment_consignments c ON l.order_id = c.order_id
''').df())
"
```

#### Step 56: Compare BI recon with order booking dates (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    WITH ord AS (
        SELECT 
            CAST(booking_timestamp_local AS DATE) as d,
            COUNT(*) as orders,
            SUM(net_order_total_amount) as order_net,
            SUM(gross_subtotal_amount) as order_gross
        FROM erp_order_headers
        GROUP BY 1
    )
    SELECT 
        b.recon_date,
        b.recon_row_count,
        o.orders,
        b.certified_net_recognized_revenue,
        o.order_net,
        o.order_gross
    FROM bi_executive_daily_recon b
    JOIN ord o ON b.recon_date = o.d
    LIMIT 10
''').df())
"
```

#### Step 57: Inspect difference on early dates (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    WITH ord AS (
        SELECT 
            CAST(booking_timestamp_local AS DATE) as d,
            COUNT(*) as orders,
            SUM(net_order_total_amount) as order_net
        FROM erp_order_headers
        GROUP BY 1
    )
    SELECT 
        b.recon_date,
        b.recon_row_count,
        o.orders,
        b.certified_net_recognized_revenue,
        o.order_net,
        b.certified_net_recognized_revenue - o.order_net as diff
    FROM bi_executive_daily_recon b
    JOIN ord o ON b.recon_date = o.d
    WHERE b.recon_date <= '2024-12-10'
''').df())
"
```

#### Step 58: Check row count vs order count in BI recon (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    WITH ord AS (
        SELECT 
            CAST(booking_timestamp_local AS DATE) as d,
            COUNT(*) as orders,
            SUM(net_order_total_amount) as order_net
        FROM erp_order_headers
        GROUP BY 1
    )
    SELECT 
        b.recon_date,
        b.recon_row_count,
        b.distinct_orders_touched,
        o.orders
    FROM bi_executive_daily_recon b
    JOIN ord o ON b.recon_date = o.d
    LIMIT 5
''').df())
"
```

#### Step 59: Check total lines per booking date (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    WITH ord_lines AS (
        SELECT 
            CAST(h.booking_timestamp_local AS DATE) as d,
            COUNT(h.order_id) as total_lines,
            COUNT(DISTINCT h.order_id) as total_orders
        FROM erp_order_headers h
        JOIN erp_order_line_items l ON h.order_id = l.order_id
        GROUP BY 1
    )
    SELECT 
        b.recon_date,
        b.recon_row_count,
        ol.total_lines,
        b.distinct_orders_touched,
        ol.total_orders
    FROM bi_executive_daily_recon b
    JOIN ord_lines ol ON b.recon_date = ol.d
    LIMIT 5
''').df())
"
```

#### Step 60: Find candidate date column for BI recon (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('--- Match bi_executive_daily_recon with various candidate date columns ---')
candidates = [
    ('erp_order_headers', 'booking_timestamp_local'),
    ('erp_order_headers', 'closed_at_local'),
    ('erp_order_line_items', 'rev_rec_date'),
    ('wms_fulfillment_consignments', 'label_created_at_utc'),
    ('wms_fulfillment_consignments', 'shipped_at_utc'),
    ('wms_fulfillment_consignments', 'delivered_at_utc'),
]

for tbl, col in candidates:
    df = con.execute(f'''
        WITH src AS (
            SELECT CAST({col} AS DATE) as d, COUNT(*) as cnt
            FROM {tbl}
            GROUP BY 1
        )
        SELECT COUNT(*) as matched_days, 
               CORR(b.recon_row_count, s.cnt) as corr_rows
        FROM bi_executive_daily_recon b
        JOIN src s ON b.recon_date = s.d
    ''').df()
    print(f'{tbl}.{col}: {df.to_dict(orient=\"records\")[0]}')
"
```

#### Step 61: Examine early rows of BI recon (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

df = con.execute('''
    SELECT 
        b.recon_date,
        b.recon_row_count,
        b.distinct_orders_touched,
        b.certified_net_recognized_revenue,
        b.total_landed_freight_cost,
        b.blended_gross_margin_pct
    FROM bi_executive_daily_recon b
    ORDER BY recon_date
    LIMIT 10
''').df()
print(df)
"
```

#### Step 62: Analyze carrier performance and on-time delivery (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== CONSIGNMENTS BY CARRIER ===')
df_c = con.execute('''
    SELECT 
        carrier_code,
        COUNT(*) as total_consignments,
        SUM(CASE WHEN delivery_status = 'DELIVERED' THEN 1 ELSE 0 END) as delivered,
        SUM(CASE WHEN delivery_status = 'IN_TRANSIT' THEN 1 ELSE 0 END) as in_transit,
        SUM(CASE WHEN delivery_status = 'EXCEPTION_LOST' THEN 1 ELSE 0 END) as exception_lost,
        ROUND(100.0 * SUM(CASE WHEN delivery_status != 'DELIVERED' THEN 1 ELSE 0 END) / COUNT(*), 2) as non_delivered_pct,
        ROUND(100.0 * SUM(CASE WHEN delivery_status = 'EXCEPTION_LOST' THEN 1 ELSE 0 END) / COUNT(*), 2) as lost_pct
    FROM wms_fulfillment_consignments
    GROUP BY carrier_code
''').df()
print(df_c)

print('\n=== ON-TIME DELIVERY ANALYSIS BY CARRIER ===')
df_ontime = con.execute('''
    SELECT 
        carrier_code,
        COUNT(*) as total,
        SUM(CASE WHEN delivery_status = 'DELIVERED' AND delivered_at_utc <= promised_delivery_date THEN 1 ELSE 0 END) as on_time,
        SUM(CASE WHEN delivery_status = 'DELIVERED' AND delivered_at_utc > promised_delivery_date THEN 1 ELSE 0 END) as late,
        SUM(CASE WHEN delivery_status = 'EXCEPTION_LOST' THEN 1 ELSE 0 END) as lost,
        SUM(CASE WHEN delivery_status = 'IN_TRANSIT' THEN 1 ELSE 0 END) as in_transit,
        ROUND(100.0 * SUM(CASE WHEN delivery_status = 'DELIVERED' AND delivered_at_utc <= promised_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 2) as on_time_pct,
        ROUND(100.0 * (COUNT(*) - SUM(CASE WHEN delivery_status = 'DELIVERED' AND delivered_at_utc <= promised_delivery_date THEN 1 ELSE 0 END)) / COUNT(*), 2) as failure_rate_pct
    FROM wms_fulfillment_consignments
    GROUP BY carrier_code
''').df()
print(df_ontime)
"
```

#### Step 63: Re-run on-time delivery query with cast (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

df_ontime = con.execute('''
    SELECT 
        carrier_code,
        COUNT(*) as total,
        SUM(CASE WHEN delivery_status = 'DELIVERED' AND delivered_at_utc <= promised_delivery_date::TIMESTAMPTZ THEN 1 ELSE 0 END) as on_time,
        SUM(CASE WHEN delivery_status = 'DELIVERED' AND delivered_at_utc > promised_delivery_date::TIMESTAMPTZ THEN 1 ELSE 0 END) as late,
        SUM(CASE WHEN delivery_status = 'EXCEPTION_LOST' THEN 1 ELSE 0 END) as lost,
        SUM(CASE WHEN delivery_status = 'IN_TRANSIT' THEN 1 ELSE 0 END) as in_transit,
        ROUND(100.0 * SUM(CASE WHEN delivery_status = 'DELIVERED' AND delivered_at_utc <= promised_delivery_date::TIMESTAMPTZ THEN 1 ELSE 0 END) / COUNT(*), 2) as on_time_pct,
        ROUND(100.0 * (COUNT(*) - SUM(CASE WHEN delivery_status = 'DELIVERED' AND delivered_at_utc <= promised_delivery_date::TIMESTAMPTZ THEN 1 ELSE 0 END)) / COUNT(*), 2) as failure_rate_pct
    FROM wms_fulfillment_consignments
    GROUP BY carrier_code
''').df()
print(df_ontime)
"
```

#### Step 64: Check scans and delay rates by carrier (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== SCANS BY CARRIER AND EXCEPTION ===')
df_scans = con.execute('''
    SELECT 
        c.carrier_code,
        COUNT(DISTINCT c.consignment_id) as total_consignments,
        COUNT(s.scan_id) as total_scans,
        SUM(CASE WHEN s.scan_event_code = 'DELIVERY_EXCEPTION_DELAY' THEN 1 ELSE 0 END) as delay_scans,
        COUNT(DISTINCT CASE WHEN s.scan_event_code = 'DELIVERY_EXCEPTION_DELAY' THEN c.consignment_id END) as consignments_with_delay,
        COUNT(DISTINCT CASE WHEN s.exception_code IS NOT NULL THEN c.consignment_id END) as consignments_with_exception
    FROM wms_fulfillment_consignments c
    LEFT JOIN carrier_telematics_scans s ON c.consignment_id = s.consignment_id
    GROUP BY c.carrier_code
''').df()
print(df_scans)
print('\nRatio of delay consignments:')
for i, r in df_scans.iterrows():
    pct = 100.0 * r['consignments_with_delay'] / r['total_consignments']
    print(f\"{r['carrier_code']}: {r['consignments_with_delay']} / {r['total_consignments']} = {pct:.4f}%\")
"
```

#### Step 65: Decompose exception codes by carrier (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== EXCEPTION CODES BY CARRIER ===')
df_exc = con.execute('''
    SELECT 
        c.carrier_code,
        s.exception_code,
        s.exception_details,
        COUNT(*) as scan_count,
        COUNT(DISTINCT c.consignment_id) as consignment_count
    FROM wms_fulfillment_consignments c
    JOIN carrier_telematics_scans s ON c.consignment_id = s.consignment_id
    WHERE s.exception_code IS NOT NULL OR s.scan_event_code = 'DELIVERY_EXCEPTION_DELAY'
    GROUP BY c.carrier_code, s.exception_code, s.exception_details
    ORDER BY c.carrier_code, consignment_count DESC
''').df()
print(df_exc.to_string())
"
```

#### Step 66: Decompose DHL consignments by fault (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== DHL CONSIGNMENT BREAKDOWN ===')
df = con.execute('''
    WITH dhl_scans AS (
        SELECT 
            c.consignment_id,
            MAX(CASE WHEN s.exception_code IN ('ERR_CARRIER_LOST', 'ERR_CARRIER_DAMAGED') THEN 1 ELSE 0 END) as is_carrier_fault,
            MAX(CASE WHEN s.exception_code IN ('ERR_POSTCODE_TRUNCATED', 'ERR_CUSTOMS_EORI_MISSING') THEN 1 ELSE 0 END) as is_merchant_bug,
            MAX(CASE WHEN s.exception_code IS NOT NULL THEN 1 ELSE 0 END) as has_any_exception
        FROM wms_fulfillment_consignments c
        LEFT JOIN carrier_telematics_scans s ON c.consignment_id = s.consignment_id
        WHERE c.carrier_code = 'DHL'
        GROUP BY c.consignment_id
    )
    SELECT 
        COUNT(*) as total_dhl_consignments,
        SUM(has_any_exception) as total_with_exception,
        SUM(is_carrier_fault) as carrier_fault_count,
        SUM(is_merchant_bug) as merchant_bug_count,
        SUM(CASE WHEN is_carrier_fault = 1 AND is_merchant_bug = 1 THEN 1 ELSE 0 END) as both_count,
        SUM(CASE WHEN is_merchant_bug = 1 AND is_carrier_fault = 0 THEN 1 ELSE 0 END) as merchant_bug_only_count
    FROM dhl_scans
''').df()
print(df.to_string())
"
```

#### Step 67: Check cancellation reasons and line items (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== CANCELLATION REASONS IN ERP ORDER HEADERS ===')
print(con.execute('''
    SELECT 
        cancellation_reason,
        order_status,
        COUNT(*) as order_count,
        SUM(net_order_total_amount) as sum_net,
        SUM(gross_subtotal_amount) as sum_gross
    FROM erp_order_headers
    WHERE cancellation_reason IS NOT NULL OR order_status = 'CANCELLED'
    GROUP BY cancellation_reason, order_status
''').df())

print('\n=== LINE ITEMS FOR CANCELLED ORDERS ===')
print(con.execute('''
    SELECT 
        h.cancellation_reason,
        l.rev_rec_status,
        l.rma_disposition,
        COUNT(*) as line_count,
        COUNT(DISTINCT l.order_id) as order_count,
        SUM(l.extended_net_amount) as sum_net,
        SUM(l.extended_cogs_amount) as sum_cogs
    FROM erp_order_headers h
    JOIN erp_order_line_items l ON h.order_id = l.order_id
    WHERE h.cancellation_reason IS NOT NULL OR h.order_status = 'CANCELLED'
    GROUP BY h.cancellation_reason, l.rev_rec_status, l.rma_disposition
''').df())
"
```

#### Step 68: Check delivery status of cancelled orders (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== CONSIGNMENTS FOR CANCELLED ORDERS ===')
print(con.execute('''
    SELECT 
        h.cancellation_reason,
        c.delivery_status,
        COUNT(DISTINCT h.order_id) as order_count,
        COUNT(c.consignment_id) as consignment_count,
        SUM(c.actual_freight_cost_usd) as sum_freight,
        SUM(l.extended_net_amount) as sum_order_net,
        SUM(l.extended_cogs_amount) as sum_cogs
    FROM erp_order_headers h
    JOIN erp_order_line_items l ON h.order_id = l.order_id
    LEFT JOIN wms_fulfillment_consignments c ON h.order_id = c.order_id
    WHERE h.cancellation_reason IS NOT NULL
    GROUP BY h.cancellation_reason, c.delivery_status
''').df())
"
```

#### Step 69: Calculate post-pack cancellation leakage (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== POST-PACK CANCELLATION LEAKAGE AUDIT ===')
df = con.execute('''
    WITH order_lines AS (
        SELECT 
            order_id,
            COUNT(*) as line_cnt,
            SUM(extended_net_amount) as total_net,
            SUM(extended_cogs_amount) as total_cogs
        FROM erp_order_line_items
        GROUP BY order_id
    ),
    order_consignments AS (
        SELECT 
            order_id,
            COUNT(*) as consignment_cnt,
            SUM(actual_freight_cost_usd) as total_freight,
            STRING_AGG(DISTINCT delivery_status, ',') as delivery_statuses
        FROM wms_fulfillment_consignments
        GROUP BY order_id
    )
    SELECT 
        h.cancellation_reason,
        c.delivery_statuses,
        COUNT(h.order_id) as order_count,
        SUM(h.net_order_total_amount) as sum_order_net,
        SUM(l.total_cogs) as sum_order_cogs,
        SUM(c.total_freight) as sum_order_freight,
        SUM(l.total_cogs + COALESCE(c.total_freight, 0)) as total_leakage
    FROM erp_order_headers h
    LEFT JOIN order_lines l ON h.order_id = l.order_id
    LEFT JOIN order_consignments c ON h.order_id = c.order_id
    WHERE h.cancellation_reason IS NOT NULL
    GROUP BY h.cancellation_reason, c.delivery_statuses
''').df()
print(df.to_string())
"
```

#### Step 70: Check rma_disposition for post-pack cancellations (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        l.rma_disposition,
        COUNT(*) as line_cnt,
        COUNT(DISTINCT l.order_id) as order_cnt,
        SUM(l.extended_cogs_amount) as cogs
    FROM erp_order_line_items l
    JOIN erp_order_headers h ON l.order_id = h.order_id
    WHERE h.cancellation_reason = 'CUSTOMER_REQUEST_POST_PACK'
    GROUP BY l.rma_disposition
''').df())
"
```

#### Step 71: Check payments for post-pack cancellations (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        pe.event_type,
        COUNT(*),
        SUM(pe.amount_gross),
        SUM(pe.processing_fee)
    FROM erp_order_headers h
    JOIN payment_events pe ON h.order_id = pe.order_id
    WHERE h.cancellation_reason = 'CUSTOMER_REQUEST_POST_PACK'
    GROUP BY pe.event_type
''').df())
"
```

#### Step 72: Check payment terms of post-pack cancellations (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        payment_terms,
        COUNT(*),
        SUM(net_order_total_amount)
    FROM erp_order_headers
    WHERE cancellation_reason = 'CUSTOMER_REQUEST_POST_PACK'
    GROUP BY payment_terms
''').df())
"
```

#### Step 73: Analyze repeat order rates across customer hierarchy levels (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== ENTITY POPULATIONS & REPEAT ORDER RATES IN ERP_ORDER_HEADERS ===')
levels = ['session_cookie_token', 'buyer_user_id', 'subsidiary_account_id', 'parent_tax_entity_id']

for lvl in levels:
    df = con.execute(f'''
        WITH entity_orders AS (
            SELECT 
                {lvl} as entity_id,
                COUNT(DISTINCT order_id) as order_count,
                MIN(booking_timestamp_local) as first_order,
                MAX(booking_timestamp_local) as last_order,
                SUM(net_order_total_amount) as total_spend
            FROM erp_order_headers
            WHERE {lvl} IS NOT NULL
            GROUP BY 1
        )
        SELECT 
            COUNT(*) as total_entities,
            SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) as repeat_entities,
            ROUND(100.0 * SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as repeat_pct,
            AVG(order_count) as avg_orders,
            SUM(total_spend) as total_spend
        FROM entity_orders
    ''').df()
    print(f'Level: {lvl}')
    print(df.to_string(index=False))
    print()
"
```

#### Step 74: Inspect customer_entity_mappings profile (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== CUSTOMER_ENTITY_MAPPINGS PROFILE ===')
print(con.execute('''
    SELECT 
        COUNT(*) as total_tokens,
        SUM(CASE WHEN is_returning_cookie THEN 1 ELSE 0 END) as returning_tokens,
        ROUND(100.0 * SUM(CASE WHEN is_returning_cookie THEN 1 ELSE 0 END) / COUNT(*), 4) as returning_pct,
        COUNT(DISTINCT buyer_user_id) as distinct_buyers,
        COUNT(DISTINCT subsidiary_account_id) as distinct_subsidiaries,
        COUNT(DISTINCT parent_tax_entity_id) as distinct_parents
    FROM customer_entity_mappings
''').df().to_string())

print('\n=== RESOLUTION METHODS IN MAPPINGS ===')
print(con.execute('''
    SELECT 
        resolution_method,
        COUNT(*) as cnt,
        ROUND(100.0 * COUNT(*) / 385000, 2) as pct,
        SUM(CASE WHEN is_returning_cookie THEN 1 ELSE 0 END) as returning,
        ROUND(100.0 * SUM(CASE WHEN is_returning_cookie THEN 1 ELSE 0 END) / COUNT(*), 2) as returning_pct
    FROM customer_entity_mappings
    GROUP BY resolution_method
    ORDER BY cnt DESC
''').df())
"
```

#### Step 75: Analyze corporate tax entities retention and NDR (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== CORPORATE TAX ENTITIES RETENTION & SPEND ===')
print(con.execute('''
    SELECT 
        tier,
        COUNT(*) as total_parents,
        SUM(CASE WHEN is_retained_period THEN 1 ELSE 0 END) as retained_parents,
        ROUND(100.0 * SUM(CASE WHEN is_retained_period THEN 1 ELSE 0 END) / COUNT(*), 2) as retention_rate,
        SUM(base_period_recurring_revenue) as base_revenue,
        SUM(current_period_recurring_revenue) as current_revenue,
        ROUND(100.0 * SUM(current_period_recurring_revenue) / SUM(base_period_recurring_revenue), 2) as net_retention_rate_ndr
    FROM corporate_tax_entities
    GROUP BY tier
    ORDER BY total_parents DESC
''').df().to_string())

print('\nTotal Corporate Entities:')
print(con.execute('''
    SELECT 
        COUNT(*) as total_parents,
        SUM(CASE WHEN is_retained_period THEN 1 ELSE 0 END) as retained_parents,
        ROUND(100.0 * SUM(CASE WHEN is_retained_period THEN 1 ELSE 0 END) / COUNT(*), 2) as retention_rate,
        SUM(base_period_recurring_revenue) as base_revenue,
        SUM(current_period_recurring_revenue) as current_revenue,
        ROUND(100.0 * SUM(current_period_recurring_revenue) / SUM(base_period_recurring_revenue), 2) as net_retention_rate_ndr
    FROM corporate_tax_entities
''').df().to_string())
"
```

#### Step 76: Analyze cohort repeat rates by session vs parent (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== COHORT ANALYSIS BY FIRST ORDER QUARTER ===')
print('--- By Session Cookie Token ---')
df_sess = con.execute('''
    WITH first_purchase AS (
        SELECT 
            session_cookie_token,
            DATE_TRUNC('quarter', MIN(booking_timestamp_local)) as cohort_q,
            COUNT(DISTINCT order_id) as total_orders
        FROM erp_order_headers
        GROUP BY 1
    )
    SELECT 
        cohort_q,
        COUNT(*) as cohort_size,
        SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) as repeat_count,
        ROUND(100.0 * SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as repeat_pct
    FROM first_purchase
    GROUP BY 1
    ORDER BY 1
''').df()
print(df_sess)

print('\n--- By Parent Tax Entity ---')
df_parent = con.execute('''
    WITH first_purchase AS (
        SELECT 
            parent_tax_entity_id,
            DATE_TRUNC('quarter', MIN(booking_timestamp_local)) as cohort_q,
            COUNT(DISTINCT order_id) as total_orders
        FROM erp_order_headers
        GROUP BY 1
    )
    SELECT 
        cohort_q,
        COUNT(*) as cohort_size,
        SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) as repeat_count,
        ROUND(100.0 * SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as repeat_pct
    FROM first_purchase
    GROUP BY 1
    ORDER BY 1
''').df()
print(df_parent)
"
```

#### Step 77: Analyze spend concentration by parent entity (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== SPEND CONCENTRATION AMONG PARENT TAX ENTITIES ===')
df = con.execute('''
    WITH parent_spend AS (
        SELECT 
            h.parent_tax_entity_id,
            t.legal_entity_name,
            t.tier,
            SUM(h.net_order_total_amount) as total_spend,
            COUNT(h.order_id) as order_count
        FROM erp_order_headers h
        LEFT JOIN corporate_tax_entities t ON h.parent_tax_entity_id = t.parent_tax_entity_id
        GROUP BY 1, 2, 3
    ),
    ranked AS (
        SELECT *,
               ROW_NUMBER() OVER (ORDER BY total_spend DESC) as rank,
               SUM(total_spend) OVER (ORDER BY total_spend DESC) as cum_spend,
               SUM(total_spend) OVER () as grand_total
        FROM parent_spend
    )
    SELECT 
        rank,
        parent_tax_entity_id,
        legal_entity_name,
        tier,
        order_count,
        total_spend,
        ROUND(100.0 * total_spend / grand_total, 2) as pct_of_total,
        ROUND(100.0 * cum_spend / grand_total, 2) as cum_pct
    FROM ranked
    WHERE rank <= 15 OR rank IN (50, 100, 200, 650)
    ORDER BY rank
''').df()
print(df.to_string())
"
```

#### Step 78: Inspect voucher usage in order headers (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== VOUCHER OVERVIEW IN ERP_ORDER_HEADERS ===')
print(con.execute('''
    SELECT 
        CASE WHEN voucher_code IS NOT NULL THEN 'VOUCHER_USED' ELSE 'NO_VOUCHER' END as voucher_status,
        COUNT(*) as order_count,
        SUM(gross_subtotal_amount) as gross_subtotal,
        SUM(msa_discount_amount) as msa_discount,
        SUM(promo_voucher_amount) as voucher_discount,
        SUM(net_order_total_amount) as net_order_total
    FROM erp_order_headers
    GROUP BY 1
''').df().to_string())

print('\n=== VOUCHER TYPES / CODES ===')
print(con.execute('''
    SELECT 
        voucher_code,
        COUNT(*) as order_count,
        AVG(promo_voucher_amount) as avg_voucher,
        SUM(promo_voucher_amount) as total_voucher,
        AVG(gross_subtotal_amount) as avg_subtotal,
        AVG(net_order_total_amount) as avg_net_order
    FROM erp_order_headers
    WHERE voucher_code IS NOT NULL
    GROUP BY voucher_code
    ORDER BY order_count DESC
''').df().to_string())
"
```

#### Step 79: Calculate unit economics by voucher code (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== UNIT ECONOMICS BY VOUCHER CODE ===')
df_vouch = con.execute('''
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
        COALESCE(h.voucher_code, 'NO_VOUCHER') as voucher,
        COUNT(h.order_id) as order_count,
        SUM(h.gross_subtotal_amount) as gross_subtotal,
        SUM(h.msa_discount_amount) as msa_discount,
        SUM(h.promo_voucher_amount) as voucher_discount,
        SUM(h.net_order_total_amount) as net_revenue,
        SUM(c.cogs) as total_cogs,
        SUM(f.freight) as total_freight,
        SUM(h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0)) as contribution_margin,
        ROUND(AVG(h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0)), 2) as avg_margin_per_order,
        ROUND(100.0 * SUM(h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0)) / SUM(h.net_order_total_amount), 2) as margin_pct
    FROM erp_order_headers h
    LEFT JOIN order_cogs c ON h.order_id = c.order_id
    LEFT JOIN order_freight f ON h.order_id = f.order_id
    GROUP BY 1
    ORDER BY order_count DESC
''').df()
print(df_vouch.to_string())
"
```

#### Step 80: Analyze voucher economics by tier and code (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== VOUCHER ECONOMICS BY CUSTOMER TIER & VOUCHER CODE ===')
df_tier = con.execute('''
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
        t.tier,
        COALESCE(h.voucher_code, 'NO_VOUCHER') as voucher,
        COUNT(h.order_id) as order_count,
        SUM(h.net_order_total_amount) as net_revenue,
        SUM(c.cogs) as total_cogs,
        SUM(COALESCE(f.freight, 0)) as total_freight,
        SUM(h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0)) as contribution_margin,
        ROUND(AVG(h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0)), 2) as avg_margin_per_order
    FROM erp_order_headers h
    LEFT JOIN corporate_tax_entities t ON h.parent_tax_entity_id = t.parent_tax_entity_id
    LEFT JOIN order_cogs c ON h.order_id = c.order_id
    LEFT JOIN order_freight f ON h.order_id = f.order_id
    GROUP BY 1, 2
    ORDER BY t.tier, order_count DESC
''').df()
print(df_tier.to_string())
"
```

#### Step 81: Check negative contribution margin orders (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== ORDERS WITH NEGATIVE CONTRIBUTION MARGIN ===')
df_neg = con.execute('''
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
        COALESCE(h.voucher_code, 'NO_VOUCHER') as voucher,
        COUNT(h.order_id) as total_orders,
        SUM(CASE WHEN h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0) < 0 THEN 1 ELSE 0 END) as negative_margin_orders,
        SUM(CASE WHEN h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0) < 0 THEN h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0) ELSE 0 END) as negative_margin_sum
    FROM erp_order_headers h
    LEFT JOIN order_cogs c ON h.order_id = c.order_id
    LEFT JOIN order_freight f ON h.order_id = f.order_id
    GROUP BY 1
''').df()
print(df_neg.to_string())
"
```

#### Step 82: Inspect negative margin orders in NO_VOUCHER (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== 31 NEGATIVE MARGIN ORDERS IN NO_VOUCHER ===')
print(con.execute('''
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
        h.order_id,
        h.payment_terms,
        h.gross_subtotal_amount,
        h.msa_discount_amount,
        h.net_order_total_amount,
        c.cogs,
        f.freight,
        h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0) as margin
    FROM erp_order_headers h
    LEFT JOIN order_cogs c ON h.order_id = c.order_id
    LEFT JOIN order_freight f ON h.order_id = f.order_id
    WHERE h.voucher_code IS NULL 
      AND h.net_order_total_amount - c.cogs - COALESCE(f.freight, 0) < 0
    LIMIT 10
''').df().to_string())
"
```

#### Step 83: Check range of APPEASE30 orders (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        MIN(gross_subtotal_amount) as min_subtotal,
        MAX(gross_subtotal_amount) as max_subtotal,
        MIN(promo_voucher_amount) as min_voucher,
        MAX(promo_voucher_amount) as max_voucher,
        MIN(net_order_total_amount) as min_net,
        MAX(net_order_total_amount) as max_net
    FROM erp_order_headers
    WHERE voucher_code = 'APPEASE30'
''').df().to_string())
"
```

#### Step 84: Check SKUs for APPEASE30 orders (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        l.product_category,
        l.sku_id,
        l.item_description,
        COUNT(*) as line_count,
        AVG(l.ordered_quantity) as avg_qty,
        AVG(l.unit_list_price) as avg_list,
        AVG(l.unit_cogs_amount) as avg_cogs
    FROM erp_order_line_items l
    JOIN erp_order_headers h ON l.order_id = h.order_id
    WHERE h.voucher_code = 'APPEASE30'
    GROUP BY 1, 2, 3
''').df().to_string())
"
```

#### Step 85: Inspect STACKED20-MSA accounts (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        h.parent_tax_entity_id,
        t.legal_entity_name,
        t.tier,
        COUNT(h.order_id) as order_count,
        SUM(h.gross_subtotal_amount) as gross_subtotal,
        SUM(h.msa_discount_amount) as msa_discount,
        SUM(h.promo_voucher_amount) as voucher_discount,
        SUM(h.net_order_total_amount) as net_order_total,
        SUM(l.extended_cogs_amount) as total_cogs,
        SUM(f.freight) as total_freight
    FROM erp_order_headers h
    JOIN corporate_tax_entities t ON h.parent_tax_entity_id = t.parent_tax_entity_id
    JOIN (SELECT order_id, SUM(extended_cogs_amount) as extended_cogs_amount FROM erp_order_line_items GROUP BY order_id) l ON h.order_id = l.order_id
    JOIN (SELECT order_id, SUM(actual_freight_cost_usd) as freight FROM wms_fulfillment_consignments GROUP BY order_id) f ON h.order_id = f.order_id
    WHERE h.voucher_code = 'STACKED20-MSA'
    GROUP BY 1, 2, 3
''').df().to_string())
"
```

#### Step 86: Analyze retention impact of APPEASE30 (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== APPEASEMENT VOUCHER RETENTION IMPACT ===')
print(con.execute('''
    WITH buyer_vouchers AS (
        SELECT 
            buyer_user_id,
            MAX(CASE WHEN voucher_code = 'APPEASE30' THEN 1 ELSE 0 END) as got_appease,
            COUNT(DISTINCT order_id) as total_orders,
            MIN(booking_timestamp_local) as first_order,
            MAX(booking_timestamp_local) as last_order
        FROM erp_order_headers
        GROUP BY 1
    )
    SELECT 
        got_appease,
        COUNT(*) as total_buyers,
        SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) as repeat_buyers,
        ROUND(100.0 * SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) as repeat_rate_pct,
        AVG(total_orders) as avg_orders
    FROM buyer_vouchers
    GROUP BY 1
''').df().to_string())
"
```

#### Step 87: Check revenue recognition by payment terms (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== REVENUE RECOGNITION BY PAYMENT TERMS ===')
print(con.execute('''
    SELECT 
        h.payment_terms,
        l.rev_rec_status,
        COUNT(*) as line_count,
        COUNT(DISTINCT l.order_id) as order_count,
        SUM(l.extended_net_amount) as net_amount
    FROM erp_order_line_items l
    JOIN erp_order_headers h ON l.order_id = h.order_id
    GROUP BY h.payment_terms, l.rev_rec_status
    ORDER BY h.payment_terms, l.rev_rec_status
''').df().to_string())
"
```

#### Step 88: Verify GL double-entry balance (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== GL DOUBLE-ENTRY BALANCE AUDIT ===')
res = con.execute('''
    SELECT 
        SUM(debit_amount) as total_debits,
        SUM(credit_amount) as total_credits,
        SUM(debit_amount) - SUM(credit_amount) as diff
    FROM erp_general_ledger_entries
''').fetchone()
print(f'Total Debits:  {res[0]:,.2f}')
print(f'Total Credits: {res[1]:,.2f}')
print(f'Difference:    {res[2]:,.2f}')

print('\nCheck unbalanced vouchers:')
unbal = con.execute('''
    SELECT journal_voucher_id, SUM(debit_amount) - SUM(credit_amount) as voucher_diff
    FROM erp_general_ledger_entries
    GROUP BY journal_voucher_id
    HAVING ABS(SUM(debit_amount) - SUM(credit_amount)) > 0.001
''').fetchall()
print('Unbalanced vouchers count:', len(unbal))
"
```

#### Step 89: Inspect GL by fiscal period (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== GL ENTRIES BY FISCAL PERIOD ===')
df_gl_period = con.execute('''
    SELECT 
        fiscal_period,
        COUNT(*) as entries,
        SUM(debit_amount) as debits,
        SUM(credit_amount) as credits,
        ROUND(SUM(debit_amount) - SUM(credit_amount), 2) as diff
    FROM erp_general_ledger_entries
    GROUP BY fiscal_period
    ORDER BY fiscal_period
''').df()
print(df_gl_period.to_string())
"
```

#### Step 90: Check FY2024 vs FY2025 breakdown (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print('=== FY2024 vs FY2025 RECONCILIATION ===')

print('\n--- ERP Order Headers by Year ---')
print(con.execute('''
    SELECT 
        date_trunc('year', booking_timestamp_local) as yr,
        payment_terms,
        COUNT(*) as orders,
        SUM(net_order_total_amount) as net_total
    FROM erp_order_headers
    GROUP BY 1, 2
    ORDER BY 1, 2
''').df().to_string())

print('\n--- Payment Events by Year (Captures) ---')
print(con.execute('''
    SELECT 
        date_trunc('year', event_timestamp_utc) as yr,
        currency,
        COUNT(*) as captures,
        SUM(amount_gross) as gross_orig,
        SUM(amount_gross * fx_applied_rate) as gross_usd
    FROM payment_events
    WHERE event_type = 'charge.captured'
    GROUP BY 1, 2
    ORDER BY 1, 2
''').df().to_string())

print('\n--- Treasury Settlements by Year ---')
print(con.execute('''
    SELECT 
        date_trunc('year', settlement_date_utc) as yr,
        COUNT(*) as batches,
        SUM(gross_cleared_amount) as gross_cleared,
        SUM(net_liquidity_amount) as net_liq
    FROM treasury_settlements
    GROUP BY 1
    ORDER BY 1
''').df().to_string())
"
```

#### Step 91: Check year-end settlement batches (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        ts.settlement_batch_id,
        ts.settlement_date_utc,
        ts.gross_cleared_amount,
        ts.net_liquidity_amount,
        COUNT(pe.event_id) as pe_cnt,
        MIN(pe.event_timestamp_utc) as min_event,
        MAX(pe.event_timestamp_utc) as max_event
    FROM treasury_settlements ts
    LEFT JOIN payment_events pe 
      ON 'stl_' || SUBSTRING(ts.settlement_batch_id, 5) = pe.settlement_batch_id 
     AND pe.event_type = 'charge.captured'
    WHERE ts.settlement_date_utc >= '2025-12-25'
    GROUP BY ts.settlement_batch_id, ts.settlement_date_utc, ts.gross_cleared_amount, ts.net_liquidity_amount
    ORDER BY ts.settlement_date_utc
''').df().to_string())
"
```

#### Step 92: Check monthly recognized revenue in ERP line items (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        date_trunc('month', rev_rec_date) as rev_month,
        COUNT(*) as lines,
        SUM(extended_net_amount) as net_rev
    FROM erp_order_line_items
    WHERE rev_rec_status = 'RECOGNIZED_DELIVERED'
    GROUP BY 1
    ORDER BY 1
''').df().to_string())
"
```

#### Step 93: Check recognized revenue by year and payment terms (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

print(con.execute('''
    SELECT 
        date_trunc('year', l.rev_rec_date) as rev_year,
        h.payment_terms,
        COUNT(*) as lines,
        SUM(l.extended_net_amount) as net_rev
    FROM erp_order_line_items l
    JOIN erp_order_headers h ON l.order_id = h.order_id
    WHERE l.rev_rec_status = 'RECOGNIZED_DELIVERED'
    GROUP BY 1, 2
    ORDER BY 1, 2
''').df().to_string())
"
```

#### Step 94: Test cc_lines query (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)

# Test all the specific queries we need for the memo
q_bridge = '''
WITH cc_lines AS (
    SELECT 
        l.rev_rec_status,
        COUNT(DISTINCT l.order_id) as orders,
        COUNT(*) as lines,
        SUM(l.extended_net_amount) as amount
    FROM erp_order_line_items l
    JOIN erp_order_headers h ON l.order_id = h.order_id
    WHERE h.payment_terms = 'CREDIT_CARD_PREPAID'
    GROUP BY l.rev_rec_status
)
SELECT * FROM cc_lines;
'''
print(con.execute(q_bridge).df())
"
```

#### Step 95: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/run_all_audits.py
```

#### Step 96: Execute master audit pipeline script (`run_command`)
```bash
python3 analysis/run_all_audits.py
```

#### Step 97: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/forensic_audit.sql
```

#### Step 98: Test SQL queries in forensic_audit.sql (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)
with open('analysis/forensic_audit.sql') as f:
    sql_text = f.read()

# Filter out duckdb dot-commands for python execution
queries = [q.strip() for q in sql_text.split(';') if q.strip() and not q.strip().startswith('.')]
for i, q in enumerate(queries):
    # execute
    res = con.execute(q).fetchall()
print(f'Successfully executed {len(queries)} SQL queries from forensic_audit.sql!')
"
```

#### Step 99: edit_file (`edit_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/forensic_audit.sql
```

#### Step 100: Test execution of forensic_audit.sql (`run_command`)
```bash
python3 -c "
import duckdb
con = duckdb.connect('enterprise_forensic_audit.duckdb', read_only=True)
with open('analysis/forensic_audit.sql') as f:
    sql_text = f.read()

queries = [q.strip() for q in sql_text.split(';') if q.strip()]
for i, q in enumerate(queries):
    res = con.execute(q).fetchall()
print(f'Successfully executed all {len(queries)} SQL queries from forensic_audit.sql!')
"
```

#### Step 101: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/verify_invariants.py
```

#### Step 102: Run verification suite (`run_command`)
```bash
python3 analysis/verify_invariants.py
```

#### Step 103: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/EXECUTIVE_MEMO.md
```

#### Step 104: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/EXECUTIVE_MEMO.md
```

#### Step 105: Check word count of EXECUTIVE_MEMO.md (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()
words = text.split()
print(f'Total words in EXECUTIVE_MEMO.md: {len(words)}')
"
```

#### Step 106: Word count by section (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()

sections = text.split('## ')
for s in sections:
    lines = s.split('\n')
    header = lines[0]
    words = len(s.split())
    print(f'{header[:40]:40s}: {words} words')
"
```

#### Step 107: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/EXECUTIVE_MEMO.md
```

#### Step 108: Check word count of updated memo (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()
words = text.split()
print(f'Total words in EXECUTIVE_MEMO.md: {len(words)}')
"
```

#### Step 109: Word count per section in updated memo (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()

sections = text.split('## ')
for s in sections:
    lines = s.split('\n')
    header = lines[0]
    words = len(s.split())
    print(f'{header[:40]:40s}: {words} words')
"
```

#### Step 110: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/EXECUTIVE_MEMO.md
```

#### Step 111: Check word count of memo (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()
words = text.split()
print(f'Total words in EXECUTIVE_MEMO.md: {len(words)}')
"
```

#### Step 112: Check words per section (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()

sections = text.split('## ')
for s in sections:
    lines = s.split('\n')
    header = lines[0]
    words = len(s.split())
    print(f'{header[:40]:40s}: {words} words')
"
```

#### Step 113: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/EXECUTIVE_MEMO.md
```

#### Step 114: Check word count of memo (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()
words = text.split()
print(f'Total words in EXECUTIVE_MEMO.md: {len(words)}')
"
```

#### Step 115: Words per section (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()

sections = text.split('## ')
for s in sections:
    lines = s.split('\n')
    header = lines[0]
    words = len(s.split())
    print(f'{header[:40]:40s}: {words} words')
"
```

#### Step 116: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/EXECUTIVE_MEMO.md
```

#### Step 117: Check word count of memo (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()
words = text.split()
print(f'Total words in EXECUTIVE_MEMO.md: {len(words)}')
"
```

#### Step 118: Print line by line word count (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()

for i, line in enumerate(text.split('\n')):
    if line.strip():
        print(f'{i:3d}: ({len(line.split()):2d} w) {line[:70]}')
"
```

#### Step 119: Test word count reduction (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()

# Let's replace some verbose phrases
t = text

# Section 1 replacements
t = t.replace('A forensic audit of `enterprise_forensic_audit.duckdb` (11 tables, 2.55M rows, Dec 2024–Dec 2025) across Billing, ERP, WMS, Identity, and BI Mart records resolves the C-suite deadlock:',
              'Forensic audit of `enterprise_forensic_audit.duckdb` (11 tables, 2.55M rows, Dec 2024–Dec 2025) across all decoupled systems resolves the C-suite deadlock:')

t = t.replace('Zero fraud. Gap is ASC 606 delivery timing ($3.60M) & disputes ($442.25K). Cash delta is fees ($1.58M), reserves ($160K net), disputes ($465.5K), FX ($86.55K).',
              'Zero fraud. Revenue gap is ASC 606 delivery timing ($3.60M) & disputes ($442K). Cash shortfall is fees ($1.58M), reserves ($160K net), disputes ($465.5K), FX ($86.55K).')

t = t.replace('Refute termination. 3,566 failures trace to bug `DEP-2025-07-02-ADDR-V2`. DHL genuine reliability is 98.65%. Prevents **$8.5M penalty**.',
              'Refute termination. 3,566 failures trace to internal bug `DEP-2025-07-02-ADDR-V2`. DHL genuine reliability is 98.65%. Prevents **$8.5M penalty**.')

t = t.replace('Refute collapse. Lucas audited transient browser cookies, not accounts. Enterprise spend expanded +24.8% YoY (124.8% NDR).',
              'Refute collapse. Lucas audited ephemeral cookies, not corporate accounts. Enterprise spend expanded +24.8% YoY (124.8% NDR).')

t = t.replace('Conditional approval. Expand `APPEASE30` with guardrails ($300 min). Ban promo stacking on MSA contracts to save **+$6.84M to +$7.71M**.',
              'Conditional approval. Expand `APPEASE30` with guardrails ($300 min). Ban promo stacking on MSA contracts to save **+$6.84M to +$7.71M** EBITDA.')

# Section 2 replacements
t = t.replace('Gross gateway charges ($58,420,500.00; 108,231 captured CC transactions) reconcile to recognized revenue with **$0.00 unexplained variance**. Under ASC 606, revenue is recognized upon confirmed delivery:',
              'Gross charges ($58,420,500.00; 108,231 captured CC transactions) reconcile to recognized revenue with **$0.00 unexplained variance** under ASC 606 (delivery-based recognition):')

t = t.replace('*Total Enterprise Position:* Across all terms (NET30 $16.30M, NET60 $20.52M, Wire $14.15M), total recognized revenue is **$105,341,799.66** (gross invoiced bookings: $117,391,799.66). The BI mart (`bi_executive_daily_recon`, $138.69M) is distorted by line-consignment fan-out.',
              '*Total Enterprise Revenue:* Across all terms (NET30 $16.30M, NET60 $20.52M, Wire $14.15M), total recognized revenue is **$105,341,799.66** (invoiced bookings: $117,391,799.66). The BI mart (`bi_executive_daily_recon`, $138.69M) is distorted by line-consignment join fan-out.')

# Section 3 replacements
t = t.replace('The **$2,294,500.00 cash difference** in Barclays Operating Account ****4821 is 100% accounted for by fees, reserves, disputes, and FX drift, balancing to **$0.00 variance**:',
              'The **$2,294,500.00 cash shortfall** in Barclays Operating Account ****4821 is 100% accounted for by contractual deductions, balancing to **$0.00 variance**:')

t = t.replace('*GL Proof:* Postings balance across 831,245 lines (Debits/Credits: $265,397,974.09; Imbalance: **$0.00**). GL `1010 Cash in Transit` net debit is **$56,126,000.00**; `1150 Risk Reserve Receivable` net debit is **$160,000.00**.',
              '*GL Proof:* Debits and credits balance across all 831,245 lines ($265,397,974.09; Imbalance: **$0.00**). GL `1010 Cash in Transit` net debit matches operating cash ($56,126,000.00); `1150 Risk Reserve Receivable` net debit is $160,000.00.')

# Section 4 replacements
t = t.replace('Auditing 621,849 scans decomposes the 19.18% headline DHL failure claim:',
              'Auditing 621,849 scans decomposes DHL\'s 19.18% headline failure claim:')

t = t.replace('**Verdict:** **REJECT TERMINATION.** DHL genuine fault is **1.35%** (98.65% reliability), beating FedEx (1.51%) and UPS (1.51%). 92.96% of DHL exceptions (3,566 pkgs) stem from Meridian\'s faulty address deployment. Termination triggers an **$8.5M penalty**.',
              '**Verdict:** **REJECT TERMINATION.** DHL genuine fault is **1.35%** (98.65% reliability), beating FedEx (1.51%) and UPS (1.51%). 92.96% of DHL exceptions (3,566 pkgs) trace to Meridian\'s IT bug. Termination triggers an **$8.5M wrongful penalty**.')

t = t.replace('WMS scans confirm that **100% (640/640) of post-pack cancelled orders were delivered** (`POST_PACK_DELIVERED_NO_RETURN`). On credited NET30 orders ($1.92M invoices), direct leakage is **$1,570,560.00** ($1,472,000.00 COGS + $98,560.00 freight). Support tools require a WMS lock blocking cancellation post `PACK_VERIFIED`.',
              'WMS scans confirm **100% (640/640) of post-pack cancelled orders were delivered** (`POST_PACK_DELIVERED_NO_RETURN`). On credited NET30 orders ($1.92M invoices), direct leakage is **$1,570,560.00** ($1,472,000.00 COGS + $98,560.00 freight). Fix: WMS lock blocking cancellation post `PACK_VERIFIED`.')

# Section 5 replacements
t = t.replace('Lucas Ferreira\'s 3.8% retention figure reflects transient browser cookies, not B2B accounts:',
              'Lucas Ferreira\'s 3.8% retention metric reflects transient browser cookies, not B2B accounts:')

t = t.replace('Top 5 Strategic Enterprise parents (`PAR-0001`–`PAR-0005`) generate **$55,923,485.99** (47.64% of total spend of $117.39M), expanding at 119.69% NDR. 100% of parent entities repeated across 2025; perceived decay is right-censorship of young cookies.',
              'Top 5 Strategic Enterprise parents (`PAR-0001`–`PAR-0005`) generate **$55,923,485.99** (47.64% of total spend of $117.39M), expanding at 119.69% NDR. 100% of parent entities repeated across 2025; cohort decay is right-censorship of young cookies.')

# Section 6 replacements
t = t.replace('Analysis of 125,130 orders demonstrates stark divergence in voucher profitability:',
              'Analysis of 125,130 orders shows stark divergence in voucher profitability:')

t = t.replace('- **The Loophole:** 1,200 enterprise orders stacked 20% promo voucher `STACKED20-MSA` ($6.84M) on top of 20% MSA discounts ($6.84M). Orders priced at $17,100 carried $18,525 COGS and $5,000 freight, burning **-$6,425.00/order** and handing **-$7,710,000.00 in losses** to top accounts.',
              '- **The Loophole:** 1,200 enterprise orders stacked 20% promo voucher `STACKED20-MSA` ($6.84M) on 20% MSA discounts ($6.84M). Priced at $17,100 against $18,525 COGS and $5,000 freight, this burned **-$6,425.00/order** and bled **-$7,710,000.00 in losses** to top accounts.')

t = t.replace('- **Guardrails:** `APPEASE30` buyers repeat at **85.79%** (vs 55.35% non-appeased) and net +$1.89M. Expansion is approved under two rules:\n  1. **Anti-Stacking Rule:** Hard system block preventing promo vouchers on accounts with MSA discounts (`msa_discount_pct > 0`). Kill `STACKED20-MSA`.\n  2. **Basket Minimums:** Minimum order value of **$300** for $30 appeasements (max 10% discount). Exclude heavy servers/storage from promo discounts.\n  3. **EBITDA Impact:** Eliminating stacked discounts recovers **+$6.84M revenue** and stops **$7.71M losses**, boosting EBITDA by **+$6.84M to +$7.71M annually**.',
              '- **Guardrails:** `APPEASE30` buyers repeat at **85.79%** (vs 55.35% non-appeased) and net +$1.89M. Expansion approved under two rules:\n  1. **Anti-Stacking Rule:** Hard block preventing promo vouchers on orders with MSA discounts (`msa_discount_pct > 0`). Kill `STACKED20-MSA`.\n  2. **Basket Minimums:** Minimum order value of **$300** for $30 appeasements (max 10% discount). Exclude servers/storage.\n  3. **EBITDA Impact:** Eliminating stacked discounts recovers **+$6.84M revenue** and stops **$7.71M losses**, boosting EBITDA by **+$6.84M to +$7.71M annually**.')

# Section 7 table replacements
t = t.replace('| **1** | **Enforce ERP Anti-Stacking & Kill STACKED20-MSA:** Block promo discounts on MSA contracts. | VP Growth (Ferreira) & CFO (Vance) | Immediate | **+$6.84M to +$7.71M Annual EBITDA Gain** stopping below-cost sales. |',
              '| **1** | **Enforce ERP Anti-Stacking:** Block promo discounts on MSA contracts; kill STACKED20-MSA. | VP Growth & CFO | Immediate | **+$6.84M to +$7.71M EBITDA** by stopping below-cost sales. |')

t = t.replace('| **2** | **Halt DHL Termination & Hotfix Address Bug:** Retain contract; hotfix deployment `DEP-2025-07-02-ADDR-V2`. | VP Logistics (Carvalho) & CTO | 48 Hours | **Avoids $8.5M Termination Penalty**; fixes 3,566 European shipments/yr. |',
              '| **2** | **Halt DHL Termination & Hotfix Address Bug:** Retain contract; hotfix `DEP-2025-07-02-ADDR-V2`. | VP Logistics & CTO | 48 Hours | **Avoids $8.5M Penalty**; fixes 3,566 European shipments/yr. |')

t = t.replace('| **3** | **Deploy WMS Dispatch Lock on Cancellations:** Block Support cancellations post `PACK_VERIFIED`. | VP Logistics (Carvalho) & VP CX (Lin) | 14 Days | **+$1,570,560.00 Cash Recovery** stopping delivered hardware loss. |',
              '| **3** | **Deploy WMS Dispatch Lock:** Block Support order cancellations post `PACK_VERIFIED`. | VP Logistics & VP CX | 14 Days | **+$1,570,560.00 Cash Recovery** stopping delivered hardware loss. |')

t = t.replace('| **4** | **Re-architect BI Mart to Primary GL Tables:** Deprecate `bi_executive_daily_recon`; track parent retention. | Audit Chair (Patel) & CFO (Vance) | 30 Days | **Eliminates $33.35M Reporting Error**; aligns dashboards to GL. |',
              '| **4** | **Re-architect BI Mart:** Deprecate `bi_executive_daily_recon`; track parent retention from GL/ERP. | Audit Chair & CFO | 30 Days | **Eliminates $33.35M Error**; aligns dashboards to GL to $0.00. |')

print(f'New word count: {len(t.split())}')
"
```

#### Step 120: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/condense_memo.py
```

#### Step 121: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/condense_memo.py
```

#### Step 122: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/condense_memo.py
```

#### Step 123: Run condense memo script (`run_command`)
```bash
python3 analysis/condense_memo.py
```

#### Step 124: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/condense_memo.py
```

#### Step 125: Check word count of condensed memo (`run_command`)
```bash
python3 analysis/condense_memo.py
```

#### Step 126: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/condense_memo.py
```

#### Step 127: Check word count of memo (`run_command`)
```bash
python3 analysis/condense_memo.py
```

#### Step 128: write_file (`write_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/condense_memo.py
```

#### Step 129: Check word count of memo (`run_command`)
```bash
python3 analysis/condense_memo.py
```

#### Step 130: Verify word count of EXECUTIVE_MEMO.md (`run_command`)
```bash
python3 -c "
with open('EXECUTIVE_MEMO.md') as f:
    text = f.read()
words = text.split()
print(f'Final word count in EXECUTIVE_MEMO.md: {len(words)}')
assert len(words) <= 1500, 'Word count exceeded!'
"
```

#### Step 131: read_file (`read_file`)
```bash
/home/anuj/Downloads/starter-repo/analysis/starter_query.py
```

#### Step 132: Remove temporary condense script (`run_command`)
```bash
rm -f analysis/condense_memo.py
```

#### Step 133: read_file (`read_file`)
```bash
/home/anuj/Downloads/starter-repo/README.md
```

#### Step 134: Check transcript directory (`run_command`)
```bash
ls -la /home/anuj/.gemini/antigravity-cli/brain/0d619db4-81ba-4bac-87b5-04d222f63c06/.system_generated/logs/
```

#### Step 135: Copy raw JSONL transcripts to ai_sessions (`run_command`)
```bash
cp /home/anuj/.gemini/antigravity-cli/brain/0d619db4-81ba-4bac-87b5-04d222f63c06/.system_generated/logs/transcript.jsonl ai_sessions/
cp /home/anuj/.gemini/antigravity-cli/brain/0d619db4-81ba-4bac-87b5-04d222f63c06/.system_generated/logs/transcript_full.jsonl ai_sessions/
ls -lh ai_sessions/
```

