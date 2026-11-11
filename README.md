# Aura Enterprise Technologies — Enterprise Cross-System Audit & Analytics Challenge

**Role:** Senior Data Analyst / Lead Analytics Engineer (B2B Assessment · Level 1 Take-Home)  
**Format:** Asynchronous repository assessment — DuckDB + SQL / Python + Forensic Executive Memo  
**Time guidance:** You have **24 hours** from the moment you accept your assignment to submit your public GitHub repository.

---

## 1. Your Mandate

You are engaged as the independent Lead Analytics Engineer by the Audit Committee of the Board of Directors at **Aura Enterprise Technologies**. Aura is a high-growth B2B enterprise marketplace operating across four decoupled systems of record:
1. **Billing & Payment Processor (Stripe):** Event-level authorizations, captures, processing fee schedules, rolling 5% risk reserves, and dispute clawbacks (`billing_events`).
2. **Accrual ERP & Financial Ledger (NetSuite):** Sales order bookings, line-item cancellations, ASC 606 revenue recognition status, and returns (`erp_orders`, `erp_order_lines`).
3. **Logistics Telematics & WMS (Manhattan Associates):** Distribution center allocation, multi-facility split shipments, and real-time barcode scan streams (`wms_fulfillment`, `wms_package_scans`).
4. **Customer Master Data Management (MDM):** Corporate conglomerate hierarchies, subsidiary accounts, authorized procurement buyer profiles, and cross-session identity mappings (`customer_accounts`, `buyer_profiles`, `customer_identity_mappings`).

The executive leadership team is deadlocked over conflicting operational hypotheses and financial discrepancies. Finance, Logistics, Growth, and Customer Support are operating from isolated systems, producing contradictory metrics:

- **Elena Vance (Chief Financial Officer):** Reports a multi-million-dollar gap between gross payment gateway charges and NetSuite recognized revenue, alongside a severe operating cash shortfall. She suspects payment processor webhook failures or merchant fraud.
- **Marcus Carvalho (VP Logistics & Supply Chain):** Claims on-time delivery SLA exceeds 97% based on carrier scan telematics, and asserts Customer Support is prematurely refunding orders while packages are already in flight.
- **Sarah Lin (VP Customer Experience):** Claims delivery delays and hardware return friction are driving customer churn, arguing for expanded customer appeasement vouchers.
- **Lucas Ferreira (VP Marketing & Enterprise Growth):** Claims enterprise retention has collapsed to near zero, reporting that over 90% of checkout sessions never return.
- **Vikram Patel (Chief Legal Officer & Audit Chair):** Demands a GAAP ASC 606 compliant revenue reconciliation down to $0.00, an audit of inventory leakage from zombie dispatches, and margin guardrails on all commercial policies.

Your mission is to query `enterprise_audit.duckdb`, uncover the cross-system root causes, prove the mathematical truth, and author a definitive decision memo for the Board.

**Modern Tooling Encouraged:** You are welcome and expected to use modern programming languages, SQL environments, and AI coding assistants (Claude, ChatGPT, Cursor, Copilot). Your work is evaluated on the analytical rigor, defensive relational modeling, and executive clarity of your code and decision memo.

---

## 2. Package Contents

| Asset | Purpose |
| :--- | :--- |
| `enterprise_audit.duckdb` | The complete enterprise database (8 tables, ~1.8M total records across 15 months: Oct 2024 – Dec 2025). |
| `README.md` | This assignment specification and candidate guide. |
| `schema_dictionary.md` | Detailed column definitions, data types, grains, foreign keys, and temporal zones for all 8 tables. |
| `STAKEHOLDER_NOTES.md` | Internal Slack / Email memo thread among the C-suite. Treat all executive claims as hypotheses to audit, not verified facts. |
| `analysis/starter_query.sql` | Minimal SQL query template for the DuckDB CLI. |
| `analysis/starter_query.py` | Minimal Python script template (`duckdb` + `pandas`). |
| `requirements.txt` | Python environment dependencies. |
| `.devcontainer/devcontainer.json` | VS Code / GitHub Codespaces container configuration. |

---

## 3. Required GitHub Deliverables

Your final deliverable is a **single public GitHub repository** containing:

