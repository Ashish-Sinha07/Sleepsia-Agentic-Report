# Data Profile: Sleepsia Agentic Report System

## Executive Summary

**File:** `data/final_sleepsia_report_data.xlsx`  
**Total Sheets:** 20  
**Data Period:** 2026-06-21 to 2026-08-21 (62 days)  
**Primary Grain:** Product × Platform × Date  
**Data Type:** Synthetic prototype dataset for business reporting and analytics

---

## 1. Sheet Inventory

### 1.1 Reference/Master Data

| Sheet | Rows | Purpose | Key Fields |
|-------|------|---------|-----------|
| **Product_Master** | 8 | Product catalog with pricing and costs | SKU, ProductName, ProductType, SellingPrice_INR, ProductCost_INR |
| **Platform_Master** | 4 | Supported sales platforms | PlatformID, Platform, DefaultPlatformFeePct |
| **Warehouse_Master** | 5 | Regional warehouse locations | WarehouseID, Region, Zone, City, StorageCapacity_Units |
| **Business_Config** | 10 | Business rules and thresholds | ConfigKey, Value, Description |
| **Supply_Chain_Config** | 7 | Inventory rules and thresholds | ConfigKey, Value, Unit/Threshold |
| **README** | 10 | Data metadata and usage notes | Item, Description, Copilot Studio Prototype Note |
| **TABLE_DIRECTORY** | 18 | Excel table mapping to sheets | Excel Table Name, Source Sheet, Purpose |

### 1.2 Transactional Data

| Sheet | Rows | Purpose | Key Fields |
|-------|------|---------|-----------|
| **Daily_Sales** | 744 | Daily sales by platform and product | Date, PlatformID, SKU, Orders, UnitsSold, GrossSales_INR, NetSales_INR, AdAttributedUnits |
| **Advertising** | 744 | Daily advertising performance and spend | Date, PlatformID, SKU, Impressions, Clicks, AttributedOrders, AdSpend_INR, ROAS, ACOS_Pct |
| **Daily_Costs** | 744 | Daily operational costs | Date, PlatformID, SKU, ProductCost_INR, PlatformFee_INR, ShippingCost_INR, PaymentFee_INR, OtherVariableCost_INR |
| **Returns** | 275 | Return transactions | ReturnID, ReturnDate, PlatformID, SKU, UnitsReturned, RefundAmount_INR, Reason |
| **Cancellations** | 142 | Canceled orders | CancellationID, CancellationDate, PlatformID, SKU, UnitsCancelled, Reason |

### 1.3 Regional/Warehouse Data

| Sheet | Rows | Purpose | Key Fields |
|-------|------|---------|-----------|
| **Regional_Sales** | 930 | Sales by warehouse and region | Date, WarehouseID, Region, SKU, UnitsSold, NetSales_INR |
| **Inventory_Daily** | 930 | Daily inventory by warehouse | Date, WarehouseID, SKU, OpeningStock_Units, ClosingStock_Units, DaysOfCover, StockStatus |
| **Regional_KPI** | 930 | Regional performance KPIs | Date, WarehouseID, SKU, DaysOfCover, StockStatus, DemandFulfillmentPct |
| **Replenishment_Alerts** | 11 | Low-stock and reorder alerts | Date, WarehouseID, SKU, StockStatus, Priority, RecommendedAction |

### 1.4 Aggregated/Summary Data

| Sheet | Rows | Purpose | Key Fields |
|-------|------|---------|-----------|
| **Daily_KPI** | 744 | Consolidated daily KPIs (all metrics) | Date, PlatformID, SKU, + 31 metrics including Orders, Profit_INR, ProfitMargin_Pct, ReturnRate_Pct, OrganicShare_Pct |
| **Management_Summary** | 10 | High-level business metrics | Metric (Total Net Sales, Total Units, Total Ad Spend, Organic/Inorganic split) |
| **Regional_Top_Products** | 15 | Top 3 products per region | Region, SKU, UnitsSold, NetSales_INR, RankInRegion |
| **Supply_Chain_Summary** | 5 | Warehouse health snapshot | WarehouseID, TotalStock_Units, LowStockSKUs, StockoutSKUs, WarehouseHealth |

---

## 2. Data Types & Field Specifications

### 2.1 Dimension Fields (All Sheets)

