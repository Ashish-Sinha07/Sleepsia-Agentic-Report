
---

# 3. `.claude/database.md`

```markdown
# Sleepsia MySQL Database Specification

## 1. Database

Database:

MySQL 8+

Use:

- SQLAlchemy
- PyMySQL or mysql-connector-python

Connection configuration must use environment variables.

Required environment variables:

DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD

Never hardcode credentials.

---

# 2. Core Tables

## products

Purpose:

Store product master information.

Suggested fields:

product_id
sku
product_name
product_type
material
intended_use
primary_market
selling_price
product_cost
target_margin_pct
brand
category
sub_category
active
created_at
updated_at

---

## platforms

Fields:

platform_id
platform_name
sales_channel_type
default_platform_fee_pct
active
created_at
updated_at

Supported platforms:

Amazon
Blinkit
Flipkart
Myntra
JioMart

---

## daily_sales

Fields:

sales_id
date
platform_id
sku
orders
units_sold
gross_sales
discount
net_sales
ad_attributed_units
ad_attributed_sales
warehouse_id
region
created_at

Indexes:

date
platform_id
sku
warehouse_id

---

## advertising

Fields:

advertising_id
date
platform_id
sku
impressions
clicks
attributed_orders
attributed_units
attributed_sales
ad_spend
created_at

Indexes:

date
platform_id
sku

Derived metrics should normally NOT be stored:

CTR
ROAS
ACOS

Calculate them.

---

## returns

Fields:

return_id
return_date
platform_id
sku
reason
units_returned
refund_amount
status
created_at

---

## cancellations

Fields:

cancellation_id
cancellation_date
platform_id
sku
reason
units_cancelled
created_at

---

## daily_costs

Fields:

cost_id
date
platform_id
sku
product_cost
platform_fee
shipping_cost
payment_fee
other_variable_cost
created_at

---

## warehouses

Fields:

warehouse_id
warehouse_name
region
zone
city
latitude
longitude
storage_capacity
status
created_at
updated_at

Latitude and longitude are required for the India warehouse map.

---

## inventory_daily

Fields:

inventory_id
date
warehouse_id
sku
opening_stock
inbound_stock
demand
fulfilled_units
closing_stock
avg_daily_demand_7d
days_of_cover
reorder_point
recommended_reorder_qty
stockout
stock_status
created_at

---

## regional_sales

Fields:

date
region
platform_id
sku
orders
units_sold
sales
created_at

---

# 3. Analytical Views

## vw_product_platform_daily

Primary analytical view.

Include:

Date
Platform
SKU
Product
Orders
Units
Revenue
Discount
Net Sales
Ad Spend
Ad Sales
Product Cost
Platform Fees
Shipping
Payment Fees
Returns
Refunds
Cancellations
Contribution
Profit Margin
ROAS
ACOS
Organic Sales
Return Rate
Cancellation Rate

---

## vw_platform_performance

Aggregate by platform.

Include:

Revenue
Units
Orders
Ad Spend
Ad Sales
ROAS
ACOS
Contribution
Profit Margin
Returns
Cancellations

---

## vw_product_performance

Aggregate by:

SKU
Product
Platform

Include:

Revenue
Units
Orders
Ad Spend
Ad Sales
ROAS
ACOS
Contribution
Profit Margin
Returns
Cancellations
Organic Share

---

## vw_profitability

Include:

SKU
Product
Platform
Revenue
Total Costs
Contribution
Profit Margin
Profitability Status

---

## vw_inventory_health

Include:

Warehouse
City
SKU
Stock
Demand
Days of Cover
Reorder Point
Recommended Reorder Quantity
Stock Status

---

# 4. Derived Metrics

## Net Revenue

Gross Sales - Discount

---

## Organic Sales

Net Sales - Ad Attributed Sales

---

## ROAS

Ad Attributed Sales / Ad Spend

If Ad Spend = 0:

ROAS = NULL

---

## ACOS

Ad Spend / Ad Attributed Sales * 100

If Ad Sales = 0:

ACOS = NULL

---

## Contribution

Net Sales
- Refunds
- Product Cost
- Platform Fees
- Shipping Cost
- Payment Fees
- Advertising Cost
- Other Variable Costs

---

## Profit Margin

Contribution / Net Sales * 100

If Net Sales = 0:

Profit Margin = NULL

---

## Return Rate

Returned Units / Sold Units * 100

---

## Cancellation Rate

Cancelled Units / Orders * 100

---

## Days of Cover

Available Stock / Average Daily Demand

---

# 5. Database Design Rules

1. Use primary keys.
2. Use foreign keys where appropriate.
3. Use indexes on common filter fields.
4. Avoid unnecessary duplication.
5. Do not store derived metrics unnecessarily.
6. Use DECIMAL for financial values.
7. Use DATE/DATETIME for dates.
8. Use INT/BIGINT for quantities.
9. Use BOOLEAN for flags.
10. Keep original source data unchanged.
11. Maintain created_at and updated_at where appropriate.
12. Use transactions during bulk loading.

---

# 6. Financial Precision

Use:

DECIMAL(18,2)

for monetary values.

Percentage values:

DECIMAL(10,4)

Do not use floating-point types for financial storage.