```
├── README.md                     # Instructions to reproduce analysis (setup + run commands)
├── analysis/                     # Reproducible SQL / Python scripts reproducing all figures
│   ├── audit_master.py           # Master audit pipeline & invariant assertion engine ($0.00 variance)
│   ├── asc606_revenue_bridge.sql # Pure SQL ASC 606 revenue bridge & treasury cash waterfall
│   ├── logistics_and_leakage_audit.sql # Pure SQL SLA, zombie dispatches, lost claims & RMA scrap
│   ├── retention_and_survival_analysis.py # Entity resolution, cohort matrices & Kaplan-Meier curves
│   ├── unit_economics_and_guardrails.py   # Unit economics, voucher stress test & MOV thresholds
│   ├── starter_query.py          # Quick inspection script
│   └── starter_query.sql         # DuckDB CLI starter query
├── EXECUTIVE_MEMO.md             # C-level decision briefing (max 1,500 words)
└── ai_sessions/                  # Raw AI conversation transcripts, exported logs, and session notes
    ├── audit_engineering_session.md # Formatted engineering transcript & prompt steering log
    └── session_transcript_raw.jsonl # Raw JSONL session log
```

### 3.1 `analysis/` — Reproducible Analysis Scripts
- Every metric, percentage, and dollar figure cited in `EXECUTIVE_MEMO.md` must be directly reproducible by running code in this directory.
- Code must execute top-to-bottom against `enterprise_audit.duckdb` without manual intervention or hardcoded adjustments.
- Use defensive relational modeling: guard against Cartesian join multiplicity on split shipments and payment events.

### 3.2 `EXECUTIVE_MEMO.md` — Board & C-Suite Decision Briefing (Max 1,500 words)
Address your memo to the Board Audit Committee and executive team (CEO, Elena Vance, Marcus Carvalho, Sarah Lin, Lucas Ferreira, Vikram Patel). Structure your memo into five core sections:
1. **Executive Summary & Ground-Truth Scorecard:** High-level executive synthesis answering each stakeholder's hypothesis with empirical findings.
2. **Financial Waterfall & Revenue Reconciliation:** Complete ASC 606 bridge table reconciling gross payment charges to recognized GAAP revenue and net liquid cash deposits down to $0.00 variance.
3. **Supply Chain Leakage & Logistics SLA Audit:** True national and facility delivery SLA, root-cause analysis of zombie dispatches (post-pack cancellations delivered anyway), and lost-in-transit exposure.
4. **Customer Master Entity Retention & Survival Analysis:** B2B parent-subsidiary retention curves controlling for right-censoring in recent cohorts.
5. **Causal Policy Interventions & Margin Guardrails:** Empirical evaluation of customer appeasements with contribution margin guardrails and minimum order value (MOV) thresholds.

### 3.3 `ai_sessions/` — Raw AI Tooling Transcripts
Store raw, unedited conversation logs, transcripts, or session exports from your AI assistant here.
- If using **Claude Code**: export the CLI session transcript or session markdown.
- If using **Cursor**: save your Composer / chat session export or markdown copy.
- If using **ChatGPT / Copilot**: include the shared link or exported conversation log.

Top analytics engineers treat AI assistants as high-speed query drafters while applying defensive human skepticism. Your session transcripts provide evidence of your analytical direction, prompt steering, and error correction during the Level 2 live defense.

---

## 4. How to Reproduce the Analysis

### Quickstart — Master Audit Suite (Recommended)
To execute the complete end-to-end audit, assert mathematical invariants down to $0.00, and print the executive scorecard and waterfall tables:

```bash
# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the master audit suite (validates all invariants & prints executive scorecard)
python analysis/audit_master.py
```

### Modular Domain Analysis Scripts

Each domain investigation is isolated in its own dedicated, reproducible script:

1. **Master Invariant & ASC 606 Waterfall:**
   ```bash
   python analysis/audit_master.py
   ```
2. **Customer Entity Graph, Cohort Retention & Kaplan-Meier Survival Analysis:**
   ```bash
   python analysis/retention_and_survival_analysis.py
   ```
3. **Unit Economics, Appeasement Stress-Testing & MOV Thresholds:**
   ```bash
   python analysis/unit_economics_and_guardrails.py
   ```
4. **Pure SQL Audits (DuckDB):**
   ```bash
   # Run GAAP ASC 606 Revenue Bridge & Treasury Reserve Waterfall
   python3 -c "import duckdb; con = duckdb.connect('enterprise_audit.duckdb', read_only=True); [print(con.execute(s).df().to_string(index=False), '\n') for s in open('analysis/asc606_revenue_bridge.sql').read().split(';') if s.strip()]"

   # Run Logistics SLA, Zombie Dispatches, Carrier Claims & RMA Scrap
   python3 -c "import duckdb; con = duckdb.connect('enterprise_audit.duckdb', read_only=True); [print(con.execute(s).df().to_string(index=False), '\n') for s in open('analysis/logistics_and_leakage_audit.sql').read().split(';') if s.strip()]"
   ```
5. **Starter Queries:**
   ```bash
   python analysis/starter_query.py
   ```
