-- ============================================================================
-- Sleepsia Agentic Business Reporting System
-- MySQL 8+ Schema
-- ============================================================================

-- ============================================================================
-- 1. MASTER DATA TABLES
-- ============================================================================

-- Products Master
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(20) NOT NULL UNIQUE,
    product_name VARCHAR(255) NOT NULL,
    product_type VARCHAR(100),
    material VARCHAR(100),
    intended_use VARCHAR(255),
    primary_market VARCHAR(100),
    selling_price DECIMAL(18,2) NOT NULL,
    product_cost DECIMAL(18,2) NOT NULL,
    target_margin_pct DECIMAL(10,4),
    brand VARCHAR(100),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_sku (sku),
    INDEX idx_active (active),
    INDEX idx_product_type (product_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Platforms Master
CREATE TABLE IF NOT EXISTS platforms (
    platform_id VARCHAR(10) PRIMARY KEY,
    platform_name VARCHAR(100) NOT NULL UNIQUE,
    sales_channel_type VARCHAR(50),
    default_platform_fee_pct DECIMAL(10,4) NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_active (active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Warehouses Master
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id VARCHAR(20) PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    zone VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    storage_capacity_units INT,
    status VARCHAR(50) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_region (region),
    INDEX idx_zone (zone),
    INDEX idx_city (city),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 2. TRANSACTIONAL TABLES
-- ============================================================================

-- Daily Sales
CREATE TABLE IF NOT EXISTS daily_sales (
    sales_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_date DATE NOT NULL,
    platform_id VARCHAR(10) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    orders INT DEFAULT 0,
    units_sold INT DEFAULT 0,
    gross_sales DECIMAL(18,2) DEFAULT 0,
    discount DECIMAL(18,2) DEFAULT 0,
    net_sales DECIMAL(18,2) DEFAULT 0,
    ad_attributed_units INT DEFAULT 0,
    ad_attributed_sales DECIMAL(18,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    FOREIGN KEY (sku) REFERENCES products(sku),
    UNIQUE KEY uk_daily_sales (sale_date, platform_id, sku),
    INDEX idx_sale_date (sale_date),
    INDEX idx_platform_id (platform_id),
    INDEX idx_sku (sku),
    INDEX idx_date_platform_sku (sale_date, platform_id, sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Daily Advertising
CREATE TABLE IF NOT EXISTS advertising (
    advertising_id INT AUTO_INCREMENT PRIMARY KEY,
    ad_date DATE NOT NULL,
    platform_id VARCHAR(10) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    impressions INT DEFAULT 0,
    clicks INT DEFAULT 0,
    attributed_orders INT DEFAULT 0,
    attributed_units INT DEFAULT 0,
    attributed_sales DECIMAL(18,2) DEFAULT 0,
    ad_spend DECIMAL(18,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    FOREIGN KEY (sku) REFERENCES products(sku),
    UNIQUE KEY uk_advertising (ad_date, platform_id, sku),
    INDEX idx_ad_date (ad_date),
    INDEX idx_platform_id (platform_id),
    INDEX idx_sku (sku),
    INDEX idx_date_platform_sku (ad_date, platform_id, sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Daily Costs
CREATE TABLE IF NOT EXISTS daily_costs (
    cost_id INT AUTO_INCREMENT PRIMARY KEY,
    cost_date DATE NOT NULL,
    platform_id VARCHAR(10) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    product_cost DECIMAL(18,2) DEFAULT 0,
    platform_fee DECIMAL(18,2) DEFAULT 0,
    shipping_cost DECIMAL(18,2) DEFAULT 0,
    payment_fee DECIMAL(18,2) DEFAULT 0,
    other_variable_cost DECIMAL(18,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    FOREIGN KEY (sku) REFERENCES products(sku),
    UNIQUE KEY uk_daily_costs (cost_date, platform_id, sku),
    INDEX idx_cost_date (cost_date),
    INDEX idx_platform_id (platform_id),
    INDEX idx_sku (sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Returns
CREATE TABLE IF NOT EXISTS returns (
    return_id INT AUTO_INCREMENT PRIMARY KEY,
    return_date DATE NOT NULL,
    platform_id VARCHAR(10) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    reason VARCHAR(255),
    units_returned INT DEFAULT 0,
    refund_amount DECIMAL(18,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'Completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    FOREIGN KEY (sku) REFERENCES products(sku),
    INDEX idx_return_date (return_date),
    INDEX idx_platform_id (platform_id),
    INDEX idx_sku (sku),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cancellations
CREATE TABLE IF NOT EXISTS cancellations (
    cancellation_id INT AUTO_INCREMENT PRIMARY KEY,
    cancellation_date DATE NOT NULL,
    platform_id VARCHAR(10) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    reason VARCHAR(255),
    units_cancelled INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id),
    FOREIGN KEY (sku) REFERENCES products(sku),
    INDEX idx_cancellation_date (cancellation_date),
    INDEX idx_platform_id (platform_id),
    INDEX idx_sku (sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 3. INVENTORY TABLES
-- ============================================================================

-- Inventory Daily
CREATE TABLE IF NOT EXISTS inventory_daily (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    inventory_date DATE NOT NULL,
    warehouse_id VARCHAR(20) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    opening_stock INT DEFAULT 0,
    inbound_stock INT DEFAULT 0,
    demand_units INT DEFAULT 0,
    fulfilled_units INT DEFAULT 0,
    closing_stock INT DEFAULT 0,
    avg_daily_demand_7d INT DEFAULT 0,
    days_of_cover DECIMAL(10,2),
    reorder_point INT DEFAULT 0,
    recommended_reorder_qty INT DEFAULT 0,
    stockout VARCHAR(10) DEFAULT 'No',
    stock_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    FOREIGN KEY (sku) REFERENCES products(sku),
    UNIQUE KEY uk_inventory_daily (inventory_date, warehouse_id, sku),
    INDEX idx_inventory_date (inventory_date),
    INDEX idx_warehouse_id (warehouse_id),
    INDEX idx_sku (sku),
    INDEX idx_stock_status (stock_status),
    INDEX idx_date_warehouse_sku (inventory_date, warehouse_id, sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Regional Sales
CREATE TABLE IF NOT EXISTS regional_sales (
    regional_sales_id INT AUTO_INCREMENT PRIMARY KEY,
    sales_date DATE NOT NULL,
    warehouse_id VARCHAR(20) NOT NULL,
    region VARCHAR(100) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    units_sold INT DEFAULT 0,
    net_sales DECIMAL(18,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    FOREIGN KEY (sku) REFERENCES products(sku),
    INDEX idx_sales_date (sales_date),
    INDEX idx_warehouse_id (warehouse_id),
    INDEX idx_region (region),
    INDEX idx_sku (sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Replenishment Alerts
CREATE TABLE IF NOT EXISTS replenishment_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    alert_date DATE NOT NULL,
    warehouse_id VARCHAR(20) NOT NULL,
    region VARCHAR(100) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    closing_stock INT DEFAULT 0,
    avg_daily_demand_7d INT DEFAULT 0,
    days_of_cover DECIMAL(10,2),
    reorder_point INT DEFAULT 0,
    recommended_reorder_qty INT DEFAULT 0,
    stock_status VARCHAR(50),
    priority VARCHAR(50),
    recommended_action VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    FOREIGN KEY (sku) REFERENCES products(sku),
    INDEX idx_alert_date (alert_date),
    INDEX idx_warehouse_id (warehouse_id),
    INDEX idx_sku (sku),
    INDEX idx_priority (priority),
    INDEX idx_stock_status (stock_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 4. CONFIGURATION TABLES
-- ============================================================================

-- Business Configuration
CREATE TABLE IF NOT EXISTS business_config (
    config_id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value VARCHAR(255),
    unit_threshold VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Supply Chain Configuration
CREATE TABLE IF NOT EXISTS supply_chain_config (
    config_id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value VARCHAR(255),
    unit_threshold VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- 5. ANALYTICAL VIEWS
-- ============================================================================

-- View: Product-Platform-Daily (Primary analytical view)
CREATE OR REPLACE VIEW vw_product_platform_daily AS
SELECT
    ds.sale_date AS date,
    pl.platform_id,
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
        - dc.product_cost
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
                - dc.product_cost
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

-- View: Platform Performance (Aggregated)
CREATE OR REPLACE VIEW vw_platform_performance AS
SELECT
    pl.platform_id,
    pl.platform_name,
    SUM(vpd.gross_sales) AS gross_sales,
    SUM(vpd.discount) AS total_discount,
    SUM(vpd.net_sales) AS net_sales,
    SUM(vpd.units_sold) AS units_sold,
    SUM(vpd.orders) AS orders,
    SUM(vpd.ad_attributed_sales) AS ad_attributed_sales,
    SUM(vpd.ad_spend) AS total_ad_spend,
    CASE WHEN SUM(vpd.ad_spend) > 0
        THEN ROUND(SUM(vpd.ad_attributed_sales) / SUM(vpd.ad_spend), 4)
        ELSE NULL
    END AS overall_roas,
    CASE WHEN SUM(vpd.ad_attributed_sales) > 0
        THEN ROUND((SUM(vpd.ad_spend) / SUM(vpd.ad_attributed_sales)) * 100, 4)
        ELSE NULL
    END AS overall_acos_pct,
    SUM(vpd.contribution_inr) AS contribution,
    CASE WHEN SUM(vpd.net_sales) > 0
        THEN ROUND((SUM(vpd.contribution_inr) / SUM(vpd.net_sales)) * 100, 4)
        ELSE NULL
    END AS profit_margin_pct,
    SUM(vpd.units_returned) AS units_returned,
    SUM(vpd.refund_amount) AS total_refunds,
    SUM(vpd.units_cancelled) AS units_cancelled
FROM vw_product_platform_daily vpd
INNER JOIN platforms pl ON vpd.platform_id = pl.platform_id
GROUP BY pl.platform_id, pl.platform_name;

-- View: Product Performance (By SKU, Platform, and Overall)
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    vpd.sku,
    vpd.product_name,
    vpd.platform_id,
    vpd.platform,
    SUM(vpd.gross_sales) AS gross_sales,
    SUM(vpd.discount) AS total_discount,
    SUM(vpd.net_sales) AS net_sales,
    SUM(vpd.units_sold) AS units_sold,
    SUM(vpd.orders) AS orders,
    SUM(vpd.ad_attributed_sales) AS ad_attributed_sales,
    SUM(vpd.ad_spend) AS total_ad_spend,
    CASE WHEN SUM(vpd.ad_spend) > 0
        THEN ROUND(SUM(vpd.ad_attributed_sales) / SUM(vpd.ad_spend), 4)
        ELSE NULL
    END AS roas,
    CASE WHEN SUM(vpd.ad_attributed_sales) > 0
        THEN ROUND((SUM(vpd.ad_spend) / SUM(vpd.ad_attributed_sales)) * 100, 4)
        ELSE NULL
    END AS acos_pct,
    SUM(vpd.contribution_inr) AS contribution,
    CASE WHEN SUM(vpd.net_sales) > 0
        THEN ROUND((SUM(vpd.contribution_inr) / SUM(vpd.net_sales)) * 100, 4)
        ELSE NULL
    END AS profit_margin_pct,
    ROUND((SUM(vpd.ad_attributed_sales) / NULLIF(SUM(vpd.net_sales), 0)) * 100, 4) AS ad_share_pct,
    SUM(vpd.units_returned) AS units_returned,
    SUM(vpd.refund_amount) AS total_refunds,
    SUM(vpd.units_cancelled) AS units_cancelled
FROM vw_product_platform_daily vpd
GROUP BY vpd.sku, vpd.product_name, vpd.platform_id, vpd.platform;

-- View: Profitability Analysis
CREATE OR REPLACE VIEW vw_profitability AS
SELECT
    vpd.date,
    vpd.sku,
    vpd.product_name,
    vpd.platform_id,
    vpd.platform,
    vpd.net_sales,
    (
        vpd.product_cost
        + vpd.platform_fee
        + vpd.shipping_cost
        + vpd.payment_fee
        + vpd.ad_spend
        + vpd.other_variable_cost
    ) AS total_costs,
    vpd.contribution_inr,
    vpd.profit_margin_pct,
    CASE
        WHEN vpd.contribution_inr < 0 THEN 'Critical'
        WHEN vpd.profit_margin_pct < 15 THEN 'At Risk'
        ELSE 'Healthy'
    END AS profitability_status
FROM vw_product_platform_daily vpd;

-- View: Inventory Health
CREATE OR REPLACE VIEW vw_inventory_health AS
SELECT
    id.inventory_date AS date,
    id.warehouse_id,
    w.warehouse_name,
    w.region,
    w.city,
    id.sku,
    pr.product_name,
    id.closing_stock,
    id.demand_units,
    id.avg_daily_demand_7d,
    id.days_of_cover,
    id.reorder_point,
    id.recommended_reorder_qty,
    id.stock_status,
    id.stockout
FROM inventory_daily id
INNER JOIN warehouses w ON id.warehouse_id = w.warehouse_id
INNER JOIN products pr ON id.sku = pr.sku
ORDER BY id.inventory_date DESC, id.warehouse_id, id.sku;

-- View: Warehouse Summary
CREATE OR REPLACE VIEW vw_warehouse_summary AS
SELECT
    w.warehouse_id,
    w.warehouse_name,
    w.region,
    w.zone,
    w.city,
    w.latitude,
    w.longitude,
    SUM(CASE WHEN id.stock_status = 'Healthy' THEN 1 ELSE 0 END) AS healthy_skus,
    SUM(CASE WHEN id.stock_status = 'Low Stock' THEN 1 ELSE 0 END) AS low_stock_skus,
    SUM(CASE WHEN id.stock_status = 'Critical' THEN 1 ELSE 0 END) AS critical_skus,
    SUM(CASE WHEN id.stockout = 'Yes' THEN 1 ELSE 0 END) AS stockout_skus,
    SUM(id.closing_stock) AS total_stock_units,
    CASE
        WHEN SUM(CASE WHEN id.stock_status = 'Critical' THEN 1 ELSE 0 END) > 0 THEN 'Critical'
        WHEN SUM(CASE WHEN id.stock_status = 'Low Stock' THEN 1 ELSE 0 END) > 0 THEN 'At Risk'
        ELSE 'Healthy'
    END AS warehouse_health
FROM warehouses w
LEFT JOIN inventory_daily id ON w.warehouse_id = id.warehouse_id
    AND id.inventory_date = (
        SELECT MAX(inventory_date) FROM inventory_daily
        WHERE warehouse_id = w.warehouse_id
    )
GROUP BY w.warehouse_id, w.warehouse_name, w.region, w.zone, w.city, w.latitude, w.longitude;

-- View: Regional Performance
CREATE OR REPLACE VIEW vw_regional_performance AS
SELECT
    rs.sales_date AS date,
    w.region,
    rs.sku,
    pr.product_name,
    SUM(rs.units_sold) AS units_sold,
    SUM(rs.net_sales) AS net_sales,
    COUNT(DISTINCT rs.warehouse_id) AS warehouses_active
FROM regional_sales rs
INNER JOIN warehouses w ON rs.warehouse_id = w.warehouse_id
INNER JOIN products pr ON rs.sku = pr.sku
GROUP BY rs.sales_date, w.region, rs.sku, pr.product_name;

-- View: Daily KPI Summary (High-level metrics)
CREATE OR REPLACE VIEW vw_daily_kpi_summary AS
SELECT
    vpd.date,
    SUM(vpd.orders) AS total_orders,
    SUM(vpd.units_sold) AS total_units_sold,
    SUM(vpd.gross_sales) AS total_gross_sales,
    SUM(vpd.discount) AS total_discount,
    SUM(vpd.net_sales) AS total_net_sales,
    SUM(vpd.ad_attributed_sales) AS total_ad_sales,
    SUM(vpd.organic_sales) AS total_organic_sales,
    SUM(vpd.ad_spend) AS total_ad_spend,
    CASE WHEN SUM(vpd.ad_spend) > 0
        THEN ROUND(SUM(vpd.ad_attributed_sales) / SUM(vpd.ad_spend), 4)
        ELSE NULL
    END AS overall_roas,
    SUM(vpd.contribution_inr) AS total_contribution,
    CASE WHEN SUM(vpd.net_sales) > 0
        THEN ROUND((SUM(vpd.contribution_inr) / SUM(vpd.net_sales)) * 100, 4)
        ELSE NULL
    END AS overall_profit_margin_pct,
    SUM(vpd.units_returned) AS total_units_returned,
    SUM(vpd.units_cancelled) AS total_units_cancelled
FROM vw_product_platform_daily vpd
GROUP BY vpd.date;

-- ============================================================================
-- 6. INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional indexes for common query patterns
CREATE INDEX idx_daily_sales_date_range ON daily_sales(sale_date, platform_id, sku);
CREATE INDEX idx_inventory_warehouse_date ON inventory_daily(warehouse_id, inventory_date);
CREATE INDEX idx_replenishment_priority_date ON replenishment_alerts(alert_date, priority);
CREATE INDEX idx_returns_date ON returns(return_date);
CREATE INDEX idx_cancellations_date ON cancellations(cancellation_date);

-- ============================================================================
-- 7. INITIAL SEED DATA
-- ============================================================================

-- Platforms
INSERT IGNORE INTO platforms (platform_id, platform_name, sales_channel_type, default_platform_fee_pct, active) VALUES
('AMZ', 'Amazon', 'Marketplace', 16.00, TRUE),
('BLK', 'Blinkit', 'Quick Commerce', 18.00, TRUE),
('FLP', 'Flipkart', 'Marketplace', 15.00, TRUE),
('MTR', 'Myntra', 'Marketplace', 17.00, TRUE),
('JMT', 'JioMart', 'Quick Commerce', 16.00, TRUE);

-- Warehouses
INSERT IGNORE INTO warehouses (warehouse_id, warehouse_name, region, zone, city, latitude, longitude, storage_capacity_units, status) VALUES
('WH-NCR', 'Delhi NCR Warehouse', 'Delhi NCR', 'North', 'Gurugram', 28.4595, 77.0266, 5000, 'Active'),
('WH-JPR', 'Jaipur Warehouse', 'Jaipur', 'North', 'Jaipur', 26.9124, 75.7873, 3500, 'Active'),
('WH-MUM', 'Mumbai Warehouse', 'Mumbai', 'West', 'Mumbai', 19.0760, 72.8777, 4500, 'Active'),
('WH-BLR', 'Bengaluru Warehouse', 'Bengaluru', 'South', 'Bengaluru', 12.9716, 77.5946, 4500, 'Active'),
('WH-HYD', 'Hyderabad Warehouse', 'Hyderabad', 'South', 'Hyderabad', 17.3850, 78.4867, 3000, 'Active');

-- Business Configuration
INSERT IGNORE INTO business_config (config_key, config_value, unit_threshold, description) VALUES
('ReportSchedule', 'Daily', '06:00 AM IST', 'Daily product/platform performance report'),
('ReportingGrain', 'Product × Platform × Date', NULL, 'Primary analytical grain'),
('OrganicSalesRule', 'Total sales - ad-attributed sales', NULL, 'Confirm with business/platform attribution rules'),
('ProfitRule', 'Net sales - refunds - product cost - fees - logistics - ads - other variable costs', NULL, 'Illustrative prototype formula'),
('LossThreshold', 'Contribution < 0', NULL, 'Flag as critical'),
('LowMarginThreshold', 'Margin < 15%', NULL, 'Flag as at risk'),
('HealthyMarginThreshold', 'Margin >= 15%', NULL, 'Flag as healthy');

-- Supply Chain Configuration
INSERT IGNORE INTO supply_chain_config (config_key, config_value, unit_threshold, description) VALUES
('PrimaryGrain', 'Warehouse × Product × Date', NULL, 'Regional inventory tracking'),
('DemandWindow', '7', 'days', 'Trailing average demand'),
('CriticalCoverageDays', '3', 'days', 'Below this threshold = Critical'),
('LowStockCoverageDays', '7', 'days', 'Below this threshold = Low Stock'),
('StockoutRule', 'Closing stock = 0', NULL, 'Immediate alert'),
('SafetyStock', '14', 'days', 'Safety stock threshold');

-- ============================================================================
-- End of Schema Definition
-- ============================================================================
