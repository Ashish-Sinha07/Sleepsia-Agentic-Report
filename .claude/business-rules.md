# Sleepsia Business Rules

## Revenue

Net Revenue:

Gross Sales - Discount

---

## Organic Sales

Organic Sales:

Net Sales - Ad Attributed Sales

---

## Inorganic / Ad-Attributed Sales

Inorganic Sales:

Ad Attributed Sales

---

## Organic Share

Organic Share:

Organic Sales / Net Sales * 100

---

## ROAS

ROAS:

Ad Attributed Sales / Ad Spend

If Ad Spend is zero:

Return NULL.

Never return infinity.

---

## ACOS

ACOS:

Ad Spend / Ad Attributed Sales * 100

If Ad Attributed Sales is zero:

Return NULL.

---

## Contribution

Contribution:

Net Sales
- Refund Amount
- Product Cost
- Platform Fee
- Shipping Cost
- Payment Fee
- Advertising Spend
- Other Variable Costs

---

## Profit Margin

Profit Margin:

Contribution / Net Sales * 100

If Net Sales is zero:

Return NULL.

---

## Return Rate

Return Rate:

Returned Units / Sold Units * 100

---

## Cancellation Rate

Cancellation Rate:

Cancelled Units / Orders * 100

---

# Inventory Rules

## Days of Cover

Days of Cover:

Available Stock / Average Daily Demand

---

## Stockout

Closing Stock <= 0

Status:

STOCKOUT

Stockout takes priority over all other statuses.

---

## Critical Stock

Days of Cover < 3

Status:

CRITICAL

---

## Low Stock

Days of Cover >= 3
AND
Days of Cover < 7

Status:

LOW

---

## Healthy Stock

Days of Cover >= 7

Status:

HEALTHY

---

# Profitability Rules

## Negative Profit

Contribution < 0

Status:

LOSS

---

## Low Margin

Profit Margin >= 0
AND
Profit Margin < Target Margin

Status:

LOW_MARGIN

---

## Healthy Profitability

Profit Margin >= Target Margin

Status:

HEALTHY

---

# Advertising Rules

Default MVP thresholds:

ROAS < 2.5

Status:

INEFFICIENT

ROAS >= 2.5 AND ROAS < 4

Status:

REVIEW

ROAS >= 4

Status:

EFFICIENT

These thresholds should eventually be configurable.

---

# Alert Severity

CRITICAL:

- Stockout
- Negative contribution
- Severe data failure
- Critical warehouse issue

HIGH:

- Days of cover < 3
- Very poor ROAS
- Severe return rate
- Significant profitability decline

MEDIUM:

- Low stock
- Low margin
- ROAS requiring review

LOW:

- Minor performance change
- Positive opportunity

---

# AI Rules

The AI must:

1. Use database-backed results.
2. Never invent numbers.
3. Explain the source metric.
4. Distinguish facts from recommendations.
5. State assumptions.
6. State when data is unavailable.
7. Avoid presenting guesses as facts.

---

# Recommendation Format

Every recommendation should contain:

Finding
Evidence
Business Impact
Recommended Action

Example:

Finding:

ROAS for Product X on Amazon declined.

Evidence:

ROAS decreased from 4.2 to 2.7.

Impact:

Advertising efficiency has deteriorated.

Action:

Review campaign targeting and spend allocation.

Do not claim causality unless supporting data exists.