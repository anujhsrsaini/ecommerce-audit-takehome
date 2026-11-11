# Schema Dictionary — Aura Enterprise Technologies Database

**Database File:** `enterprise_audit.duckdb`  
**Time Horizon:** 15 calendar months (October 1, 2024 through December 31, 2025)  
**Total Records:** ~1.8 Million rows across 8 relational tables

---

## Architecture Overview

The database models four decoupled enterprise systems operating asynchronously:
1. **Billing & Payment Processor (Stripe):** `billing_events` (Strict UTC timestamps)
2. **Accrual ERP & Order Ledger (NetSuite):** `erp_orders`, `erp_order_lines` (Local Eastern Business Time `America/New_York`)
3. **Logistics Telematics & WMS (Manhattan Associates):** `wms_fulfillment`, `wms_package_scans` (Strict UTC timestamps)
4. **Customer Master Data Management (MDM):** `customer_accounts`, `buyer_profiles`, `customer_identity_mappings` (Strict UTC timestamps)

---

## Table 1: `billing_events`
- **Domain:** Payment Gateway & Merchant Acquiring (Stripe)
- **Grain:** 1 row per atomic payment event / webhook message received from the payment processor.
- **Primary Key:** `event_id` (`VARCHAR`)
- **Temporal Zone:** `TIMESTAMPTZ` (UTC)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `event_id` | `VARCHAR` | Primary Key. UUID identifier of the gateway event. |
| `event_type` | `VARCHAR` | Event type: `payment_intent.created`, `charge.authorized`, `charge.captured`, `charge.refunded`, `dispute.created`, `dispute.funds_withdrawn`, `processor.fee_credit`. |
| `payment_intent_id` | `VARCHAR` | Correlation ID grouping all lifecycle events for a checkout attempt (e.g. `pi_3M...`). |
| `charge_id` | `VARCHAR` | Unique transaction ID assigned upon authorization / capture (e.g. `ch_2K...`). |
| `order_id` | `VARCHAR` | Commercial order reference passed in metadata (e.g. `SO-2024-001429`). |
| `customer_account_id` | `VARCHAR` | Account ID passed in merchant metadata. |
| `event_timestamp_utc` | `TIMESTAMPTZ` | Microsecond UTC timestamp when the payment gateway processed the event. |
| `currency` | `VARCHAR` | Currency code (`USD`). |
| `amount_gross` | `DOUBLE` | Gross transaction value. Positive for captures/credits; negative for refunds and disputes. |
| `processing_fee` | `DOUBLE` | Fee charged by the gateway. Calculated via merchant fee tier schedules. |
| `amount_net` | `DOUBLE` | Net liquidity impact before reserve withholdings: `amount_gross - processing_fee`. |
| `fee_schedule_tier` | `VARCHAR` | Tier applied: `STANDARD_BLENDED` (2.9% + $0.30), `ENTERPRISE_INTERCHANGE_PLUS`, `DISPUTE_FEE` ($15.00). |
| `risk_reserve_rate` | `DOUBLE` | Rolling risk reserve rate (0.0500 = 5.0% holdback on gross captures). |
| `risk_reserve_hold_amount` | `DOUBLE` | Cash withheld from immediate bank settlement: `ROUND(amount_gross * 0.05, 2)`. |
| `risk_reserve_release_date`| `DATE` | Exactly `DATE(event_timestamp_utc) + INTERVAL 90 DAYS` for captures. |
| `settlement_status` | `VARCHAR` | Status: `PENDING_CLEARING`, `SETTLED`, `WITHHELD_IN_RESERVE`, `CHARGEBACK_DEBITED`. |
| `settlement_batch_id` | `VARCHAR` | Bank payout batch deposit reference (e.g. `po_batch_0042`). |
| `settlement_date_utc` | `DATE` | T+2 clearing date for net liquid bank deposits. |
| `failure_reason` | `VARCHAR` | Reason code for declined payments (if applicable). |
| `dispute_reason` | `VARCHAR` | Chargeback dispute reason (e.g. `fraudulent_unrecognized`). |
| `dispute_status` | `VARCHAR` | Dispute state (`UNDER_REVIEW`, `WON`, `LOST`). |
| `idempotency_key` | `VARCHAR` | Client idempotency key preventing duplicate processing. |

---