| Field | Type | Cardinality | Notes |
|-------|------|-------------|-------|
| Date | datetime64 | 62 unique dates | Continuous daily data |
| PlatformID | string | 4 values (AMZ, BLK, FLP, MTR) | Foreign key to Platform_Master |
| Platform | string | 4 values | Denormalized from PlatformID |
| WarehouseID | string | 5 values (WH-NCR, WH-JPR, WH-MUM, WH-BLR, WH-HYD) | Foreign key to Warehouse_Master |
| Region | string | 5 regions (Delhi NCR, Jaipur, Mumbai, Bengaluru, Hyderabad) | Denormalized from WarehouseID |
| Zone | string | 3 zones (North, West, South) | Denormalized from WarehouseID |
| SKU | string | 3 unique SKUs (SLP-1001, SLP-1002, SLP-1003) | Foreign key to Product_Master |
| ProductName | string | 3 unique names | Denormalized from SKU |

### 2.2 Numeric Fields (Sales & Revenue)

| Field | Type | Range | Notes |
|-------|------|-------|-------|
| UnitsSold | int64 | 1-20 units/day | Daily sales volume |
| Orders | int64 | 1-20 orders/day | Daily order count |
| GrossSales_INR | int64 | ₹7,992 - ₹14,990 | Before discounts |
| Discount_INR | float64 | ₹0 - ₹659.49 | Varies by platform |
| NetSales_INR | float64 | ₹7,332.51 - ₹14,591.38 | After discounts |
| AdAttributedSales_INR | float64 | ₹2,839.50 - ₹8,754.83 | Ad-driven revenue |
| OrganicSales_INR | float64 | ₹3,666.25 - ₹5,836.55 | Non-ad revenue (derived) |

### 2.3 Numeric Fields (Costs)

| Field | Type | Notes |
|-------|------|-------|
| ProductCost_INR | int64 | COGS per unit; 52 unique values in Daily_Costs |
| PlatformFee_INR | float64 | Commission based on platform and sales |
| ShippingCost_INR | float64 | Logistics cost per order |
| PaymentFee_INR | float64 | Payment gateway fees |
| OtherVariableCost_INR | float64 | Miscellaneous variable costs |

### 2.4 Numeric Fields (Advertising)

| Field | Type | Notes |
|-------|------|-------|
| Impressions | int64 | Ad views (range: 617 - 1,911 per day) |
| Clicks | int64 | Ad clicks (range: 37 - 102 per day) |
| CTR_Pct | float64 | Click-Through Rate (3.39% - 6.16%) |
| AttributedOrders | int64 | Attributed to ads (0-9 orders) |
| AttributedUnits | int64 | Attributed to ads (0-9 units) |
| AdSpend_INR | float64 | Daily ad spend (₹824 - ₹1,419 per SKU/platform) |
| ROAS | float64 | Return on Ad Spend (3.44 - 6.17x) |
| ACOS_Pct | float64 | Ad Cost of Sale (16.21% - 29.03%) |

### 2.5 Numeric Fields (Inventory)

| Field | Type | Notes |
|-------|------|-------|
| OpeningStock_Units | int64 | BOD inventory (0-183 units) |
| InboundStock_Units | int64 | Received stock (0-50 units, mostly 0) |
| ClosingStock_Units | int64 | EOD inventory (0-207 units) |
| Demand_Units | int64 | Daily demand (4-20 units) |
| Fulfilled_Units | int64 | Orders fulfilled (4-20 units, 100% in data) |
| AvgDailyDemand_7D | int64 | 7-day rolling average (3, 7, or 8 units) |
| DaysOfCover | float64 | Stock coverage (0-36 days) |

### 2.6 Categorical Fields

| Field | Type | Values | Notes |
|-------|------|--------|-------|
| ProfitabilityStatus | string | "Healthy", "At Risk", "Critical" | Daily_KPI sheet only |
| StockStatus | string | "Healthy", "Low Stock", "Critical", "Stockout" | Inventory_Daily, Regional_KPI |
| Stockout | string | "No" (only value in data) | Boolean flag |
| Status (Warehouse) | string | "Active" (all) | Warehouse_Master |
| Status (Returns) | string | "Completed" (all) | Returns sheet |
| Priority (Alerts) | string | "Medium", "High" | Replenishment_Alerts |
| Active (Products) | string | "Yes" (all) | Product_Master |
| Active (Platforms) | string | "Yes" (all) | Platform_Master |

---

## 3. Derived & Calculated Fields

### 3.1 Sales-Derived Fields

| Field | Formula | Location | Notes |
|-------|---------|----------|-------|
| NetSales_INR | GrossSales_INR - Discount_INR | Daily_Sales, Daily_KPI, Regional_Sales | Pre-cost revenue |
| OrganicUnits | UnitsSold - AdAttributedUnits | Daily_KPI | Non-ad units |
| OrganicSales_INR | NetSales_INR - AdAttributedSales_INR | Daily_KPI | Non-ad revenue |
| OrganicShare_Pct | OrganicUnits / UnitsSold × 100 | Daily_KPI | Organic vs. paid ratio |

