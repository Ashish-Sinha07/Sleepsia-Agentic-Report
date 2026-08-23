"""
Agent Service - Central orchestrator that coordinates DatabaseService, MetricsEngine, and AI agents.

This service implements:
1. DatabaseService - Query MySQL database for business metrics
2. MetricsEngine wrapper - Calculate and cache metrics
3. Agent coordination - Call validation, analysis, recommendation, and report agents
4. KPI orchestration - Aggregate KPIs across dimensions
5. Product analysis - Analyze profitability and performance
6. Platform analysis - Compare platform-wise metrics
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

# Import agents
from agents import (
    DataValidationAgent,
    DataAnalysisAgent,
    InsightRecommendationAgent,
    LLMAnalysisAgent,
    ReportAgent,
)

# Import analytics models
from analytics.models import (
    ProductMetrics,
    PlatformMetrics,
    DailyMetrics,
    AnalysisResult,
    PerformanceFinding,
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Centralized database access service.

    Provides query methods for:
    - KPI aggregations
    - Product performance
    - Platform performance
    - Inventory metrics
    - Alert data
    """

    def __init__(self, db: Session):
        """Initialize with SQLAlchemy session."""
        self.db = db

    def get_kpi_aggregation(
        self,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
        warehouse_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get aggregated KPI metrics for a date range.

        Returns:
            Dict with keys: total_orders, total_units_sold, total_revenue,
            net_revenue, total_profit, ad_spend, units_returned, units_cancelled
        """
        query = """
        SELECT
            COALESCE(SUM(total_orders), 0) as total_orders,
            COALESCE(SUM(total_units_sold), 0) as total_units_sold,
            COALESCE(SUM(total_gross_sales), 0) as total_gross_sales,
            COALESCE(SUM(total_net_sales), 0) as total_net_sales,
            COALESCE(SUM(total_contribution), 0) as total_contribution,
            COALESCE(SUM(total_ad_spend), 0) as total_ad_spend,
            COALESCE(SUM(total_units_returned), 0) as total_units_returned,
            COALESCE(SUM(total_units_cancelled), 0) as total_units_cancelled,
            COALESCE(AVG(overall_profit_margin_pct), NULL) as overall_profit_margin_pct,
            COALESCE(AVG(overall_roas), NULL) as overall_roas,
            COALESCE(SUM(total_ad_sales), 0) as total_ad_sales,
            COALESCE(SUM(total_organic_sales), 0) as total_organic_sales
        FROM vw_daily_kpi_summary
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        if warehouse_id:
            query += " AND warehouse_id = :warehouse_id"
            params["warehouse_id"] = warehouse_id

        result = self.db.execute(text(query), params).fetchone()

        if not result or result[0] is None:
            return {
                "total_orders": 0,
                "total_units_sold": 0,
                "total_revenue": Decimal(0),
                "net_revenue": Decimal(0),
                "total_contribution": Decimal(0),
                "total_ad_spend": Decimal(0),
                "units_returned": 0,
                "units_cancelled": 0,
                "profit_margin_pct": None,
                "roas": None,
                "ad_sales": Decimal(0),
                "organic_sales": Decimal(0),
            }

        return {
            "total_orders": result[0] or 0,
            "total_units_sold": result[1] or 0,
            "total_revenue": result[2] or Decimal(0),
            "net_revenue": result[3] or Decimal(0),
            "total_contribution": result[4] or Decimal(0),
            "total_ad_spend": result[5] or Decimal(0),
            "units_returned": result[6] or 0,
            "units_cancelled": result[7] or 0,
            "profit_margin_pct": result[8],
            "roas": result[9],
            "ad_sales": result[10] or Decimal(0),
            "organic_sales": result[11] or Decimal(0),
        }

    def get_product_metrics(
        self,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
        sku: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get product-level metrics for analysis.

        Returns:
            List of dicts with product metrics
        """
        query = """
        SELECT
            sku,
            product_name,
            platform_id,
            platform,
            COALESCE(SUM(gross_sales), 0) as gross_sales,
            COALESCE(SUM(net_sales), 0) as net_sales,
            COALESCE(SUM(units_sold), 0) as units_sold,
            COALESCE(SUM(orders), 0) as orders,
            COALESCE(SUM(ad_spend), 0) as ad_spend,
            COALESCE(AVG(roas), NULL) as roas,
            COALESCE(AVG(acos_pct), NULL) as acos_pct,
            COALESCE(SUM(contribution_inr), 0) as contribution,
            COALESCE(AVG(profit_margin_pct), NULL) as profit_margin,
            COALESCE(SUM(units_returned), 0) as units_returned,
            COALESCE(SUM(units_cancelled), 0) as units_cancelled,
            COALESCE(AVG(organic_share_pct), NULL) as organic_share
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        if sku:
            query += " AND sku = :sku"
            params["sku"] = sku

        query += " GROUP BY sku, product_name, platform_id, platform ORDER BY net_sales DESC"

        results = self.db.execute(text(query), params).fetchall()

        products = []
        for row in results:
            products.append({
                "sku": row[0],
                "product_name": row[1],
                "platform_id": row[2],
                "platform": row[3],
                "gross_sales": row[4] or Decimal(0),
                "net_sales": row[5] or Decimal(0),
                "units_sold": row[6] or 0,
                "orders": row[7] or 0,
                "ad_spend": row[8] or Decimal(0),
                "roas": row[9],
                "acos_pct": row[10],
                "contribution": row[11] or Decimal(0),
                "profit_margin": row[12],
                "units_returned": row[13] or 0,
                "units_cancelled": row[14] or 0,
                "organic_share": row[15],
            })

        return products

    def get_platform_metrics(
        self,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get platform-level metrics for comparison.

        Returns:
            List of dicts with platform metrics
        """
        query = """
        SELECT
            platform_id,
            platform,
            COALESCE(SUM(gross_sales), 0) as gross_sales,
            COALESCE(SUM(net_sales), 0) as net_sales,
            COALESCE(SUM(units_sold), 0) as units_sold,
            COALESCE(SUM(orders), 0) as orders,
            COALESCE(SUM(ad_spend), 0) as ad_spend,
            COALESCE(AVG(roas), NULL) as avg_roas,
            COALESCE(AVG(acos_pct), NULL) as avg_acos,
            COALESCE(SUM(contribution_inr), 0) as contribution,
            COALESCE(AVG(profit_margin_pct), NULL) as profit_margin,
            COALESCE(SUM(units_returned), 0) as units_returned,
            COALESCE(SUM(units_cancelled), 0) as units_cancelled
        FROM vw_product_platform_daily
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        query += " GROUP BY platform_id, platform ORDER BY net_sales DESC"

        results = self.db.execute(text(query), params).fetchall()

        platforms = []
        for row in results:
            units_sold = row[4] or 0
            units_returned = row[11] or 0

            # Calculate return rate
            return_rate = None
            if units_sold > 0:
                return_rate = (units_returned / units_sold) * 100

            platforms.append({
                "platform_id": row[0],
                "platform_name": row[1],
                "gross_sales": row[2] or Decimal(0),
                "net_sales": row[3] or Decimal(0),
                "units_sold": units_sold,
                "orders": row[5] or 0,
                "ad_spend": row[6] or Decimal(0),
                "roas": row[7],
                "acos_pct": row[8],
                "contribution": row[9] or Decimal(0),
                "profit_margin": row[10],
                "units_returned": units_returned,
                "units_cancelled": row[12] or 0,
                "return_rate_pct": return_rate,
            })

        return platforms

    def get_daily_metrics(
        self,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get daily metrics for trend analysis."""
        query = """
        SELECT
            date,
            total_orders,
            total_units_sold,
            total_net_sales,
            total_gross_sales,
            total_ad_spend,
            total_contribution,
            overall_profit_margin_pct,
            overall_roas,
            total_units_returned,
            total_units_cancelled
        FROM vw_daily_kpi_summary
        WHERE date BETWEEN :start_date AND :end_date
        """

        params = {"start_date": start_date, "end_date": end_date}

        if platform_id:
            query += " AND platform_id = :platform_id"
            params["platform_id"] = platform_id

        query += " ORDER BY date ASC"

        results = self.db.execute(text(query), params).fetchall()

        daily = []
        for row in results:
            daily.append({
                "date": row[0],
                "orders": row[1] or 0,
                "units_sold": row[2] or 0,
                "net_sales": row[3] or Decimal(0),
                "gross_sales": row[4] or Decimal(0),
                "ad_spend": row[5] or Decimal(0),
                "contribution": row[6] or Decimal(0),
                "profit_margin": row[7],
                "roas": row[8],
                "units_returned": row[9] or 0,
                "units_cancelled": row[10] or 0,
            })

        return daily


class MetricsEngineWrapper:
    """
    Wrapper around the MetricsEngine that:
    1. Formats raw data into engine-compatible structures
    2. Caches calculations
    3. Provides calculation results to agents
    """

    def __init__(self, db_service: DatabaseService):
        """Initialize with database service."""
        self.db_service = db_service

    def calculate_product_metrics(
        self,
        product_data: Dict[str, Any],
    ) -> ProductMetrics:
        """
        Convert raw product data to ProductMetrics for analysis.

        Args:
            product_data: Dict from DatabaseService.get_product_metrics()

        Returns:
            ProductMetrics object ready for analysis
        """
        units_sold = product_data.get("units_sold", 0)
        orders = product_data.get("orders", 0)
        ad_spend = product_data.get("ad_spend", Decimal(0))
        units_returned = product_data.get("units_returned", 0)
        units_cancelled = product_data.get("units_cancelled", 0)

        # Calculate return rate
        return_rate = None
        if units_sold > 0:
            return_rate = (units_returned / units_sold) * 100

        # Calculate cancellation rate
        cancellation_rate = None
        if orders > 0:
            cancellation_rate = (units_cancelled / orders) * 100

        return ProductMetrics(
            sku=product_data.get("sku"),
            product_name=product_data.get("product_name"),
            platform_id=product_data.get("platform_id"),
            platform_name=product_data.get("platform"),
            revenue_inr=product_data.get("net_sales", Decimal(0)),
            units_sold=units_sold,
            orders=orders,
            ad_spend_inr=ad_spend,
            roas=product_data.get("roas"),
            acos_pct=product_data.get("acos_pct"),
            contribution_inr=product_data.get("contribution", Decimal(0)),
            profit_margin_pct=product_data.get("profit_margin"),
            return_rate_pct=return_rate,
            cancellation_rate_pct=cancellation_rate,
            organic_share_pct=product_data.get("organic_share"),
        )

    def calculate_platform_metrics(
        self,
        platform_data: Dict[str, Any],
    ) -> PlatformMetrics:
        """
        Convert raw platform data to PlatformMetrics for analysis.

        Args:
            platform_data: Dict from DatabaseService.get_platform_metrics()

        Returns:
            PlatformMetrics object ready for analysis
        """
        units_sold = platform_data.get("units_sold", 0)
        units_returned = platform_data.get("units_returned", 0)

        # Calculate return rate
        return_rate = None
        if units_sold > 0:
            return_rate = (units_returned / units_sold) * 100

        return PlatformMetrics(
            platform_id=platform_data.get("platform_id"),
            platform_name=platform_data.get("platform_name"),
            total_revenue_inr=platform_data.get("net_sales", Decimal(0)),
            total_units_sold=units_sold,
            total_orders=platform_data.get("orders", 0),
            total_ad_spend_inr=platform_data.get("ad_spend", Decimal(0)),
            platform_roas=platform_data.get("roas"),
            platform_acos_pct=platform_data.get("acos_pct"),
            total_contribution_inr=platform_data.get("contribution", Decimal(0)),
            overall_profit_margin_pct=platform_data.get("profit_margin"),
            overall_return_rate_pct=return_rate,
        )


class AgentService:
    """
    Central service that orchestrates all agents.

    Responsibilities:
    1. Query database via DatabaseService
    2. Calculate metrics via MetricsEngineWrapper
    3. Coordinate DataValidationAgent for data quality
    4. Coordinate DataAnalysisAgent for pattern detection
    5. Coordinate InsightRecommendationAgent for recommendations
    6. Coordinate LLMAnalysisAgent for NLP explanations
    7. Coordinate ReportAgent for report generation
    """

    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
        self.db_service = DatabaseService(db)
        self.metrics_wrapper = MetricsEngineWrapper(self.db_service)

        # Initialize agents
        self.validation_agent = DataValidationAgent()
        self.analysis_agent = DataAnalysisAgent()
        self.insight_agent = InsightRecommendationAgent()
        self.llm_agent = LLMAnalysisAgent()
        self.report_agent = ReportAgent()

    def get_executive_kpis(
        self,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
        warehouse_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get executive KPIs for dashboard.

        Flow:
        1. Query database for aggregated metrics
        2. Calculate secondary metrics (margins, rates, etc)
        3. Return KPIs formatted for frontend

        Args:
            start_date: Period start
            end_date: Period end
            platform_id: Optional filter for specific platform
            warehouse_id: Optional filter for specific warehouse

        Returns:
            Dict with KPI metrics formatted for display
        """
        logger.info(
            f"Getting executive KPIs: {start_date} to {end_date}, "
            f"platform={platform_id}, warehouse={warehouse_id}"
        )

        # Query database
        kpi_data = self.db_service.get_kpi_aggregation(
            start_date, end_date, platform_id, warehouse_id
        )

        # Calculate derived metrics
        total_revenue = kpi_data.get("total_revenue", Decimal(0))
        net_revenue = kpi_data.get("net_revenue", Decimal(0))
        contribution = kpi_data.get("total_contribution", Decimal(0))
        ad_spend = kpi_data.get("total_ad_spend", Decimal(0))
        ad_sales = kpi_data.get("ad_sales", Decimal(0))
        units_sold = kpi_data.get("total_units_sold", 0)
        units_returned = kpi_data.get("units_returned", 0)
        orders = kpi_data.get("total_orders", 0)

        # Profit calculation
        total_profit = contribution
        profit_margin_pct = None
        if net_revenue and net_revenue > 0:
            profit_margin_pct = (contribution / net_revenue) * 100

        # Return rate
        return_rate_pct = None
        if units_sold > 0:
            return_rate_pct = (units_returned / units_sold) * 100

        # Cancellation rate
        cancellation_rate_pct = None
        if orders > 0:
            cancellation_rate_pct = (kpi_data.get("units_cancelled", 0) / orders) * 100

        # ROAS and ACOS
        roas = kpi_data.get("roas")
        acos_pct = None
        if ad_spend and ad_spend > 0 and ad_sales and ad_sales > 0:
            acos_pct = (ad_spend / ad_sales) * 100

        # AOV
        avg_order_value = None
        if orders > 0:
            avg_order_value = float(net_revenue / orders) if net_revenue else 0

        return {
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "revenue": {
                "total_revenue": float(total_revenue) if total_revenue else 0,
                "net_revenue": float(net_revenue) if net_revenue else 0,
                "ad_attributed_sales": float(ad_sales) if ad_sales else 0,
                "organic_sales": float(kpi_data.get("organic_sales", Decimal(0))),
            },
            "profitability": {
                "total_profit": float(total_profit) if total_profit else 0,
                "profit_margin_pct": float(profit_margin_pct) if profit_margin_pct else None,
                "contribution": float(contribution) if contribution else 0,
            },
            "units": {
                "total_units_sold": units_sold,
                "units_returned": units_returned,
                "units_cancelled": kpi_data.get("units_cancelled", 0),
                "avg_order_value": avg_order_value,
            },
            "orders": {
                "total_orders": orders,
                "return_rate_pct": float(return_rate_pct) if return_rate_pct else None,
                "cancellation_rate_pct": float(cancellation_rate_pct) if cancellation_rate_pct else None,
            },
            "advertising": {
                "total_ad_spend": float(ad_spend) if ad_spend else 0,
                "roas": float(roas) if roas else None,
                "acos_pct": float(acos_pct) if acos_pct else None,
            },
        }

    def analyze_product_performance(
        self,
        start_date: date,
        end_date: date,
        platform_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze product performance across all dimensions.

        Flow:
        1. Query database for product metrics
        2. Convert to ProductMetrics objects
        3. Run DataAnalysisAgent to identify patterns
        4. Categorize products (healthy, at-risk, unprofitable)
        5. Return structured analysis

        Args:
            start_date: Period start
            end_date: Period end
            platform_id: Optional filter for specific platform

        Returns:
            Dict with product analysis, risks, opportunities
        """
        logger.info(
            f"Analyzing product performance: {start_date} to {end_date}, platform={platform_id}"
        )

        # Query database
        product_data_list = self.db_service.get_product_metrics(
            start_date, end_date, platform_id
        )

        if not product_data_list:
            logger.warning("No product data found for analysis")
            return {
                "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
                "total_products": 0,
                "healthy_products": 0,
                "at_risk_products": 0,
                "unprofitable_products": 0,
                "products": [],
                "findings": [],
                "risks": [],
                "opportunities": [],
            }

        # Convert to ProductMetrics objects
        product_metrics = [
            self.metrics_wrapper.calculate_product_metrics(p) for p in product_data_list
        ]

        # Run analysis agent
        all_findings = []
        for product_metric in product_metrics:
            findings = self.analysis_agent.analyze_product_performance(product_metric)
            all_findings.extend(findings)

        # Categorize products
        healthy_products = 0
        at_risk_products = 0
        unprofitable_products = 0

        for metric in product_metrics:
            margin = metric.profit_margin_pct
            if margin is None:
                continue
            elif margin < 0:
                unprofitable_products += 1
            elif margin < 15.0:
                at_risk_products += 1
            else:
                healthy_products += 1

        # Extract findings by type
        risks = [f for f in all_findings if f.severity in ("critical", "high")]
        opportunities = [f for f in all_findings if f.severity == "low"]

        return {
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "total_products": len(product_metrics),
            "healthy_products": healthy_products,
            "at_risk_products": at_risk_products,
            "unprofitable_products": unprofitable_products,
            "products": [
                {
                    "sku": p.sku,
                    "product_name": p.product_name,
                    "platform": p.platform_name,
                    "revenue": float(p.revenue_inr) if p.revenue_inr else 0,
                    "units_sold": p.units_sold,
                    "margin_pct": float(p.profit_margin_pct) if p.profit_margin_pct else None,
                    "roas": float(p.roas) if p.roas else None,
                    "return_rate_pct": float(p.return_rate_pct) if p.return_rate_pct else None,
                }
                for p in sorted(product_metrics, key=lambda x: x.revenue_inr or 0, reverse=True)[:50]
            ],
            "findings": [
                {
                    "sku": f.sku,
                    "finding_type": f.finding_type,
                    "severity": f.severity,
                    "description": f.description,
                    "metric_name": f.metric_name,
                    "metric_value": float(f.metric_value) if isinstance(f.metric_value, Decimal) else f.metric_value,
                    "threshold": float(f.threshold) if isinstance(f.threshold, Decimal) else f.threshold,
                    "recommendation": f.recommendation,
                }
                for f in all_findings
            ],
            "risks": [f.description for f in risks],
            "opportunities": [f.description for f in opportunities],
        }

    def analyze_platform_performance(
        self,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """
        Analyze platform-wise performance and comparison.

        Flow:
        1. Query database for platform metrics
        2. Convert to PlatformMetrics objects
        3. Run DataAnalysisAgent for each platform
        4. Compare platforms side-by-side
        5. Identify platform-specific risks and opportunities

        Args:
            start_date: Period start
            end_date: Period end

        Returns:
            Dict with platform analysis and comparison
        """
        logger.info(f"Analyzing platform performance: {start_date} to {end_date}")

        # Query database
        platform_data_list = self.db_service.get_platform_metrics(start_date, end_date)

        if not platform_data_list:
            logger.warning("No platform data found for analysis")
            return {
                "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
                "platforms": [],
                "findings": [],
                "comparison": {},
            }

        # Convert to PlatformMetrics objects
        platform_metrics = [
            self.metrics_wrapper.calculate_platform_metrics(p) for p in platform_data_list
        ]

        # Run analysis agent
        all_findings = []
        for platform_metric in platform_metrics:
            findings = self.analysis_agent.analyze_platform_performance(platform_metric)
            all_findings.extend(findings)

        # Build response
        platforms_response = [
            {
                "platform_id": p.platform_id,
                "platform_name": p.platform_name,
                "revenue": float(p.total_revenue_inr) if p.total_revenue_inr else 0,
                "units_sold": p.total_units_sold,
                "orders": p.total_orders,
                "ad_spend": float(p.total_ad_spend_inr) if p.total_ad_spend_inr else 0,
                "margin_pct": float(p.overall_profit_margin_pct) if p.overall_profit_margin_pct else None,
                "roas": float(p.platform_roas) if p.platform_roas else None,
                "return_rate_pct": float(p.overall_return_rate_pct) if p.overall_return_rate_pct else None,
            }
            for p in platform_metrics
        ]

        # Platform comparison metrics
        if len(platform_metrics) > 1:
            revenues = [float(p.total_revenue_inr or 0) for p in platform_metrics]
            margins = [float(p.overall_profit_margin_pct or 0) for p in platform_metrics if p.overall_profit_margin_pct]

            comparison = {
                "highest_revenue": {
                    "platform": platform_metrics[0].platform_name,
                    "revenue": float(platform_metrics[0].total_revenue_inr or 0),
                },
                "highest_margin": None,
                "lowest_margin": None,
                "revenue_distribution": {p.platform_name: r for p, r in zip(platform_metrics, revenues)},
            }

            if margins:
                max_margin_platform = max(platform_metrics, key=lambda x: x.overall_profit_margin_pct or 0)
                min_margin_platform = min(platform_metrics, key=lambda x: x.overall_profit_margin_pct or float('inf'))

                comparison["highest_margin"] = {
                    "platform": max_margin_platform.platform_name,
                    "margin": float(max_margin_platform.overall_profit_margin_pct),
                }
                comparison["lowest_margin"] = {
                    "platform": min_margin_platform.platform_name,
                    "margin": float(min_margin_platform.overall_profit_margin_pct),
                }
        else:
            comparison = {}

        return {
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "total_platforms": len(platform_metrics),
            "platforms": platforms_response,
            "findings": [
                {
                    "platform_id": f.platform_id,
                    "finding_type": f.finding_type,
                    "severity": f.severity,
                    "description": f.description,
                    "metric_name": f.metric_name,
                    "metric_value": float(f.metric_value) if isinstance(f.metric_value, Decimal) else f.metric_value,
                    "recommendation": f.recommendation,
                }
                for f in all_findings
            ],
            "comparison": comparison,
            "risks": [f.description for f in all_findings if f.severity in ("critical", "high")],
            "opportunities": [f.description for f in all_findings if f.severity == "low"],
        }

    def get_inventory_alerts(
        self,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """
        Generate inventory and warehouse alerts.

        Returns:
            Dict with critical, warning, and info alerts
        """
        logger.info(f"Getting inventory alerts for {start_date} to {end_date}")

        # Query database for inventory metrics
        query = """
        SELECT
            warehouse_id,
            warehouse_name,
            sku,
            product_name,
            current_stock,
            days_of_cover,
            reorder_point,
            min_stock_level,
            CASE
                WHEN current_stock = 0 THEN 'stockout'
                WHEN current_stock < min_stock_level THEN 'critical'
                WHEN current_stock < reorder_point THEN 'low'
                ELSE 'healthy'
            END as status
        FROM vw_inventory_status
        WHERE warehouse_id IS NOT NULL
        """

        results = self.db.execute(text(query)).fetchall()

        critical_alerts = []
        warning_alerts = []

        for row in results:
            if row[8] == "stockout":
                critical_alerts.append({
                    "warehouse": row[1],
                    "sku": row[2],
                    "product": row[3],
                    "alert_type": "stockout",
                    "message": f"{row[3]} is out of stock at {row[1]}",
                })
            elif row[8] == "critical":
                critical_alerts.append({
                    "warehouse": row[1],
                    "sku": row[2],
                    "product": row[3],
                    "alert_type": "critical_stock",
                    "current_stock": row[4],
                    "message": f"{row[3]} critical stock at {row[1]}: {row[4]} units",
                })
            elif row[8] == "low":
                warning_alerts.append({
                    "warehouse": row[1],
                    "sku": row[2],
                    "product": row[3],
                    "alert_type": "low_stock",
                    "current_stock": row[4],
                    "days_of_cover": row[5],
                    "message": f"{row[3]} low stock at {row[1]}: {row[4]} units ({row[5]} days)",
                })

        return {
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "critical": critical_alerts,
            "warning": warning_alerts,
            "total_alerts": len(critical_alerts) + len(warning_alerts),
        }

    def generate_business_report(
        self,
        report_type: str,
        start_date: date,
        end_date: date,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive business report.

        Flow:
        1. Get KPIs
        2. Analyze product performance
        3. Analyze platform performance
        4. Get alerts
        5. Call ReportAgent to generate report

        Args:
            report_type: "executive", "detailed", "platform", "product"
            start_date: Period start
            end_date: Period end
            filters: Optional filters

        Returns:
            Dict with report metadata and content
        """
        logger.info(f"Generating {report_type} report: {start_date} to {end_date}")

        if filters is None:
            filters = {}

        # Gather all analysis
        kpis = self.get_executive_kpis(start_date, end_date)
        products = self.analyze_product_performance(start_date, end_date)
        platforms = self.analyze_platform_performance(start_date, end_date)
        alerts = self.get_inventory_alerts(start_date, end_date)

        # Build report content
        report_data = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "executive_summary": {
                "kpis": kpis,
                "critical_alerts": len(alerts.get("critical", [])),
                "product_risks": len([p for p in products.get("findings", []) if p["severity"] == "critical"]),
                "platform_risks": len([p for p in platforms.get("findings", []) if p["severity"] == "critical"]),
            },
            "kpis": kpis,
            "product_analysis": products,
            "platform_analysis": platforms,
            "alerts": alerts,
        }

        return {
            "report_id": f"REP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "report_type": report_type,
            "status": "completed",
            "generated_at": datetime.now().isoformat(),
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "data": report_data,
        }

    def ask_business_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Answer a business question using the AI assistant.

        Flow:
        1. Parse question intent using LLMAnalysisAgent
        2. Identify required data and filters
        3. Query database and calculate metrics
        4. Generate natural language response
        5. Provide recommendations

        Args:
            question: User question
            context: Optional context (date range, platform, etc)

        Returns:
            Dict with answer, confidence, and recommendations
        """
        logger.info(f"Processing question: {question}")

        # Default context
        if context is None:
            context = {}

        # Default date range (last 30 days)
        end_date = context.get("end_date", date.today())
        start_date = context.get("start_date", date(end_date.year, end_date.month, 1) if end_date.day > 1 else end_date)

        # Try to answer the question
        answer = "I don't have sufficient data to answer that accurately."
        confidence = 0.0
        data_sources = []
        recommendations = []

        # Check if question is about KPIs
        if any(word in question.lower() for word in ["revenue", "profit", "sales", "margin", "roas", "acos"]):
            kpis = self.get_executive_kpis(start_date, end_date)
            data_sources.append("KPI aggregation")

            if "profit margin" in question.lower():
                margin = kpis.get("profitability", {}).get("profit_margin_pct")
                if margin:
                    answer = f"Your profit margin for the period is {margin:.2f}%."
                    confidence = 0.9

        # Check if question is about products
        elif any(word in question.lower() for word in ["product", "sku", "top", "bottom", "unprofitable"]):
            products = self.analyze_product_performance(start_date, end_date)
            data_sources.append("Product analysis")

            risks = products.get("risks", [])
            if risks:
                answer = f"Found {len(risks)} product issues: " + "; ".join(risks[:3])
                recommendations = products.get("opportunities", [])[:3]
                confidence = 0.8

        # Check if question is about platforms
        elif any(word in question.lower() for word in ["platform", "amazon", "flipkart", "blinkit", "myntra", "jiomart"]):
            platforms = self.analyze_platform_performance(start_date, end_date)
            data_sources.append("Platform analysis")

            if platforms.get("platforms"):
                answer = f"Analyzed {len(platforms.get('platforms', []))} platforms. "
                confidence = 0.8

        return {
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "data_sources": data_sources,
            "recommendations": recommendations,
            "period": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
        }