## Table 2: `erp_orders`
- **Domain:** Accrual ERP Sales Order Ledger (NetSuite)
- **Grain:** 1 row per commercial order booking.
- **Primary Key:** `order_id` (`VARCHAR`, e.g. `SO-2024-081294`)
- **Temporal Zone:** `TIMESTAMP` (Stored in local Eastern Time `America/New_York`)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `order_id` | `VARCHAR` | Primary Key. Commercial Sales Order Number. |
| `customer_account_id` | `VARCHAR` | Foreign Key to `customer_accounts.account_id`. |
| `buyer_profile_id` | `VARCHAR` | Foreign Key to `buyer_profiles.buyer_id` (NULL for guest orders). |
| `guest_checkout_token` | `VARCHAR` | Session checkout tracking token (resolvable in `customer_identity_mappings`). |
| `order_status` | `VARCHAR` | Order lifecycle: `PENDING_APPROVAL`, `APPROVED`, `FULFILLED`, `CANCELLED`, `CLOSED`. |
| `payment_method` | `VARCHAR` | Payment terms: `CREDIT_CARD`, `ACH_TRANSFER`, `NET30_INVOICE`, `NET60_INVOICE`. |
| `payment_intent_ref` | `VARCHAR` | Processor reference linking to `billing_events.payment_intent_id`. |
| `booking_timestamp_local` | `TIMESTAMP` | Booking timestamp in Eastern Business Time (`America/New_York`). |
| `order_timezone` | `VARCHAR` | Wall-clock timezone (`America/New_York`). |
| `currency` | `VARCHAR` | Functional currency (`USD`). |
| `gross_subtotal_amount` | `DOUBLE` | Sum of line catalog prices before discounts: `SUM(extended_gross_amount)`. |
| `promotional_discount_amount`| `DOUBLE`| Contractual or promotional discounts applied. |
| `tax_amount` | `DOUBLE` | State and local sales tax accrued (0.00 for tax-exempt B2B buyers). |
| `shipping_charged_amount` | `DOUBLE` | Shipping fee charged to customer (may differ from actual carrier freight cost). |
| `net_order_total_amount` | `DOUBLE` | Invoiced total: `gross_subtotal - promotional_discount + tax + shipping_charged`. |
| `cancellation_reason` | `VARCHAR` | `CUSTOMER_REQUEST_PRE_PACK`, `CUSTOMER_REQUEST_POST_PACK`, `PAYMENT_FAILED`. |
| `cancelled_at_local` | `TIMESTAMP` | Eastern timestamp when order was cancelled. |
| `closed_at_local` | `TIMESTAMP` | Eastern timestamp when accounting period was closed for this order. |

---

## Table 3: `erp_order_lines`
- **Domain:** Line Item & Revenue Recognition Ledger (NetSuite)
- **Grain:** 1 row per SKU line item within an order.
- **Primary Key:** `order_line_id` (`VARCHAR`, e.g. `SO-2024-081294-01`)
- **Foreign Keys:** `order_id` (FK to `erp_orders.order_id`), `sku_id`.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `order_line_id` | `VARCHAR` | Primary Key. Formatted as `{order_id}-{line_number:02d}`. |
| `order_id` | `VARCHAR` | Foreign Key referencing `erp_orders.order_id`. |
| `line_number` | `INTEGER` | 1-based sequential line index within the sales order. |
| `sku_id` | `VARCHAR` | Stock Keeping Unit code (e.g. `SKU-ENT-0042`). |
| `product_category` | `VARCHAR` | Category (e.g. `Enterprise Servers`, `Storage Arrays`, `Networking`). |
| `item_description` | `VARCHAR` | Product title. |
| `ordered_quantity` | `INTEGER` | Quantity ordered. |
| `cancelled_quantity` | `INTEGER` | Quantity cancelled prior to or post warehouse packaging. |
| `fulfilled_quantity` | `INTEGER` | Quantity physically manifested and dispatched by WMS. |
| `returned_quantity` | `INTEGER` | Quantity returned under an RMA. |
| `unit_catalog_price` | `DOUBLE` | Standard list price per unit. |
| `unit_discount_amount` | `DOUBLE` | Allocated discount per unit. |
| `unit_net_price` | `DOUBLE` | Net price per unit: `unit_catalog_price - unit_discount_amount`. |
| `extended_gross_amount` | `DOUBLE` | `ordered_quantity * unit_catalog_price`. |
| `extended_net_amount` | `DOUBLE` | `ordered_quantity * unit_net_price`. |
| `unit_cogs_amount` | `DOUBLE` | Inventory Cost of Goods Sold per unit. |
| `extended_cogs_amount` | `DOUBLE` | Total inventory COGS: `ordered_quantity * unit_cogs_amount`. |
| `rev_rec_status` | `VARCHAR` | ASC 606 revenue status: `PENDING_DELIVERY`, `RECOGNIZED_DELIVERED`, `REVERSED_CANCELLED`, `REVERSED_RETURN`. |
| `rev_rec_date_local` | `DATE` | Legal date revenue is recognized. Matches confirmed delivery date in WMS! |
| `return_rma_number` | `VARCHAR` | Return Merchandise Authorization reference (e.g. `RMA-2024-0012`). |
| `return_disposition` | `VARCHAR` | Return disposition: `RESTOCKED_A_STOCK`, `REFURBISHED_B_STOCK`, `DAMAGED_WRITE_OFF`. |