### 3.2 Financial-Derived Fields

| Field | Formula | Location | Notes |
|-------|---------|----------|-------|
| TotalVariableCost_INR | ProductCost + PlatformFee + ShippingCost + PaymentFee + Other | Daily_KPI (implied) | Not directly stored; calculated in aggregations |
| Contribution_INR | NetSales_INR - TotalVariableCost - AdSpend | Daily_KPI | Profit before overhead |
| ProfitMargin_Pct | (Contribution_INR / NetSales_INR) × 100 | Daily_KPI | Contribution margin % |

### 3.3 Advertising-Derived Fields

| Field | Formula | Location | Notes |
|-------|---------|----------|-------|
| ROAS | AdAttributedSales_INR / AdSpend_INR | Advertising, Daily_KPI | Revenue per rupee of ads |
| ACOS_Pct | (AdSpend_INR / AdAttributedSales_INR) × 100 | Advertising, Daily_KPI | Cost as % of attributed revenue |

### 3.4 Inventory-Derived Fields

| Field | Formula | Location | Notes |
|-------|---------|----------|-------|
| ClosingStock_Units | OpeningStock + InboundStock - Demand | Inventory_Daily, Regional_KPI | EOD inventory |
| DaysOfCover | ClosingStock_Units / AvgDailyDemand_7D | Inventory_Daily, Regional_KPI | Stock runway |
| DemandFulfillmentPct | (Fulfilled_Units / Demand_Units) × 100 | Regional_KPI | Order fill rate |

---

## 4. Relationships & Foreign Keys

### 4.1 Primary Keys

| Sheet | Primary Key | Type |
|-------|-------------|------|
| Product_Master | SKU | Natural (business key) |
| Platform_Master | PlatformID | Natural |
| Warehouse_Master | WarehouseID | Natural |
| Returns | ReturnID | Surrogate |
| Cancellations | CancellationID | Surrogate |
| Daily_KPI | (Date, PlatformID, SKU) | Composite |
| Inventory_Daily | (Date, WarehouseID, SKU) | Composite |
| Regional_Sales | (Date, WarehouseID, SKU) | Composite |

### 4.2 Relationships

```
Daily_Sales --[PlatformID]--> Platform_Master
Daily_Sales --[SKU]--> Product_Master
Daily_Sales --[AdAttributedUnits]--[SKU, PlatformID, Date]--> Advertising

Inventory_Daily --[WarehouseID]--> Warehouse_Master
Inventory_Daily --[SKU]--> Product_Master

Regional_Sales --[WarehouseID]--> Warehouse_Master
Regional_Sales --[SKU]--> Product_Master

Returns --[PlatformID, SKU, ReturnDate]--> Daily_Sales (implied)
Cancellations --[PlatformID, SKU, CancellationDate]--> Daily_Sales (implied)

Daily_KPI --[composed of]--> Daily_Sales + Advertising + Daily_Costs + Returns + Cancellations
```

---

## 5. Duplicate & Denormalized Fields

### 5.1 Intentional Denormalization

The following fields are stored redundantly for convenience in transactions sheets:

| Original | Denormalized Fields | Reason |
|----------|-------------------|--------|
| PlatformID (dimension) | Platform (string) | Display name convenience |
| SKU (dimension) | ProductName (string) | Display name convenience |
| WarehouseID (dimension) | Region (string) | Geographic context |
| WarehouseID (dimension) | Zone (string) | Zone classification |

**Data Quality Impact:** No inconsistencies detected. Denormalization is consistent across sheets.

### 5.2 Field Replication Across Sheets

| Field | Appears In | Grain | Notes |
|-------|-----------|-------|-------|
| UnitsSold | Daily_Sales, Daily_KPI, Regional_Sales, Regional_KPI | Daily | Consistent across aggregations |
| NetSales_INR | Daily_Sales, Daily_KPI, Regional_Sales, Regional_KPI | Daily | May aggregate differently at regional level |
| DaysOfCover | Inventory_Daily, Regional_KPI, Replenishment_Alerts | Daily | Consistent calculation |
| StockStatus | Inventory_Daily, Regional_KPI, Replenishment_Alerts, Supply_Chain_Summary | Daily/Snapshot | Category consistent; some rows overlap |

---

## 6. Data Quality Issues & Observations

### 6.1 Data Completeness

