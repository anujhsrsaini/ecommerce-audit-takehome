# Meridian Enterprise Technologies — Enterprise Forensic Data Audit & Adversarial Challenge

**Role:** Senior / Lead Analytics Engineer, Principal Financial Data Analyst, Forensic Analytics Lead  
**Deliverable:** Asynchronous GitHub Assessment — Reproducible DuckDB Pipeline + Executive Decision Memo (`EXECUTIVE_MEMO.md`)  
**Database Horizon:** 13 Calendar Months (December 1, 2024 through December 31, 2025; ~2.55M rows across 11 tables)

---

## 1. Executive Summary of Audited Findings

An independent cross-system forensic audit was conducted on `enterprise_forensic_audit.duckdb` across five decoupled operational systems:
1. **Billing & Payment Gateway (Stripe / Treasury):** `payment_events`, `foreign_exchange_rates`, `treasury_settlements`
2. **Accrual ERP & Financial Ledger (NetSuite):** `erp_order_headers`, `erp_order_line_items`, `erp_general_ledger_entries`
3. **Logistics Telematics & 3PL (Manhattan WMS & EDI 214):** `wms_fulfillment_consignments`, `carrier_telematics_scans`
4. **Customer Identity Graph (Rudderstack / D&B):** `customer_entity_mappings`, `corporate_tax_entities`
5. **Corporate Finance Reporting Mart:** `bi_executive_daily_recon`

### Audited Scorecard

| Stakeholder & Dispute | Claimed Metric | Audited Ground Truth | Root Cause & Resolution |
| :--- | :--- | :--- | :--- |
| **Elena Vance (CFO):** Revenue Gap & Cash Shortfall | Charges exceed rev by >$4M; ~$2.3M missing cash; suspects fraud | **$58,420,500.00** gross ties to **$54,379,002.43** rec rev ($0.00 unrec) & **$56,126,000.00** cash ($0.00 unrec) | **Zero fraud or dropped transactions.** Gap is 100% ASC 606 delivery timing ($3.60M in-transit/pending) & disputes ($442.25K). Cash delta is fees ($1.58M), reserves ($160K net), disputes ($465.5K), FX ($86.55K). |
| **Marcus Carvalho (Logistics):** Terminate DHL | 19.18% failure rate vs 95% SLA | Headline: **19.18%** (3,836 pkgs). Carrier fault: **1.35%** (270 pkgs). Merchant bug: **17.83%** (3,566 pkgs) | **Refute termination.** 3,566 failures trace to internal bug `DEP-2025-07-02-ADDR-V2` (postcode truncation & omitted EORI). DHL genuine reliability is 98.65%. Prevents **$8.5M wrongful termination penalty**. |
| **Marcus Carvalho (Logistics):** Post-Pack Cancellations | Support cancels post-pack; inventory lost | **640 orders** cancelled post-pack; **100% (640/640) delivered** | **Confirmed $1,570,560.00 leakage** ($1,472,000.00 COGS + $98,560.00 freight) on credited NET30 orders. Fix: WMS dispatch lock. |
| **Lucas Ferreira (Growth):** 3.8% Retention Collapse | 385K tokens, 3.8% return; Q3–Q4 repeat ~0% | Logo retention: **94.62%** (615/650 parents). NDR: **124.80%** ($40M to $49.92M). Repeat: **100%** (parents), **99.96%** (subs) | **Refute collapse.** Lucas audited transient browser cookies, not accounts. Enterprise spend expanded +24.8% YoY (124.8% NDR). |
| **Sarah Lin (CX) & Lucas:** Voucher Expansion | Blanket voucher expansion across escalated tickets | `APPEASE30`: **+$1,890,000.00** margin (+$54/order; 85.8% repeat). `STACKED20-MSA`: **-$7,710,000.00** EBITDA loss | **Conditional approval.** Expand `APPEASE30` with guardrails ($300 min). Ban promo stacking on MSA contracts to save **+$6.84M to +$7.71M** EBITDA. |

---

## 2. Repository Structure