---

## Table 4: `wms_fulfillment`
- **Domain:** Warehouse Execution & Packaging Consignment (Manhattan WMS)
- **Grain:** 1 row per physical package / tracking consignment dispatched from a distribution center. (Orders fulfilling from multiple DCs generate multiple fulfillment packages: split shipments).
- **Primary Key:** `fulfillment_id` (`VARCHAR`, e.g. `FUL-081294-A`)
- **Temporal Zone:** `TIMESTAMPTZ` (UTC)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `fulfillment_id` | `VARCHAR` | Primary Key. Unique package identifier. |
| `order_id` | `VARCHAR` | Foreign Key referencing `erp_orders.order_id`. |
| `warehouse_id` | `VARCHAR` | Origin facility: `DC-EAST-01` (Allentown, PA), `DC-WEST-02` (Reno, NV), `DC-CENTRAL-03` (Dallas, TX). |
| `carrier_name` | `VARCHAR` | Carrier: `FEDEX`, `UPS`, `USPS`, `DHL_EXPRESS`. |
| `service_tier` | `VARCHAR` | Service tier: `GROUND`, `2_DAY_AIR`, `OVERNIGHT_PRIORITY`, `FREIGHT_LTL`. |
| `tracking_number` | `VARCHAR` | Carrier tracking barcode number. |
| `package_weight_lbs` | `DOUBLE` | Scale weight of carton in pounds. |
| `package_dim_l_in` | `DOUBLE` | Package length in inches. |
| `package_dim_w_in` | `DOUBLE` | Package width in inches. |
| `package_dim_h_in` | `DOUBLE` | Package height in inches. |
| `package_status` | `VARCHAR` | Package state: `ALLOCATED`, `PICKED`, `PACKED`, `DELIVERED`, `EXCEPTION_LOST`, `RETURNED_TO_ORIGIN`. |
| `allocated_timestamp_utc`| `TIMESTAMPTZ` | UTC timestamp when inventory was allocated to wave pick. |
| `shipped_timestamp_utc` | `TIMESTAMPTZ` | UTC timestamp when trailer departed warehouse loading dock. |
| `delivered_timestamp_utc`| `TIMESTAMPTZ`| UTC timestamp when carrier executed final delivery scan. |
| `actual_freight_cost` | `DOUBLE` | Actual freight cost billed by carrier to merchant (direct operational expense). |

---

## Table 5: `wms_package_scans`
- **Domain:** Carrier Logistics Telematics Event Stream (FedEx / UPS EDI feeds)
- **Grain:** 1 row per physical barcode scan or telematics event.
- **Primary Key:** `scan_id` (`BIGINT`)
- **Temporal Zone:** `TIMESTAMPTZ` (UTC)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `scan_id` | `BIGINT` | Primary Key. Monotonically increasing surrogate event ID. |
| `fulfillment_id` | `VARCHAR` | Foreign Key referencing `wms_fulfillment.fulfillment_id`. |
| `tracking_number` | `VARCHAR` | Carrier tracking number scanned. |
| `scan_event_code` | `VARCHAR` | Event: `PICK_COMPLETED`, `PACK_VERIFIED`, `CARRIER_RECEIVED`, `TRANSIT_HUB_ARRIVAL`, `OUT_FOR_DELIVERY`, `DELIVERY_CONFIRMED`, `LOST_IN_TRANSIT`, `RETURN_TO_SENDER_DELIVERED`. |
| `scan_timestamp_utc` | `TIMESTAMPTZ` | Microsecond UTC timestamp of scanner laser read. |
| `facility_code` | `VARCHAR` | IATA / DC code (e.g. `ABE1`, `RNO2`, `DFW3`, `ORD-HUB`). |
| `facility_city` | `VARCHAR` | City location of scanner. |
| `facility_state` | `VARCHAR` | State abbreviation (e.g. `PA`, `NV`, `TX`, `IL`). |
| `scan_device_id` | `VARCHAR` | Handheld scanner or conveyor optical belt ID. |
| `exception_reason` | `VARCHAR` | Details for transit exceptions (e.g. `CARRIER_CONTAINER_BREACH_SEARCH_EXHAUSTED`). |
| `signature_name` | `VARCHAR` | Name captured on driver delivery pad for `DELIVERY_CONFIRMED`. |

