# Executive Decision Memo — Enterprise Cross-System Audit & Forensic Analytics

**To:** Board Audit Committee & Executive Leadership  
**From:** Lead Analytics Engineer & Forensic Auditor  
**Date:** January 14, 2026  
**Subject:** Cross-System Ledger Reconciliation, Supply Chain Leakage & Retention Audit  

---

## 1. Executive Summary & Ground-Truth Scorecard

Forensic audit of Aura’s four systems (Stripe, NetSuite, Manhattan WMS, Customer MDM) across 150,000 orders and ~1.8M records (Oct 2024–Dec 2025) settles all executive disputes with empirical data:

| Stakeholder & Hypothesis | Claimed Metric | Audited Ground Truth | Root Cause & Resolution |
| :--- | :--- | :--- | :--- |
| **Elena Vance (CFO):** Revenue Gap | $7.4M gap ($184.2M vs $176.8M) | **$702.34M** Stripe / **$1,163.22M** GAAP | Stripe is Card-only. Non-card terms add $561.30M. Waterfall balances to **$0.00**. |
| **Elena Vance (CFO):** Cash Shortfall | $6.2M missing SVB cash | **$7.34M** active risk reserve in escrow | Cash intact in Stripe escrow (5% rolling holdback). Releases in 90 days. |
| **Marcus Carvalho (Logistics):** SLA | 97.2% on-time delivery SLA | **89.28%** Order SLA / **90.32%** Pkg SLA | Grain error: evaluated `delivered/FULFILLED`; omitted lost, cancelled, and pending orders. |
| **Marcus Carvalho (Logistics):** Leakage | Trigger-happy refund leakage | **2,404 orders / $13.30M COGS leaked** | Post-pack cancels delivered anyway; lacks WMS interlock. |
| **Sarah Lin (CX):** RMA Defect | Scrapped hardware in restock | **12,619 lines / $31.99M COGS scrapped** | 100% of RMAs are scrap (`DAMAGED_WRITE_OFF`). Balance sheet assets inflated $31.99M. |
| **Lucas Ferreira (Growth):** Churn | <4% retention; 90%+ one-and-done | **98.57% account repeat; 99.20% KM 1-yr** | Cookie grain error vs. resolved B2B accounts, plus right-censoring in recent cohorts. |
| **Vikram Patel (Legal):** Invariants | ASC 606 & carrier recoveries | **$0.00 bridge; $42.69M unfiled claims** | 9,382 unfiled lost parcels. Sub-$50 orders operate at negative margin. |

---

## 2. Financial Waterfall & GAAP Revenue Reconciliation

### Table 2.1: GAAP ASC 606 Revenue Recognition Bridge (down to $0.00 variance)
Under ASC 606, performance obligations are satisfied upon physical transfer of control (WMS delivery scan).

| Stage | Transaction Category | Amount (USD) | Accounting & Ledger Notes |
| :--- | :--- | :--- | :--- |
| **Gross Payment Volume** | Stripe Captured Charges | **$702,344,145.40** | 77,891 card captures in `billing_events` |
| **Less: Sales Tax Collected** | Sales Tax on Card Orders | **-$40,437,359.45** | Balance sheet tax liability; non-revenue |
| **Less: Customer Freight** | Shipping Charged to Buyers | **-$464,150.00** | Pass-through freight billed to buyers |
| **Subtotal: Card Product Invoiced**| Net Invoiced Merchandise | **$661,442,635.95** | Invoiced value on credit card orders |
| **Less: Webhook / Unfulfilled** | Pending Approval (Stuck) | **-$4,780,540.66** | 627 orders in Stripe; 0 packages manifested |
| **Less: In-Transit / Lost Lines** | Closed Orders (Carrier Lost) | **-$21,553,292.00** | 4,907 card orders lost by carriers; delivery pending |
| **Less: Post-Pack Cancelled** | Zombie Dispatches (Refunded) | **-$8,015,253.41** | 990 card orders refunded upon cancellation |
| **Less: Damaged RMA Returns** | Returned Damaged Hardware | **-$25,172,130.72** | 6,475 returned lines on card orders; reversed at intake |
| **Subtotal: Card Recognized Rev** | Credit Card Delivered Lines | **$601,921,419.16** | 147,284 delivered lines under ASC 606 |
| **Plus: Non-Card Recognized (ACH)**| ACH Delivered Lines | **+$277,754,442.42** | 67,753 delivered lines |
| **Plus: Non-Card Recognized (Net30)**| Net 30 Delivered Lines | **+$283,543,424.54** | 68,806 delivered lines |
| **Audited GAAP ASC 606 Revenue** | Total Recognized Revenue | **$1,163,219,286.12** | **Balances to NetSuite Ledger ($0.00 variance)** |

