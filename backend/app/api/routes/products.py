from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.services.product_service import ProductService
from app.schemas.product_schemas import (
    ProductPerformanceResponse,
    TopProductsResponse,
    ProductMetric,
)
from app.api.dependencies import get_date_range

# Import agent service for orchestrated analysis
try:
    from backend.services.agent_service import AgentService
    AGENT_SERVICE_AVAILABLE = True
except ImportError:
    AGENT_SERVICE_AVAILABLE = False

router = APIRouter(prefix="/product-performance", tags=["Products"])


class ProductAnalysisResponse(BaseModel):
    """Response with product analysis and agent insights."""
    products: list[dict]
    total: int
    healthy_products: int
    at_risk_products: int
    unprofitable_products: int
    findings: list[dict]
    risks: list[str]
    opportunities: list[str]


@router.get("", response_model=ProductPerformanceResponse)
async def get_products(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    platform_id: Optional[str] = Query(None),
    sku: Optional[str] = Query(None),
    include_analysis: bool = Query(False),
):
    """
    Get all products with performance metrics.

    Args:
        db: Database session
        date_range: Date range for filtering
        platform_id: Optional platform filter
        sku: Optional SKU filter
        include_analysis: Include AI agent analysis if True

    Returns:
        ProductPerformanceResponse with product metrics and optional analysis
    """
    start_date, end_date = date_range

    # Get base product metrics
    response = ProductService.get_product_performance(
        db, start_date, end_date, platform_id, sku
    )

    # Optionally enhance with agent analysis
    if include_analysis and AGENT_SERVICE_AVAILABLE:
        try:
            agent_service = AgentService(db)
            analysis = agent_service.analyze_product_performance(
                start_date, end_date, platform_id
            )
            # Attach analysis metadata to response
            response.analysis = {
                "healthy_products": analysis.get("healthy_products", 0),
                "at_risk_products": analysis.get("at_risk_products", 0),
                "unprofitable_products": analysis.get("unprofitable_products", 0),
                "risks": analysis.get("risks", []),
                "opportunities": analysis.get("opportunities", []),
            }
        except Exception as e:
            # Fallback to basic response if agent analysis fails
            pass

    return response


@router.get("/top", response_model=TopProductsResponse)
async def get_top_products(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("revenue"),
    include_analysis: bool = Query(False),
):
    """
    Get top/best performing products by specified metric.

    Supports sorting by:
    - revenue: Gross/net sales
    - contribution: Profit contribution
    - units: Units sold
    - margin: Profit margin percentage

    Args:
        db: Database session
        date_range: Date range for filtering
        limit: Maximum number of products (1-100)
        sort_by: Sort metric (revenue, contribution, units, margin)
        include_analysis: Include AI agent analysis if True

    Returns:
        TopProductsResponse with top products and optional analysis insights
    """
    start_date, end_date = date_range

    # Get top products via service
    response = ProductService.get_top_products(
        db, start_date, end_date, limit, sort_by
    )

    # Optionally enhance with agent analysis
    if include_analysis and AGENT_SERVICE_AVAILABLE:
        try:
            agent_service = AgentService(db)
            analysis = agent_service.analyze_product_performance(
                start_date, end_date
            )
            # Attach opportunities and insights
            response.analysis = {
                "opportunities": analysis.get("opportunities", []),
                "findings": analysis.get("findings", [])[:5],
            }
        except Exception as e:
            pass

    return response