---

## Table 6: `customer_accounts`
- **Domain:** Master B2B Entity Hierarchy (MDM)
- **Grain:** 1 row per commercial enterprise parent or subsidiary account.
- **Primary Key:** `account_id` (`VARCHAR`, e.g. `ACCT-000001`)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `account_id` | `VARCHAR` | Primary Key. Account Master Record. |
| `parent_enterprise_id` | `VARCHAR` | Self-referencing FK to `customer_accounts.account_id` for corporate conglomerates with multiple subsidiaries. |
| `company_name` | `VARCHAR` | Legal corporate name (e.g. `Apex Global Technologies Inc.`). |
| `account_type` | `VARCHAR` | Segment: `ENTERPRISE`, `MID_MARKET`, `SMB`, `INDIVIDUAL_CONSUMER`. |
| `credit_limit_amount` | `DOUBLE` | Authorized trade credit limit for invoicing terms. |
| `payment_terms` | `VARCHAR` | Contract billing terms: `NET30`, `NET60`, `CREDIT_CARD_UPFRONT`. |
| `contract_discount_rate` | `DOUBLE` | Negotiated agreement discount (e.g. 0.1500 = 15%). |
| `is_tax_exempt` | `BOOLEAN` | Tax exemption status for certified B2B resellers. |
| `account_created_at_utc`| `TIMESTAMPTZ` | Account creation timestamp. |
| `sales_rep_id` | `VARCHAR` | Enterprise Account Executive ID. |

---

## Table 7: `buyer_profiles`
- **Domain:** Authorized Procurement Personnel
- **Grain:** 1 row per individual employee / corporate buyer authorized to place orders.
- **Primary Key:** `buyer_id` (`VARCHAR`, e.g. `BYR-000001`)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `buyer_id` | `VARCHAR` | Primary Key. Unique buyer profile ID. |
| `account_id` | `VARCHAR` | Foreign Key referencing `customer_accounts.account_id`. |
| `buyer_email` | `VARCHAR` | Corporate email address. |
| `full_name` | `VARCHAR` | Authorized buyer's full name. |
| `job_title` | `VARCHAR` | Job title (e.g. `VP Procurement`, `IT Director`). |
| `department` | `VARCHAR` | Department (`Infrastructure`, `R&D Operations`, `IT`). |
| `is_procurement_admin` | `BOOLEAN` | Whether authorized to approve high-dollar purchase orders. |
| `created_at_utc` | `TIMESTAMPTZ` | Buyer registration timestamp. |

---

## Table 8: `customer_identity_mappings`
- **Domain:** Cross-Device Identity Resolution Graph
- **Grain:** 1 row per checkout session, guest token, or device touchpoint.
- **Primary Key:** `mapping_id` (`BIGINT`)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `mapping_id` | `BIGINT` | Primary Key. Auto-incrementing mapping entry. |
| `session_id` | `VARCHAR` | Web session token (e.g. `sess_88b1...`). |
| `guest_checkout_token` | `VARCHAR` | Token assigned to unauthenticated checkout carts. |
| `device_fingerprint_hash`| `VARCHAR` | Client device fingerprint hash. |
| `ip_subnet_prefix` | `VARCHAR` | CIDR IP prefix. |
| `resolved_account_id` | `VARCHAR` | Resolved corporate account ID. |
| `resolved_buyer_id` | `VARCHAR` | Resolved authorized buyer ID. |
| `resolution_method` | `VARCHAR` | Method: `AUTHENTICATED_LOGIN`, `DETERMINISTIC_EMAIL_MATCH`, `PROBABILISTIC_DEVICE_MATCH`, `UNRESOLVED_GUEST`. |
| `confidence_score` | `DOUBLE` | Match confidence (1.00 = authenticated, 0.85 = email, 0.65 = device, 0.00 = guest). |
| `first_observed_utc` | `TIMESTAMPTZ` | Timestamp of first session observation. |
