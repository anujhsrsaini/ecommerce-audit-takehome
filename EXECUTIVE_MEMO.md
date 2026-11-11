# Executive Decision Memo — Enterprise Forensic Audit

**To:** Board Audit Committee, CEO, CFO (Vance), VP Logistics (Carvalho), VP CX (Lin), VP Growth (Ferreira)  
**From:** Lead Analytics Engineer & Forensic Data Auditor  
**Date:** January 15, 2026  
**Subject:** Full-Funnel Reconciliation ($0.00 Variance), Carrier SLA Verdict, Retention & Voucher Guardrails

---

## 1. Executive Summary & Ground-Truth Scorecard

Forensic audit of `enterprise_forensic_audit.duckdb` (11 tables, 2.55M rows, Dec 2024–Dec 2025) across Billing, ERP, WMS, Identity, and BI Mart resolves the C-suite deadlock:

| Stakeholder & Dispute | Claimed Metric | Audited Ground Truth | Root Cause & Resolution |
| :--- | :--- | :--- | :--- |
| **Elena Vance (CFO):** Rev Gap & Cash Shortfall | Charges exceed rev by >$4M; ~$2.3M missing cash; suspects fraud | **$58,420,500.00** gross ties to **$54,379,002.43** rec rev & **$56,126,000.00** cash ($0.00 unrec) | Zero fraud. Rev gap is ASC 606 delivery timing ($3.60M) & disputes ($442K). Cash delta is fees ($1.58M), reserves ($160K net), disputes ($465.5K), FX ($86.55K). |
| **Marcus Carvalho (Logistics):** Terminate DHL | 19.18% failure rate vs 95% SLA | Headline: **19.18%** (3,836 pkgs). Carrier fault: **1.35%** (270 pkgs). Merchant bug: **17.83%** (3,566 pkgs) | Refute termination. 3,566 failures trace to internal bug `DEP-2025-07-02-ADDR-V2`. DHL genuine reliability is 98.65%. Prevents **$8.5M penalty**. |
| **Marcus Carvalho (Logistics):** Post-Pack Cancellations | Support cancels post-pack; inventory lost | **640 orders** cancelled post-pack; **100% (640/640) delivered** | Confirmed **$1,570,560.00 leakage** ($1,472,000.00 COGS + $98,560.00 freight) on credited NET30 orders. Fix: WMS dispatch lock. |
| **Lucas Ferreira (Growth):** 3.8% Retention Collapse | 385K tokens, 3.8% return; Q3–Q4 repeat ~0% | Logo retention: **94.62%** (615/650 parents). NDR: **124.80%** ($40M to $49.92M). Repeat: **100%** (parents), **99.96%** (subs) | Refute collapse. Lucas audited transient browser cookies, not accounts. Enterprise spend expanded +24.8% YoY (124.8% NDR). |
| **Sarah Lin (CX) & Lucas:** Voucher Expansion | Blanket voucher expansion across escalated tickets | `APPEASE30`: **+$1,890,000.00** margin (+$54/order; 85.8% repeat). `STACKED20-MSA`: **-$7,710,000.00** EBITDA loss | Conditional approval. Expand `APPEASE30` with guardrails ($300 min). Ban promo stacking on MSA contracts to save **+$6.84M to +$7.71M** EBITDA. |

---

## 2. Revenue Recognition Bridge

Gross charges ($58,420,500.00; 108,231 CC transactions) reconcile to recognized revenue with **$0.00 unexplained variance** under ASC 606 (delivery-based recognition):

| Bridge Stage | Category | Amount (USD) | Primary Source Records & Notes |
| :--- | :--- | :--- | :--- |
| **Starting point** | **Gross Gateway Charges** | **$58,420,500.00** | `payment_events` (`charge.captured`) / `erp_order_headers` |
| **Less:** | Pending Warehouse Delivery | -$1,821,953.84 | `erp_order_line_items` (`PENDING_DELIVERY`, 4,477 orders) |
| **Less:** | Pending In-Transit Delivery | -$1,777,293.73 | `erp_order_line_items` (`PENDING_IN_TRANSIT`, 4,176 orders) |
| **Less:** | Dispute Chargeback Reversals | -$442,250.00 | `erp_order_line_items` (`REVERSED_DISPUTE`, 1,550 orders) |
| **Audited recognized revenue** | **Recognized Delivered Revenue (CC)** | **$54,379,002.43** | `erp_order_line_items` (`RECOGNIZED_DELIVERED`, 98,028 orders) |
| **Bridge Variance** | **Unexplained Variance** | **$0.00** | **Exact balance: $58,420,500.00 - $4,041,497.57** |