```
├── README.md                     # This comprehensive reproduction guide and executive audit summary
├── EXECUTIVE_MEMO.md             # C-suite decision briefing (1,488 words; max 1,500 words)
├── analysis/                     # Reproducible SQL & Python audit pipeline
│   ├── run_all_audits.py         # Master Python analysis pipeline reproducing all figures
│   ├── forensic_audit.sql        # Complete pure SQL audit script runnable in DuckDB CLI
│   ├── verify_invariants.py      # Automated invariant test suite (31 mathematical proofs)
│   ├── starter_query.py          # Starter table inspection & inventory script
│   └── starter_query.sql         # Starter SQL exploration script
├── ai_sessions/                  # Raw AI conversation logs & session transcript
│   ├── session_transcript.md     # Chronological log of AI prompts, queries, and technical steering
│   ├── transcript_full.jsonl     # Complete raw JSONL session transcript
│   └── transcript.jsonl          # Compact raw JSONL session transcript
├── schema_dictionary.md          # Database schema documentation across all 11 tables
├── STAKEHOLDER_NOTES.md          # Internal C-suite confidential memo thread
├── requirements.txt              # Python environment dependencies
└── .devcontainer/                # Development container configuration
```

---

## 3. How to Reproduce All Results

### 3.1 Environment Setup