@router.get("/bottom", response_model=TopProductsResponse)
async def get_bottom_products(
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    limit: int = Query(10, ge=1, le=100),
    include_analysis: bool = Query(False),
):
    """
    Get bottom/underperforming products sorted by contribution (lowest first).

    These are products with lowest profit contribution.
    Useful for identifying candidates for:
    - Price optimization
    - Marketing focus
    - Discontinuation review

    Args:
        db: Database session
        date_range: Date range for filtering
        limit: Maximum number of products (1-100)
        include_analysis: Include AI agent analysis if True

    Returns:
        TopProductsResponse with bottom products and optional risk analysis
    """
    start_date, end_date = date_range

    # Get bottom products via service
    response = ProductService.get_bottom_products(
        db, start_date, end_date, limit
    )

    # Optionally enhance with agent analysis
    if include_analysis and AGENT_SERVICE_AVAILABLE:
        try:
            agent_service = AgentService(db)
            analysis = agent_service.analyze_product_performance(
                start_date, end_date
            )
            # Attach risks and recommendations
            response.analysis = {
                "risks": analysis.get("risks", []),
                "findings": [
                    f for f in analysis.get("findings", [])
                    if f.get("severity") in ("critical", "high")
                ][:5],
            }
        except Exception as e:
            pass

    return response


@router.get("/{sku}", response_model=dict)
async def get_product_details(
    sku: str = Path(..., description="Product SKU"),
    db: Session = Depends(get_db),
    date_range: tuple[date, date] = Depends(get_date_range),
    platform_id: Optional[str] = Query(None),
):
    """
    Get detailed metrics and analysis for a specific product.

    Retrieves comprehensive product analysis including:
    - Revenue and profitability metrics
    - Sales performance across platforms
    - Advertising efficiency (ROAS, ACOS)
    - Return and cancellation rates
    - Inventory status
    - AI agent findings and recommendations

    Args:
        sku: Product SKU identifier
        db: Database session
        date_range: Date range for analysis
        platform_id: Optional specific platform filter

    Returns:
        Dict with product details, metrics, and agent insights
    """
    start_date, end_date = date_range

    # Get base product metrics
    base_response = ProductService.get_product_performance(
        db, start_date, end_date, platform_id, sku
    )

    # Find the product in results
    if not base_response.products:
        raise HTTPException(status_code=404, detail=f"Product {sku} not found")

    product = base_response.products[0]

    # Build detailed response
    details = {
        "sku": product.sku,
        "product_name": product.product_name,
        "platform": product.platform,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        "metrics": {
            "revenue": {
                "gross_sales": float(product.revenue or 0),
                "net_sales": float(product.revenue or 0),
            },
            "units": {
                "total_sold": product.units_sold,
                "returned": product.units_returned,
                "cancelled": product.units_cancelled,
            },
            "orders": {
                "total": product.orders,
                "return_rate_pct": (
                    float(product.units_returned / product.units_sold * 100)
                    if product.units_sold > 0
                    else 0
                ),
                "cancellation_rate_pct": (
                    float(product.units_cancelled / product.orders * 100)
                    if product.orders > 0
                    else 0
                ),
            },
            "profitability": {
                "contribution": float(product.contribution or 0),
                "margin_pct": float(product.profit_margin_pct) if product.profit_margin_pct else None,
            },
            "advertising": {
                "ad_spend": float(product.ad_spend or 0),
                "roas": float(product.roas) if product.roas else None,
                "acos_pct": float(product.acos_pct) if product.acos_pct else None,
                "ad_attributed_sales": (
                    float(product.revenue or 0) * float(product.acos_pct or 0) / 100
                    if product.acos_pct
                    else 0
                ),
            },
        },
    }

    # Add agent analysis if available
    if AGENT_SERVICE_AVAILABLE:
        try:
            agent_service = AgentService(db)
            analysis = agent_service.analyze_product_performance(
                start_date, end_date, platform_id
            )

            # Find relevant findings for this product
            product_findings = [
                f for f in analysis.get("findings", [])
                if f.get("sku") == sku
            ]

            if product_findings:
                details["analysis"] = {
                    "findings": product_findings,
                    "recommendations": [
                        f.get("recommendation", "")
                        for f in product_findings
                        if f.get("recommendation")
                    ],
                    "risk_level": "critical" if any(
                        f.get("severity") == "critical" for f in product_findings
                    ) else "normal",
                }
        except Exception as e:
            # Silently fail if agent analysis unavailable
            pass

    return details