*Enterprise Revenue:* Total recognized revenue across all payment terms is **$105,341,799.66** (bookings: $117,391,799.66). The BI mart (`bi_executive_daily_recon`, $138.69M) is distorted by join fan-out.

---

## 3. Treasury Cash Waterfall

The **$2,294,500.00 cash shortfall** in Barclays Operating Account ****4821 is 100% accounted for by contractual deductions, balancing to **$0.00**:

| Waterfall Stage | Category | Amount (USD) | Primary Source Records & Settlement Evidence |
| :--- | :--- | :--- | :--- |
| **Starting point** | **Gross Cleared Gateway Funds** | **$58,420,500.00** | `treasury_settlements.gross_cleared_amount` (362 daily batches) |
| **Less:** | Merchant Processing Fees | -$1,582,450.00 | `treasury_settlements.processing_fees_amount` |
| **Less:** | Rolling Risk Reserve Withheld | -$1,280,000.00 | `treasury_settlements.risk_reserve_held_amount` (90-day hold) |
| **Plus:** | Prior-Period Reserves Released | +$1,120,000.00 | `treasury_settlements.risk_reserve_released_amount` (4 tranches) |
| **Less:** | Dispute Debits & Fees | -$465,500.00 | `treasury_settlements.dispute_clawback_amount` ($442.25K loss + $23.25K fees) |
| **Less:** | Realized FX Settlement Drift | -$86,550.00 | `treasury_settlements.fx_settlement_drift_amount` (EUR, GBP, CAD) |
| **Net liquid deposits** | **Operating Bank Cash Deposited** | **$56,126,000.00** | `treasury_settlements.net_liquidity_amount` (Ties to GL 1010) |
| **Waterfall Variance** | **Unexplained Cash Variance** | **$0.00** | **Exact balance: $58,420,500.00 - $2,294,500.00** |

*GL Proof:* Debits and credits balance across 831,245 lines ($265,397,974.09; Imbalance: **$0.00**). GL `1010 Cash in Transit` is **$56,126,000.00**; GL `1150 Risk Reserve Receivable` is **$160,000.00**.

---

## 4. Carrier SLA Audit & Supply Chain Leakage

### 4.1 Carrier SLA Fault Decomposition
Auditing 621,849 scans decomposes DHL's 19.18% failure claim:

| Carrier | Total Pkgs | Headline Exceptions | Headline Failure Rate | Genuine Carrier Faults | Genuine Fault Rate | Merchant Defects | Non-Carrier Root Cause |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **DHL** | 20,000 | 3,836 | 19.18% | **270** | **1.35%** | **3,566 (17.83%)** | Internal bug `DEP-2025-07-02-ADDR-V2` |
| **FedEx** | 41,905 | 634 | 1.51% | 634 | 1.51% | 0 (0.00%) | Carrier liability (lost/damaged) |
| **UPS** | 31,596 | 476 | 1.51% | 476 | 1.51% | 0 (0.00%) | Carrier liability (lost/damaged) |
| **USPS** | 31,499 | 465 | 1.48% | 465 | 1.48% | 0 (0.00%) | Carrier liability (lost/damaged) |

**Verdict: REJECT TERMINATION.** DHL genuine fault is **1.35%** (98.65% reliability), beating FedEx/UPS (1.51%). 92.96% of DHL exceptions trace to internal bug `DEP-2025-07-02-ADDR-V2`. Termination triggers an **$8.5M penalty**.

### 4.2 Post-Pack Cancellation Leakage
WMS scans confirm **100% (640/640) of post-pack cancellations were delivered** (`POST_PACK_DELIVERED_NO_RETURN`). On credited NET30 orders ($1.92M invoices), direct leakage is **$1,570,560.00** ($1,472,000.00 COGS + $98,560.00 freight). Fix: WMS lock post `PACK_VERIFIED`.

---

## 5. Customer Retention & Account Hierarchy Analysis

Lucas Ferreira's 3.8% retention metric reflects transient browser cookies, not B2B accounts:

| Identity Level | Population | Repeat / Retained | Retention Rate | Definition & Strategic Context |
| :--- | :--- | :--- | :--- | :--- |
| **Session Cookie Token** | 385,000 mapping (106,635 orders) | 14,630 mapping (16,590 orders) | 3.80% (15.56% orders) | Ephemeral browser touchpoints. |
| **Authorized Buyer User** | 33,389 | 23,634 | **70.78%** | Procurement logins across subsidiary units. |
| **Purchasing Subsidiary** | 8,496 | 8,493 | **99.96%** | Operating corporate accounts. |
| **Ultimate Parent Entity** | 650 | 650 orders (615 retained) | **100.0% repeat / 94.62% NDR** | D&B parent entity ($40M to $49.92M, 124.80% NDR). |

Top 5 Strategic accounts generate **$55,923,485.99** (47.64% of spend), expanding at 119.69% NDR. 100% of parent accounts repeated in 2025; cohort decay is right-censorship of young cookies.

---

## 6. Voucher Unit Economics & Commercial Guardrails

Analysis of 125,130 orders shows stark voucher divergence:

| Voucher Program | Orders | Net Revenue | COGS | Freight | Contribution Margin (CM) | Avg Margin | Margin % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Promo (`SAVE5`)** | 85,550 | $53,438,799.66 | $32,373,857.80 | $2,012,551.33 | **+$19,052,390.53** | +$222.70 | 35.65% |
| **Appeasement (`APPEASE30`)** | 35,000 | $10,150,000.00 | $7,735,000.00 | $525,000.00 | **+$1,890,000.00** | +$54.00 | 18.62% |
| **Baseline (No Voucher)** | 2,480 | $33,283,000.00 | $21,858,766.63 | $326,400.00 | **+$11,097,833.37** | +$4,474.93 | 33.34% |
| **Stacked (`STACKED20-MSA`)** | 1,200 | $20,520,000.00 | $22,230,000.00 | $6,000,000.00 | **-$7,710,000.00** | **-$6,425.00** | **-37.57%** |
| **Warranty (`WARRANTY100`)** | 900 | $0.00 | $36,000.00 | $25,379.43 | **-$61,379.43** | -$68.20 | -inf |
| **Company Total** | **125,130** | **$117,391,799.66** | **$84,233,624.43** | **$8,889,330.76** | **+$24,268,844.47** | **+$193.95** | **20.67%** |

### 6.1 The STACKED20-MSA Loophole & Guardrails
- **The STACKED20-MSA Loophole:** 1,200 server orders stacked 20% promo vouchers ($6.84M) on 20% MSA discounts ($6.84M). Priced at $17,100 against $18,525 COGS and $5,000 freight, this lost **-$6,425.00/order** and bled **-$7,710,000.00 EBITDA**.
- **Guardrails:** `APPEASE30` buyers repeat at **85.79%** (vs 55.35%) and profit +$1.89M. Program expansion requires two rules:
  1. **Anti-Stacking Rule:** Hard block prohibiting promo vouchers on MSA accounts (`msa_discount_pct > 0`). Kill `STACKED20-MSA`.
  2. **Basket Minimums:** Minimum order of **$300** for $30 vouchers (max 10% discount); exclude servers/storage.
  3. **EBITDA Impact:** Stopping stacked discounts recovers **+$6.84M revenue** and stops **$7.71M losses** (+**$6.84M to +$7.71M annually**).

---

## 7. Prioritized Operational Recommendations

| # | Action | Owner | Timeline | Quantified Financial Impact |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Enforce ERP Anti-Stacking:** Block promo discounts on MSA contracts; kill STACKED20-MSA. | VP Growth & CFO | Immediate | **+$6.84M to +$7.71M EBITDA** gain. |
| **2** | **Halt DHL Termination:** Retain contract; hotfix bug `DEP-2025-07-02-ADDR-V2`. | VP Logistics & CTO | 48 Hours | **Avoids $8.5M Penalty**; fixes 3,566 shipments/yr. |
| **3** | **Deploy WMS Dispatch Lock:** Block Support cancellations post `PACK_VERIFIED`. | VP Logistics & VP CX | 14 Days | **+$1,570,560.00 Recovery** of delivered inventory. |
| **4** | **Re-architect BI Mart:** Deprecate `bi_executive_daily_recon`; build on primary GL/ERP tables. | Audit Chair & CFO | 30 Days | **Eliminates $33.35M Error**; aligns dashboards to GL. |
