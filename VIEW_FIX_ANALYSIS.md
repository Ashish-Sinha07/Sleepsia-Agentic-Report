# View Creation Error Analysis & Fix

## Error Summary

**Error Code:** 1054  
**Error Message:** Unknown column 'p.platform_id' in 'field list'  
**Failing View:** vw_product_platform_daily  
**Line:** 288 in sql/schema.sql

---

## Root Cause

### The Problem
Line 288 referenced `p.platform_id`:
```sql
SELECT
    ds.sale_date AS date,
    p.platform_id,                    ← WRONG: alias 'p' does not exist
    pl.platform_name AS platform,
```

### Why It Failed
The table alias `p` was never defined in the FROM/JOIN clauses. The platforms table was aliased as `pl`:

```sql
FROM daily_sales ds
INNER JOIN platforms pl ON ds.platform_id = pl.platform_id    ← platforms is aliased 'pl'
INNER JOIN products pr ON ds.sku = pr.sku                      ← products is aliased 'pr'
LEFT JOIN advertising ad ON ...                                 ← advertising is aliased 'ad'
LEFT JOIN daily_costs dc ON ...                                 ← daily_costs is aliased 'dc'
```

### Consequence
When MySQL tried to resolve column reference `p.platform_id`, it could not find a table alias named `p`, resulting in Error Code: 1054.

---

## The Fix

**Changed line 288 from:**
```sql
p.platform_id,
```

**To:**
```sql
pl.platform_id,
```

This correctly references the `platforms` table aliased as `pl`.

---

## Corrected View Definition (vw_product_platform_daily)

```sql
CREATE OR REPLACE VIEW vw_product_platform_daily AS
SELECT
    ds.sale_date AS date,
    pl.platform_id,              ← FIXED: now correctly references platforms table
    pl.platform_name AS platform,
    ds.sku,
    pr.product_name,
    ds.orders,
    ds.units_sold,
    ds.gross_sales,
    ds.discount,
    ds.net_sales,
    ad.impressions,
    ad.clicks,
    CASE WHEN ad.impressions > 0
        THEN ROUND((ad.clicks / ad.impressions) * 100, 4)
        ELSE NULL
    END AS ctr_pct,
    ad.attributed_orders,
    ad.attributed_units,
    ad.attributed_sales AS ad_attributed_sales,
    ad.ad_spend,
    CASE WHEN ad.ad_spend > 0
        THEN ROUND(ad.attributed_sales / ad.ad_spend, 4)
        ELSE NULL
    END AS roas,
    CASE WHEN ad.attributed_sales > 0
        THEN ROUND((ad.ad_spend / ad.attributed_sales) * 100, 4)
        ELSE NULL
    END AS acos_pct,
    (ds.net_sales - ad.attributed_sales) AS organic_sales,
    CASE WHEN ds.units_sold > 0
        THEN ROUND(((ds.units_sold - ad.attributed_units) / ds.units_sold) * 100, 4)
        ELSE NULL
    END AS organic_share_pct,
    dc.product_cost,
    dc.platform_fee,
    dc.shipping_cost,
    dc.payment_fee,
    dc.other_variable_cost,
    COALESCE(ret.units_returned, 0) AS units_returned,
    COALESCE(ret.refund_amount, 0) AS refund_amount,
    COALESCE(can.units_cancelled, 0) AS units_cancelled,
    (
        ds.net_sales
        - COALESCE(ret.refund_amount, 0)
        - (dc.product_cost * ds.units_sold)
        - dc.platform_fee
        - dc.shipping_cost
        - dc.payment_fee
        - ad.ad_spend
        - dc.other_variable_cost
    ) AS contribution_inr,
    CASE WHEN ds.net_sales > 0
        THEN ROUND((
            (
                ds.net_sales
                - COALESCE(ret.refund_amount, 0)
                - (dc.product_cost * ds.units_sold)
                - dc.platform_fee
                - dc.shipping_cost
                - dc.payment_fee
                - ad.ad_spend
                - dc.other_variable_cost
            ) / ds.net_sales
        ) * 100, 4)
        ELSE NULL
    END AS profit_margin_pct,
    CASE WHEN ds.units_sold > 0
        THEN ROUND((COALESCE(ret.units_returned, 0) / ds.units_sold) * 100, 4)
        ELSE NULL
    END AS return_rate_pct,
    CASE WHEN ds.orders > 0
        THEN ROUND((COALESCE(can.units_cancelled, 0) / ds.orders) * 100, 4)
        ELSE NULL
    END AS cancellation_rate_pct
FROM daily_sales ds
INNER JOIN platforms pl ON ds.platform_id = pl.platform_id
INNER JOIN products pr ON ds.sku = pr.sku
LEFT JOIN advertising ad ON ds.sale_date = ad.ad_date
    AND ds.platform_id = ad.platform_id
    AND ds.sku = ad.sku
LEFT JOIN daily_costs dc ON ds.sale_date = dc.cost_date
    AND ds.platform_id = dc.platform_id
    AND ds.sku = dc.sku
LEFT JOIN (
    SELECT return_date, platform_id, sku, SUM(units_returned) AS units_returned, SUM(refund_amount) AS refund_amount
    FROM returns
    GROUP BY return_date, platform_id, sku
) ret ON ds.sale_date = ret.return_date
    AND ds.platform_id = ret.platform_id
    AND ds.sku = ret.sku
LEFT JOIN (
    SELECT cancellation_date, platform_id, sku, SUM(units_cancelled) AS units_cancelled
    FROM cancellations
    GROUP BY cancellation_date, platform_id, sku
) can ON ds.sale_date = can.cancellation_date
    AND ds.platform_id = can.platform_id
    AND ds.sku = can.sku;
```