### Table 2.2: Treasury Reserve & Operating Cash Waterfall (down to $0.00 variance)

| Treasury Liquidity Stage | Cash Flow Impact (USD) | Operational & Banking Notes |
| :--- | :--- | :--- |
| **Gross Payment Collections** | **$702,344,145.40** | Gross collections across 77,891 captures |
| **Less: Merchant Processing Fees** | **-$20,391,347.75** | Standard Blended fees (2.9% + $0.30) |
| **Plus: Contract Fee Credit** | **+$87,412.50** | Retroactive Interchange-Plus credit (po_trueup_20250502) |
| **Less: Customer Refunds** | **-$8,502,128.74** | 990 post-pack cancellations refunded to credit cards |
| **Less: Dispute Chargebacks & Fees**| **-$20,810,358.52** | 2,250 disputes ($20.78M debits + $33.75K fees) |
| **Net Settled Gateway Funds** | **$652,727,722.89** | Net gateway cash before reserve escrow |
| **Less: Active Risk Reserve Withheld**| **-$7,335,873.31** | 5.0% rolling 90-day reserve holdback for Q4 2025 captures |
| **Audited Liquid Net Cash (SVB)** | **$645,391,849.58** | **Liquid SVB bank deposits ($0.00 variance)** |

*Fee Credit Amortization:* The $87,412.50 credit applies to Q1 2025: Jan $29,910.15; Feb $27,971.86; Mar $29,530.49 (or $7,284.38/month across FY2025).

---

## 3. Supply Chain Leakage & Logistics SLA Audit

- **True Delivery SLA:** Across all 150,000 orders, only **133,915 delivered without defect (89.28%)**. For 149,373 orders dispatched to WMS, SLA was **89.65%**, failing the 95.0% contractual standard. At the package grain (159,767 cartons), **90.32% delivered (144,309)**, **5.87% lost in transit (9,382)**, and **3.80% returned damaged (6,076)** across Allentown (90.30%), Dallas (90.38%), and Reno (90.29%).
- **2-Day Air SLA Collapse:** Out of 25,822 delivered 2-Day Air packages, **only 8,672 arrived within 2 days (33.58% on-time)**; average transit was 3.01 days. 66.42% breached contractual transit time, driving support cancellations.
- **Zombie Dispatches:** Support cancelled **2,404 orders** post-pack (`CUSTOMER_REQUEST_POST_PACK`). Lacking a WMS interlock, cartons were loaded onto trailers 2–4 hours later and delivered anyway:
  - **Invoiced Value Lost:** **$21,879,170.75** (Line Net: $20,614,675.63).
  - **Inventory COGS Leaked:** **$13,302,535.66** ($5.16M Card, $4.19M ACH, $3.95M Net 30).
  - **Freight & Lost Fees:** **$83,374.02** freight + **$246,858.82** unrecovered Stripe fees.
- **Unfiled Carrier Insurance Claims:** Carriers lost **9,382 packages** (`CARRIER_CONTAINER_BREACH_SEARCH_EXHAUSTED`):
  - **Commercial Claim Exposure:** **$42,685,890.07** across DHL ($10.35M), UPS ($11.15M), USPS ($10.74M), and FedEx ($10.45M).
  - **Inventory COGS:** **$27,415,394.44**; **Paid Freight:** **$325,105.81**. Zero claims filed to date.
- **Scrapped RMA Hardware Assets:** Warehouse intake scrapped **12,619 line items ($31,990,019.02 COGS)** due to carrier transit damage. NetSuite credited inventory at cost rather than writing it off, inflating balance sheet assets by **$31.99M** (Storage Arrays: $14.34M, Servers: $8.98M, Networking: $3.96M).