| Issue | Severity | Details | Recommendation |
|-------|----------|---------|-----------------|
| **Stockout field always "No"** | LOW | Column in Inventory_Daily and Regional_KPI shows 100% "No" | Likely placeholder; monitor for actual stockouts |
| **Returns sheet: 100% "Completed" status** | LOW | Returns status only shows "Completed"; no pending/rejected states | Reflects transactional history only; expected |
| **Cancellations: Missing refund amounts** | MEDIUM | Cancellations sheet has no RefundAmount_INR; only Units | Business process question: what's the refund policy? |
| **NULL values in Business_Config** | LOW | Unit/Threshold column has 9 NULLs out of 10 rows | Acceptable; only 1 threshold-based config item |

### 6.2 Data Consistency

| Issue | Severity | Details | Recommendation |
|-------|----------|---------|-----------------|
| **SKU cardinality mismatch** | MEDIUM | Product_Master has 8 SKUs; Daily_Sales/Advertising only has 3 (SLP-1001, 1002, 1003) | Some products inactive in data period; verify with Product_Master.Active |
| **Platform cardinality mismatch** | LOW | Platform_Master lists 4 platforms; only 4 appear in Daily_Sales | All platforms active; no issue |
| **Warehouse cardinality mismatch** | LOW | Warehouse_Master has 5 warehouses; all 5 present in Inventory_Daily | All warehouses active; no issue |

### 6.3 Temporal Consistency

| Issue | Severity | Details | Recommendation |
|-------|----------|---------|-----------------|
| **Non-continuous date range** | LOW | 62 unique dates from 2026-06-21 to 2026-08-21 | Likely includes weekends; confirm business intent for weekend reporting |
| **Returns/Cancellations less frequent** | LOW | 275 returns, 142 cancellations for 744 sales rows | 3.7% return rate, 1.9% cancellation rate; realistic |

### 6.4 Logical/Business Inconsistencies

| Issue | Severity | Details | Recommendation |
|-------|----------|---------|-----------------|
| **Possible order fulfillment issue** | MEDIUM | Inventory_Daily shows Fulfilled_Units = Demand_Units (100% fill rate) but separate columns exist | Data synthetic; real system may have partial fulfillment |
| **Replenishment_Alerts SLP-1002 bias** | LOW | 11 alerts all for SLP-1002 (Travel Pillow) at WH-NCR/WH-JPR | Likely hotspot; monitor reorder performance |
| **ProductCost_INR variations** | MEDIUM | Same SKU has different ProductCost in Daily_Costs (52 unique) vs. Product_Master (fixed) | Daily_Costs may reflect dynamic costing; need clarification |
| **Missing price data** | LOW | Product_Master.SellingPrice_INR NOT matched to Daily_Sales.GrossSales_INR | GrossSales may aggregate or reflect discounts; needs reconciliation |

### 6.5 Data Validation Rules Not Enforced