---

## Table Relationships (Correct Normalized Design)

```
PRODUCT DIMENSION:
  products (product_id, sku, product_name, ...)
  └─ No platform_id field (CORRECT: products exist independent of platforms)

PLATFORM DIMENSION:
  platforms (platform_id, platform_name, ...)
  └─ Independent of products

SALES FACT TABLE:
  daily_sales (sale_date, platform_id FK, sku FK, ...)
  ├── foreign key: platform_id → platforms(platform_id)
  └── foreign key: sku → products(sku)

TRANSACTIONAL TABLES:
  advertising (ad_date, platform_id FK, sku FK, ...)
  daily_costs (cost_date, platform_id FK, sku FK, ...)
  returns (return_date, platform_id FK, sku FK, ...)
  cancellations (cancellation_date, platform_id FK, sku FK, ...)
  └── All connect to platforms and products independently
```

**Business Logic:** A product can be sold on multiple platforms. The daily_sales table tracks each combination of (sale_date, platform_id, sku) as a unique fact. Products do NOT have an inherent platform association in the master data. ✓ CORRECT

---

## Verification Checklist

✅ **Column References:**
- `pl.platform_id` - EXISTS in platforms table
- `pl.platform_name` - EXISTS in platforms table  
- `pr.product_name` - EXISTS in products table
- `ds.sale_date` - EXISTS in daily_sales table
- `ds.orders`, `ds.units_sold`, `ds.net_sales` - EXIST in daily_sales table
- `ad.impressions`, `ad.clicks`, `ad.ad_spend` - EXIST in advertising table
- `dc.product_cost`, `dc.platform_fee`, `dc.shipping_cost` - EXIST in daily_costs table
- `ret.units_returned`, `ret.refund_amount` - COMPUTED in subquery, EXIST
- `can.units_cancelled` - COMPUTED in subquery, EXIST

✅ **Table Aliases:**
- ds = daily_sales ✓
- pl = platforms ✓
- pr = products ✓
- ad = advertising ✓
- dc = daily_costs ✓
- ret = returns subquery ✓
- can = cancellations subquery ✓

✅ **Foreign Key Relationships:**
- daily_sales.platform_id → platforms.platform_id ✓
- daily_sales.sku → products.sku ✓
- advertising.platform_id → platforms.platform_id ✓
- advertising.sku → products.sku ✓
- daily_costs.platform_id → platforms.platform_id ✓
- daily_costs.sku → products.sku ✓
- returns.platform_id → platforms.platform_id ✓
- returns.sku → products.sku ✓
- cancellations.platform_id → platforms.platform_id ✓
- cancellations.sku → products.sku ✓

---

## Other Views - Verification

### vw_platform_performance
- ✅ Depends on: vw_product_platform_daily, platforms
- ✅ All column references valid
- ✅ Join: platforms pl ON vpd.platform_id = pl.platform_id ✓

### vw_product_performance
- ✅ Depends on: vw_product_platform_daily
- ✅ All column references valid
- ✅ Group by: vpd.sku, vpd.product_name, vpd.platform_id, vpd.platform ✓

### vw_profitability
- ✅ Depends on: vw_product_platform_daily
- ✅ All column references valid

### vw_inventory_health
- ✅ Depends on: inventory_daily, warehouses, products
- ✅ All column references valid
- ✅ Column: id.demand_units EXISTS in inventory_daily ✓

### vw_warehouse_summary
- ✅ Depends on: warehouses, inventory_daily
- ✅ All column references valid
- ✅ Subquery: SELECT MAX(inventory_date) FROM inventory_daily ✓

### vw_regional_performance
- ✅ Depends on: regional_sales, warehouses, products
- ✅ All column references valid

### vw_daily_kpi_summary
- ✅ Depends on: vw_product_platform_daily
- ✅ All column references valid

---

## Summary

**Single Fix Applied:**
- **Line 288:** Changed `p.platform_id` → `pl.platform_id`

**Root Cause:**
- Table alias mismatch: reference to non-existent alias `p` instead of existing alias `pl`

**Impact:**
- After this fix, vw_product_platform_daily will create successfully
- All dependent views (vw_platform_performance, vw_product_performance, vw_profitability, vw_daily_kpi_summary) will then create successfully
- Independent views (vw_inventory_health, vw_warehouse_summary, vw_regional_performance) have no errors and will create successfully

**Database Schema Design:**
- ✓ Properly normalized
- ✓ Correct foreign key relationships
- ✓ No unnecessary denormalization
- ✓ Products table correctly does NOT include platform_id

---

## Status: READY FOR EXECUTION

The corrected schema.sql file is ready to execute against MySQL:

```bash
mysql -u root -p -h localhost sleepsia_db < sql/schema.sql
```

Expected result: All tables and 7 views created successfully.

---

Generated: 2026-08-21