---

## 4. Customer Master Entity Retention & Survival Analysis

- **Entity Graph Resolution:** Lucas evaluated raw guest checkout cookies (41,941 orders), where tokens appear once. Resolving accounts through the Customer MDM graph proves exceptional loyalty:
  - **Operating Subsidiary Accounts:** **98.57% repeat purchase rate** (8,357 of 8,478 accounts repeat; 18.1 avg orders/account).
  - **Parent Conglomerates:** **98.57% repeat purchase rate** (8,351 of 8,472 repeat). Apex Global Technologies (`ACCT-000001`) and its 6 subsidiaries placed **304 orders totaling $2.48M**.
  - **Authorized Procurement Buyers:** **91.79% repeat purchase rate** (25,158 of 27,409 repeat; 3.9 avg orders/buyer).
- **Kaplan-Meier Survival Analysis (Right-Censoring Correction):** Median re-order cadence is **12.4 days** (mean 21.8 days; 90th percentile 50.0 days). Recent Q3/Q4 2025 cohorts appeared to show low repeat only because calendar time had not elapsed. Kaplan-Meier survival curves controlling for right-censoring confirm durable retention:

| Elapsed Time Post-First Order | Account-Level Repeat Probability | Authorized Buyer Repeat Probability |
| :--- | :--- | :--- |
| **Day 15** | 37.49% | 11.77% |
| **Day 30** | 57.54% | 21.86% |
| **Day 60** | 76.27% | 38.88% |
| **Day 90** | 84.05% | 52.56% |
| **Day 180** | 94.50% | 78.01% |
| **Day 365 (1 Year)** | **99.20%** | **95.53%** |

---

## 5. Strategic Policy Recommendations & Margin Guardrails

- **Unit Economics & Appeasement Danger:**
  - **Orders <$50 (4,820 orders):** Subtotal $37.26, COGS $17.46, freight $34.37, fee $1.11. **Contribution margin is -$16.23 (-48.1%)**; 91.5% operate at a loss.
  - **Orders $50–$100 (6,081 orders):** Subtotal $73.35, COGS $27.74, freight $34.71, fee $1.70. **Contribution margin is $8.06 (9.6%)**.
  - **Voucher Stress-Test:** Unconstrained $50–$250 appeasements destroy EBITDA: a $50 credit produces -$41.94 CM on a $73 order; a $250 credit creates -$194.53 to -$266.23 deficits.

| Priority | Executive Owner | Action Item & Operational Mandate | Financial Impact |
| :--- | :--- | :--- | :--- |
| **P1** | **Marcus Carvalho & Vikram Patel** | **Deploy WMS Interlock:** Block NetSuite cancellations once status is `PACKED`. Quarantine cartons to rework lanes. | **+$13.30M COGS recovered** annually; stops zombie dispatches. |
| **P2** | **Vikram Patel & Elena Vance** | **Execute Carrier Insurance Claims:** File claims against FedEx, UPS, DHL, USPS for 9,382 transit losses (`EXCEPTION_LOST`). | **+$42.69M cash recovery** ($27.42M COGS + $325K freight). |
| **P3** | **Elena Vance (CFO)** | **RMA Balance Sheet Impairment:** Adjust NetSuite valuation to recognize $31.99M write-off for damaged scrap (`DAMAGED_WRITE_OFF`). | Cleanses balance sheet before external audit; resolves qualification. |
| **P4** | **Sarah Lin & Lucas Ferreira** | **Enforce MOV Thresholds:** Require cart minimums for 20% CM: **$250 MOV for $50 voucher; $500 for $100; $1,250 for $250**. Ban vouchers on orders <$100. | Preserves **$4.2M gross margin**; stops small-order dilution. |
| **P5** | **Marcus Carvalho (Logistics)** | **Enforce Carrier 2-Day Air SLA Clawbacks:** Audit delivery timestamps and claim freight refunds on 66.42% breached air shipments. | **+$1.85M annual freight credits** from SLA failure terms. |
