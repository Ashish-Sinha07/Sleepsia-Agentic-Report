-- Create views for the Sleepsia Analytics API

-- View 1: Product Platform Daily Summary
CREATE OR REPLACE VIEW vw_product_platform_daily AS
SELECT
    ds.date,
    p.platform_id,
    p.platform_name as platform,
    ds.sku,
    pr.product_name,
    ds.orders,
    ds.units_sold,
    ds.gross_sales,
    ds.net_sales,
    ds.ad_attributed_sales,
    COALESCE(a.ad_spend, 0) as ad_spend,
    ds.units_sold as total_units_sold,
    CASE WHEN ds.ad_attributed_sales > 0 AND COALESCE(a.ad_spend, 0) > 0
         THEN ds.ad_attributed_sales / COALESCE(a.ad_spend, 0)
         ELSE NULL
    END as roas,
    CASE WHEN ds.ad_attributed_sales > 0 AND COALESCE(a.ad_spend, 0) > 0
         THEN (COALESCE(a.ad_spend, 0) / ds.ad_attributed_sales) * 100
         ELSE NULL
    END as acos_pct,
    CASE WHEN ds.gross_sales > 0
         THEN ((ds.gross_sales - ds.net_sales) / ds.gross_sales) * 100
         ELSE 0
    END as discount_pct,
    CASE WHEN ds.net_sales > 0 AND pr.product_cost > 0
         THEN ((ds.net_sales - (ds.units_sold * pr.product_cost)) / ds.net_sales) * 100
         ELSE 0
    END as profit_margin_pct,
    COALESCE(ret.units_returned, 0) as units_returned,
    COALESCE(can.units_cancelled, 0) as units_cancelled
FROM daily_sales ds
JOIN platforms p ON ds.platform_id = p.platform_id
JOIN products pr ON ds.sku = pr.sku
LEFT JOIN advertising a ON ds.date = a.date AND ds.platform_id = a.platform_id AND ds.sku = a.sku
LEFT JOIN returns ret ON ds.date = ret.date AND ds.platform_id = ret.platform_id AND ds.sku = ret.sku
LEFT JOIN cancellations can ON ds.date = can.date AND ds.platform_id = can.platform_id AND ds.sku = can.sku;

-- View 2: Daily KPI Summary
CREATE OR REPLACE VIEW vw_daily_kpi_summary AS
SELECT
    ds.date,
    SUM(ds.orders) as total_orders,
    SUM(ds.units_sold) as total_units_sold,
    SUM(ds.gross_sales) as total_gross_sales,
    SUM(ds.discount) as total_discount,
    SUM(ds.net_sales) as total_net_sales,
    SUM(ds.ad_attributed_sales) as total_ad_sales,
    SUM(ds.net_sales - ds.ad_attributed_sales) as total_organic_sales,
    COALESCE(SUM(a.ad_spend), 0) as total_ad_spend,
    CASE WHEN SUM(ds.ad_attributed_sales) > 0 AND COALESCE(SUM(a.ad_spend), 0) > 0
         THEN SUM(ds.ad_attributed_sales) / COALESCE(SUM(a.ad_spend), 0)
         ELSE NULL
    END as overall_roas,
    SUM(ds.net_sales - (ds.units_sold * COALESCE(pr.product_cost, 0))) as total_contribution,
    CASE WHEN SUM(ds.net_sales) > 0
         THEN (SUM(ds.net_sales - (ds.units_sold * COALESCE(pr.product_cost, 0))) / SUM(ds.net_sales)) * 100
         ELSE 0
    END as overall_profit_margin_pct,
    COALESCE(SUM(ret.units_returned), 0) as total_units_returned,
    COALESCE(SUM(can.units_cancelled), 0) as total_units_cancelled
FROM daily_sales ds
LEFT JOIN products pr ON ds.sku = pr.sku
LEFT JOIN advertising a ON ds.date = a.date AND ds.platform_id = a.platform_id AND ds.sku = a.sku
LEFT JOIN returns ret ON ds.date = ret.date AND ds.platform_id = ret.platform_id AND ds.sku = ret.sku
LEFT JOIN cancellations can ON ds.date = can.date AND ds.platform_id = can.platform_id AND ds.sku = can.sku
GROUP BY ds.date;

-- Verify views were created
SELECT "Views created successfully" AS Status;