| Constraint | Status | Risk |
|-----------|--------|------|
| NetSales_INR ≤ GrossSales_INR (discount shouldn't exceed gross) | Not checked | LOW; visually confirmed in sample |
| DaysOfCover ≥ 0 | Not checked | LOW; sample shows non-negative |
| ACOS_Pct ≥ 0 | Not checked | LOW; sample shows positive |
| RefundAmount_INR ≤ NetSales_INR per order | Not checked | MEDIUM; cannot verify without order mapping |
| ClosingStock_Units ≥ 0 | Not checked | MEDIUM; recommend constraint in data load |
| DemandFulfillmentPct ∈ [0, 100] | Not checked | LOW; sample shows 100% only |

---

## 7. Data Volume & Growth

### 7.1 Row Counts by Entity

| Entity | Rows | Grain | Growth Driver |
|--------|------|-------|---------------|
| Daily_Sales | 744 | Date × PlatformID × SKU | 62 days × 4 platforms × 3 SKUs = 744 |
| Advertising | 744 | Date × PlatformID × SKU | Same as Daily_Sales |
| Daily_Costs | 744 | Date × PlatformID × SKU | Same as Daily_Sales |
| Daily_KPI | 744 | Date × PlatformID × SKU | Consolidated from above |
| Inventory_Daily | 930 | Date × WarehouseID × SKU | 62 days × 5 warehouses × 3 SKUs = 930 |
| Regional_Sales | 930 | Date × WarehouseID × SKU | Same as Inventory_Daily |
| Regional_KPI | 930 | Date × WarehouseID × SKU | Same as Inventory_Daily |
| Returns | 275 | Return transaction | ~4.7% of gross sales |
| Cancellations | 142 | Cancellation transaction | ~1.9% of orders |
| Replenishment_Alerts | 11 | Alert day | Low-stock alerts only |

**Estimation for production (assuming 1 year of 365 days):**
- Daily_Sales/KPI: ~4,380 rows (7% of sample size)
- Returns: ~1,620 rows
- Cancellations: ~836 rows
- Inventory: ~5,475 rows
- **Estimate: 12K-20K operational rows; easily handled by MySQL**

---

## 8. Data Integrity & Quality Summary

### 8.1 Strengths

✅ **Complete dimensional coverage** – All required dimensions present (Date, Platform, SKU, Warehouse)  
✅ **No missing values** – 100% population in key transactional fields  
✅ **Logical calculated fields** – Derived metrics follow expected formulas (ROAS, ACOS, DaysOfCover)  
✅ **Referential consistency** – Dimension values appear consistently across related tables  
✅ **Realistic ranges** – Numeric values (discounts, rates, costs) within expected bounds  

### 8.2 Weaknesses

⚠️ **Synthetic data** – All operational values are prototype; may not reflect real business patterns  
⚠️ **Incomplete product SKUs** – Only 3 of 8 products active in data period  
⚠️ **Missing order-line mappings** – Returns/Cancellations not linked to specific Daily_Sales rows  
⚠️ **No audit timestamps** – Created/Modified dates not present for transaction tables  
⚠️ **Possible cost discrepancies** – ProductCost varies in Daily_Costs but fixed in Product_Master  
⚠️ **Perfect fulfillment** – Inventory_Daily shows 100% demand fulfillment; unrealistic edge case  

---

## 9. Recommended Data Model Improvements

### 9.1 For Production MVP

1. **Add timestamps** – CreatedAt, ModifiedAt (UTC) to Returns, Cancellations, Daily_* tables  
2. **Link returns/cancellations** – Add OrderID or (Date, PlatformID, SKU, OrderIndex) to tie back to Daily_Sales  
3. **Clarify costs** – Document whether ProductCost_INR in Daily_Costs is dynamic or fixed per SKU  
4. **Validate constraints** – Add database constraints:
   - CHECK (ClosingStock_Units >= 0)
   - CHECK (DaysOfCover >= 0)
   - CHECK (RefundAmount_INR > 0)
   - CHECK (ReturnRate_Pct BETWEEN 0 AND 100)
5. **Index strategy** – Primary: (Date, PlatformID, SKU); Secondary: (WarehouseID, Date), (SKU, Date)

### 9.2 For Analytics

1. **Create views** – Pre-aggregate common queries (daily total revenue, platform comparisons, region rankings)  
2. **Add surrogate keys** – For dimension tables to enable referential integrity in transaction tables  
3. **Snapshot tables** – Daily snapshot of warehouse inventory/reorder status for trend analysis  
4. **Reconciliation fields** – Add total_cost_check = ProductCost + PlatformFee + ... for audit  

---

## 10. Attached Data Lineage

**Source of Truth:** Product_Master, Platform_Master, Warehouse_Master (reference data)

**Derived Lineage:**
```
Daily_Sales (raw) + Advertising (raw) + Daily_Costs (raw) + Returns + Cancellations
    ↓
    → Daily_KPI (consolidated)
    
Inventory_Daily (raw) + Regional_Sales (raw)
    ↓
    → Regional_KPI (consolidated)
    ↓
    → Replenishment_Alerts (filtered)
    ↓
    → Supply_Chain_Summary (aggregated)

Daily_KPI
    ↓
    → Management_Summary (aggregated)
    → Regional_Top_Products (ranked)
```

---

## 11. Known Limitations

1. **Synthetic data** – Not representative of real Sleepsia business; for prototype/demo only  
2. **Static costs** – Product costs do not vary by platform (real systems may have negotiated rates)  
3. **No supplier/logistics master** – Shipping costs not traced to carriers or zones  
4. **No customer data** – Segment/cohort analysis not possible  
5. **No SKU attributes** – Material, IntendedUse in master but not used in analytics  
6. **Limited alerting** – Only stock-related alerts; no margin, ROAS, or anomaly detection  
7. **No audit trail** – No user/system record of data modifications  

---

## Conclusion

The Excel workbook provides a **complete, well-structured prototype dataset** suitable for MVP development. All core business dimensions and KPIs are represented. Data is **clean and consistent** with no critical gaps for Phase 1 (sales, profitability, inventory). Recommend moving this to MySQL with additional business rules validation and production enhancements as described in Section 9.

**Ready for:** ✅ MySQL schema design ✅ FastAPI data layer ✅ React dashboard prototyping

**Not ready for:** ❌ Production transaction processing ❌ External customer reporting ❌ Compliance audits