```bash
# Clone the repository
git clone https://github.com/anujhsrsaini/ecommerce-audit-takehome.git
cd ecommerce-audit-takehome

# Set up virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Run the Complete Python Audit Pipeline

To execute the top-to-bottom analysis pipeline that reproduces every scorecard metric, bridge table, carrier decomposition, retention matrix, and voucher economics cited in `EXECUTIVE_MEMO.md`:

```bash
python3 analysis/run_all_audits.py
```

### 3.3 Verify Mathematical Invariants (31 Automated Proofs)

To run the automated verification suite confirming that all accounting equations, GL double-entry balances, bridge tables, and operational invariants hold down to **$0.00 variance**:

```bash
python3 analysis/verify_invariants.py
```

### 3.4 Run the Pure SQL Audit Script (DuckDB CLI)

To execute the complete analysis using native DuckDB SQL:

```bash
duckdb enterprise_forensic_audit.duckdb -f analysis/forensic_audit.sql
```

---

## 4. Key Methodological Insights & System Truths

### 4.1 Revenue Recognition Bridge (ASC 606)
- **Gross Gateway Charges:** $58,420,500.00 across 108,231 prepaid credit card orders (`CREDIT_CARD_PREPAID`).
- **Timing Deductions:** Under ASC 606, revenue cannot be recognized until performance obligations are satisfied via customer delivery. At period close, $1,821,953.84 was in warehouse staging (`PENDING_DELIVERY`), and $1,777,293.73 was on carrier trucks in transit (`PENDING_IN_TRANSIT`).
- **Dispute Deductions:** $442,250.00 was reversed due to chargebacks (`REVERSED_DISPUTE`).
- **Recognized Delivered Revenue:** Exactly $54,379,002.43. Unexplained variance: **$0.00**.
- **Total Company Recognized Revenue:** Across all payment terms (including B2B invoicing: NET30 $16.30M, NET60 $20.52M, Wire $14.15M), total recognized delivered revenue is **$105,341,799.66** (total invoiced bookings: $117,391,799.66).

### 4.2 Treasury Cash Waterfall & GL Balance
- **Cash Deductions:** Gross cleared funds ($58,420,500.00) minus fees ($1,582,450.00) minus rolling risk reserve hold ($1,280,000.00) plus prior reserve release ($1,120,000.00) minus dispute clawbacks ($465,500.00) minus FX drift ($86,550.00) = **$56,126,000.00** net liquid operating cash in Barclays Operating Account ****4821.
- **Cash Shortfall:** The perceived ~$2.3M shortfall is exactly **$2,294,500.00** ($1.58M fees + $160K net reserve + $465.5K disputes + $86.55K FX drift). Unexplained variance: **$0.00**.
- **GL Double-Entry Balance:** All 831,245 journal entries in `erp_general_ledger_entries` balance to **$0.00** ($265,397,974.09 debits = $265,397,974.09 credits). GL Account `1010 Cash in Transit` net debit is exactly $56,126,000.00.

### 4.3 Carrier SLA Audit & Scan Decomposition
- **Headline vs Reality:** Marcus Carvalho observed a 19.18% headline exception rate on DHL (3,836 of 20,000 consignments).
- **Root Cause Decomposition:** Scan-by-scan telematics analysis revealed that 3,566 consignments (92.96% of exceptions, 17.83% of all shipments) were caused by Meridian's internal software deployment `DEP-2025-07-02-ADDR-V2`, which truncated postal codes (`ERR_POSTCODE_TRUNCATED`, 1,832 consignments) and omitted customs EORI identifiers (`ERR_CUSTOMS_EORI_MISSING`, 1,734 consignments).
- **Genuine Carrier Liability:** Only 270 consignments were genuine carrier faults (`ERR_CARRIER_LOST` = 194, `ERR_CARRIER_DAMAGED` = 76), giving DHL a **1.35% genuine failure rate** (98.65% reliability). DHL outperformed FedEx (1.51%), UPS (1.51%), and USPS (1.48%). Terminating DHL would trigger an unjustified **$8.5M early-termination liability**.

### 4.4 Post-Pack Cancellation Leakage
- **Scope & Evidence:** 640 orders were cancelled by Customer Support under `CUSTOMER_REQUEST_POST_PACK` after carton packaging. WMS telematics confirm that **100% (640/640) were dispatched and DELIVERED** (`POST_PACK_DELIVERED_NO_RETURN`).
- **Direct P&L Loss:** All 640 orders were NET30 terms credited in ERP ($1.92M credited invoices). Direct leakage totaled **$1,570,560.00** ($1,472,000.00 inventory COGS + $98,560.00 freight).

### 4.5 Customer Retention & Identity Resolution
- **Measurement Bias:** Lucas Ferreira queried raw browser cookie tokens (`customer_entity_mappings.session_cookie_token`, 385,000 tokens, 3.80% returning), confusing ephemeral browser touchpoints with corporate clients.
- **Enterprise Account Reality:** Audited at the ultimate parent conglomerate level (`corporate_tax_entities`), logo retention is **94.62%** (615 of 650 parent accounts retained) and Net Revenue Retention (NDR) is **124.80%** ($40.0M base expanding to $49.92M current). Top 5 Strategic accounts represent 47.64% of total spend ($55.92M) and expanded at 119.69% NDR.

### 4.6 Voucher Unit Economics & Anti-Stacking Guardrails
- **The Loophole:** 1,200 enterprise server orders stacked a 20% promo voucher (`STACKED20-MSA`, $6.84M) on top of pre-negotiated 20% MSA discounts ($6.84M). Priced at $17,100 against $18,525 COGS and $5,000 freight, this burned **-$6,425.00 per order**, draining **$7,710,000.00 in negative contribution margin** directly into the 5 largest accounts.
- **Appeasement Efficacy:** `APPEASE30` generated **+$1,890,000.00 in profit** (+18.62% margin, $54/order) on small consumables ($320 list), with appeased buyers exhibiting an **85.79% repeat purchase rate** vs 55.35% for non-appeased buyers.
- **Policy Guardrails:** Enforcing strict anti-stacking rules in NetSuite/checkout and establishing a $300 minimum order threshold immediately recovers **+$6.84M in revenue** and eliminates **$7.71M in losses**, improving annual EBITDA by **+$6.84M to +$7.71M**.

### 4.7 Corporate Finance BI Reporting Mart Defect
- `bi_executive_daily_recon` reported $138,687,597.30 in "certified net recognized revenue" and 125,933 rows. Primary ERP records prove total recognized revenue is $105,341,799.66 across 114,777 lines.
- **Root Cause:** Corporate Finance built the BI mart by joining order line items with fulfillment consignments without aggregating to order grain, producing fan-out duplication on multi-consignment / multi-facility orders. The reporting mart must be deprecated and rebuilt on primary GL/ERP tables.

---

## 5. Contact & Audit Representation

This audit was conducted independently by the Lead Analytics Engineer & Forensic Data Auditor for the Board Audit Committee of Meridian Enterprise Technologies. All figures are fully reproducible from source code in `analysis/` against `enterprise_forensic_audit.duckdb`.
