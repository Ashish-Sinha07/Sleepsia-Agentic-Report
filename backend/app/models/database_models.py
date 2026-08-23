"""
Sleepsia Agentic Business Reporting System
SQLAlchemy ORM Models

This module defines all database models for the Sleepsia reporting system,
including master data, transactional data, and inventory data.

Model structure:
- Master data: Product, Platform, Warehouse
- Transactional: DailySales, Advertising, DailyCosts, Return, Cancellation
- Inventory: InventoryDaily, RegionalSales, ReplenishmentAlert
- Configuration: BusinessConfig, SupplyChainConfig

Relationships connect transactional data to master data via foreign keys.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Integer, String, Float, Numeric, Boolean, Date, DateTime,
    ForeignKey, Index, UniqueConstraint, Text, Column
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


# ============================================================================
# 1. MASTER DATA MODELS
# ============================================================================

class Product(Base):
    """
    Products Master Data Model.

    Represents product/SKU master information including pricing, cost, and metadata.
    """
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(20), nullable=False, unique=True, index=True)
    product_name = Column(String(255), nullable=False)
    product_type = Column(String(100), nullable=True, index=True)
    material = Column(String(100), nullable=True)
    intended_use = Column(String(255), nullable=True)
    primary_market = Column(String(100), nullable=True)
    selling_price = Column(Numeric(18, 2), nullable=False)
    product_cost = Column(Numeric(18, 2), nullable=False)
    target_margin_pct = Column(Numeric(10, 4), nullable=True)
    brand = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    sub_category = Column(String(100), nullable=True)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    daily_sales = relationship("DailySales", back_populates="product", cascade="all, delete-orphan")
    advertising = relationship("Advertising", back_populates="product", cascade="all, delete-orphan")
    costs = relationship("DailyCosts", back_populates="product", cascade="all, delete-orphan")
    returns = relationship("Return", back_populates="product", cascade="all, delete-orphan")
    cancellations = relationship("Cancellation", back_populates="product", cascade="all, delete-orphan")
    inventory_daily = relationship("InventoryDaily", back_populates="product", cascade="all, delete-orphan")
    regional_sales = relationship("RegionalSales", back_populates="product", cascade="all, delete-orphan")
    replenishment_alerts = relationship("ReplenishmentAlert", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(sku='{self.sku}', name='{self.product_name}')>"


class Platform(Base):
    """
    Platforms Master Data Model.

    Represents e-commerce/quick-commerce platforms (Amazon, Flipkart, etc.)
    Platforms: Amazon, Blinkit, Flipkart, Myntra, JioMart
    """
    __tablename__ = "platforms"

    platform_id = Column(String(10), primary_key=True)
    platform_name = Column(String(100), nullable=False, unique=True)
    sales_channel_type = Column(String(50), nullable=True)
    default_platform_fee_pct = Column(Numeric(10, 4), nullable=False)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    daily_sales = relationship("DailySales", back_populates="platform", cascade="all, delete-orphan")
    advertising = relationship("Advertising", back_populates="platform", cascade="all, delete-orphan")
    costs = relationship("DailyCosts", back_populates="platform", cascade="all, delete-orphan")
    returns = relationship("Return", back_populates="platform", cascade="all, delete-orphan")
    cancellations = relationship("Cancellation", back_populates="platform", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Platform(id='{self.platform_id}', name='{self.platform_name}')>"


class Warehouse(Base):
    """
    Warehouses Master Data Model.

    Represents physical warehouses with location information and capacity.
    Includes latitude/longitude for mapping visualization.
    """
    __tablename__ = "warehouses"

    warehouse_id = Column(String(20), primary_key=True)
    warehouse_name = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False, index=True)
    zone = Column(String(50), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    storage_capacity_units = Column(Integer, nullable=True)
    status = Column(String(50), default="Active", index=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    inventory_daily = relationship("InventoryDaily", back_populates="warehouse", cascade="all, delete-orphan")
    regional_sales = relationship("RegionalSales", back_populates="warehouse", cascade="all, delete-orphan")
    replenishment_alerts = relationship("ReplenishmentAlert", back_populates="warehouse", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Warehouse(id='{self.warehouse_id}', name='{self.warehouse_name}', city='{self.city}')>"


# ============================================================================
# 2. TRANSACTIONAL DATA MODELS
# ============================================================================

class DailySales(Base):
    """
    Daily Sales Transactions Model.

    Tracks sales by date, platform, and product (SKU).
    Includes order/unit counts and sales figures with ad attribution.
    Unique constraint: (sale_date, platform_id, sku)
    """
    __tablename__ = "daily_sales"
    __table_args__ = (
        UniqueConstraint("sale_date", "platform_id", "sku", name="uk_daily_sales"),
        Index("idx_date_platform_sku", "sale_date", "platform_id", "sku"),
    )

    sales_id = Column(Integer, primary_key=True, autoincrement=True)
    sale_date = Column(Date, nullable=False, index=True)
    platform_id = Column(String(10), ForeignKey("platforms.platform_id"), nullable=False, index=True)
    sku = Column(String(20), ForeignKey("products.sku"), nullable=False, index=True)
    orders = Column(Integer, default=0)
    units_sold = Column(Integer, default=0)
    gross_sales = Column(Numeric(18, 2), default=0)
    discount = Column(Numeric(18, 2), default=0)
    net_sales = Column(Numeric(18, 2), default=0)
    ad_attributed_units = Column(Integer, default=0)
    ad_attributed_sales = Column(Numeric(18, 2), default=0)
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    platform = relationship("Platform", back_populates="daily_sales")
    product = relationship("Product", back_populates="daily_sales")

    def __repr__(self):
        return f"<DailySales(date={self.sale_date}, platform='{self.platform_id}', sku='{self.sku}')>"


class Advertising(Base):
    """
    Daily Advertising Performance Model.

    Tracks advertising metrics including spend, impressions, clicks, and attributed sales.
    Unique constraint: (ad_date, platform_id, sku)
    """
    __tablename__ = "advertising"
    __table_args__ = (
        UniqueConstraint("ad_date", "platform_id", "sku", name="uk_advertising"),
        Index("idx_date_platform_sku", "ad_date", "platform_id", "sku"),
    )

    advertising_id = Column(Integer, primary_key=True, autoincrement=True)
    ad_date = Column(Date, nullable=False, index=True)
    platform_id = Column(String(10), ForeignKey("platforms.platform_id"), nullable=False, index=True)
    sku = Column(String(20), ForeignKey("products.sku"), nullable=False, index=True)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    attributed_orders = Column(Integer, default=0)
    attributed_units = Column(Integer, default=0)
    attributed_sales = Column(Numeric(18, 2), default=0)
    ad_spend = Column(Numeric(18, 2), default=0)
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    platform = relationship("Platform", back_populates="advertising")
    product = relationship("Product", back_populates="advertising")

    def __repr__(self):
        return f"<Advertising(date={self.ad_date}, platform='{self.platform_id}', sku='{self.sku}')>"


class DailyCosts(Base):
    """
    Daily Costs Model.

    Tracks various cost components including product cost, platform fees, shipping, payments.
    Unique constraint: (cost_date, platform_id, sku)
    """
    __tablename__ = "daily_costs"
    __table_args__ = (
        UniqueConstraint("cost_date", "platform_id", "sku", name="uk_daily_costs"),
    )

    cost_id = Column(Integer, primary_key=True, autoincrement=True)
    cost_date = Column(Date, nullable=False, index=True)
    platform_id = Column(String(10), ForeignKey("platforms.platform_id"), nullable=False, index=True)
    sku = Column(String(20), ForeignKey("products.sku"), nullable=False, index=True)
    product_cost = Column(Numeric(18, 2), default=0)
    platform_fee = Column(Numeric(18, 2), default=0)
    shipping_cost = Column(Numeric(18, 2), default=0)
    payment_fee = Column(Numeric(18, 2), default=0)
    other_variable_cost = Column(Numeric(18, 2), default=0)
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    platform = relationship("Platform", back_populates="costs")
    product = relationship("Product", back_populates="costs")

    def __repr__(self):
        return f"<DailyCosts(date={self.cost_date}, platform='{self.platform_id}', sku='{self.sku}')>"


class Return(Base):
    """
    Returns/Refunds Model.

    Tracks product returns with reason, units returned, and refund amounts.
    Status values: 'Completed', 'Pending', etc.
    """
    __tablename__ = "returns"

    return_id = Column(Integer, primary_key=True, autoincrement=True)
    return_date = Column(Date, nullable=False, index=True)
    platform_id = Column(String(10), ForeignKey("platforms.platform_id"), nullable=False, index=True)
    sku = Column(String(20), ForeignKey("products.sku"), nullable=False, index=True)
    reason = Column(String(255), nullable=True)
    units_returned = Column(Integer, default=0)
    refund_amount = Column(Numeric(18, 2), default=0)
    status = Column(String(50), default="Completed", index=True)
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    platform = relationship("Platform", back_populates="returns")
    product = relationship("Product", back_populates="returns")

    def __repr__(self):
        return f"<Return(date={self.return_date}, platform='{self.platform_id}', sku='{self.sku}', units={self.units_returned})>"


class Cancellation(Base):
    """
    Order Cancellations Model.

    Tracks cancelled orders with reason and cancelled unit counts.
    """
    __tablename__ = "cancellations"

    cancellation_id = Column(Integer, primary_key=True, autoincrement=True)
    cancellation_date = Column(Date, nullable=False, index=True)
    platform_id = Column(String(10), ForeignKey("platforms.platform_id"), nullable=False, index=True)
    sku = Column(String(20), ForeignKey("products.sku"), nullable=False, index=True)
    reason = Column(String(255), nullable=True)
    units_cancelled = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    platform = relationship("Platform", back_populates="cancellations")
    product = relationship("Product", back_populates="cancellations")

    def __repr__(self):
        return f"<Cancellation(date={self.cancellation_date}, platform='{self.platform_id}', sku='{self.sku}', units={self.units_cancelled})>"


# ============================================================================
# 3. INVENTORY DATA MODELS
# ============================================================================

class InventoryDaily(Base):
    """
    Daily Inventory Snapshot Model.

    Tracks inventory levels at warehouse-product level with demand, stock status, and alerts.
    Unique constraint: (inventory_date, warehouse_id, sku)
    Stock status values: 'Healthy', 'Low Stock', 'Critical', 'Stockout'
    """
    __tablename__ = "inventory_daily"
    __table_args__ = (
        UniqueConstraint("inventory_date", "warehouse_id", "sku", name="uk_inventory_daily"),
        Index("idx_date_warehouse_sku", "inventory_date", "warehouse_id", "sku"),
    )

    inventory_id = Column(Integer, primary_key=True, autoincrement=True)
    inventory_date = Column(Date, nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.warehouse_id"), nullable=False, index=True)
    sku = Column(String(20), ForeignKey("products.sku"), nullable=False, index=True)
    opening_stock = Column(Integer, default=0)
    inbound_stock = Column(Integer, default=0)
    demand_units = Column(Integer, default=0)
    fulfilled_units = Column(Integer, default=0)
    closing_stock = Column(Integer, default=0)
    avg_daily_demand_7d = Column(Integer, default=0)
    days_of_cover = Column(Numeric(10, 2), nullable=True)
    reorder_point = Column(Integer, default=0)
    recommended_reorder_qty = Column(Integer, default=0)
    stockout = Column(String(10), default="No")
    stock_status = Column(String(50), nullable=True, index=True)
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    warehouse = relationship("Warehouse", back_populates="inventory_daily")
    product = relationship("Product", back_populates="inventory_daily")

    def __repr__(self):
        return f"<InventoryDaily(date={self.inventory_date}, warehouse='{self.warehouse_id}', sku='{self.sku}', stock={self.closing_stock})>"


class RegionalSales(Base):
    """
    Regional Sales Model.

    Aggregates sales by region and warehouse for regional demand analysis.
    """
    __tablename__ = "regional_sales"

    regional_sales_id = Column(Integer, primary_key=True, autoincrement=True)
    sales_date = Column(Date, nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.warehouse_id"), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    sku = Column(String(20), ForeignKey("products.sku"), nullable=False, index=True)
    units_sold = Column(Integer, default=0)
    net_sales = Column(Numeric(18, 2), default=0)
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    warehouse = relationship("Warehouse", back_populates="regional_sales")
    product = relationship("Product", back_populates="regional_sales")

    def __repr__(self):
        return f"<RegionalSales(date={self.sales_date}, region='{self.region}', sku='{self.sku}')>"


class ReplenishmentAlert(Base):
    """
    Replenishment Alerts Model.

    Tracks inventory replenishment alerts with stock status and recommended actions.
    Priority values: 'Critical', 'High', 'Medium', 'Low'
    Stock status values: 'Critical', 'Low Stock', 'Healthy'
    """
    __tablename__ = "replenishment_alerts"

    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    alert_date = Column(Date, nullable=False, index=True)
    warehouse_id = Column(String(20), ForeignKey("warehouses.warehouse_id"), nullable=False, index=True)
    region = Column(String(100), nullable=False)
    sku = Column(String(20), ForeignKey("products.sku"), nullable=False, index=True)
    closing_stock = Column(Integer, default=0)
    avg_daily_demand_7d = Column(Integer, default=0)
    days_of_cover = Column(Numeric(10, 2), nullable=True)
    reorder_point = Column(Integer, default=0)
    recommended_reorder_qty = Column(Integer, default=0)
    stock_status = Column(String(50), nullable=True, index=True)
    priority = Column(String(50), nullable=True, index=True)
    recommended_action = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())

    # Relationships
    warehouse = relationship("Warehouse", back_populates="replenishment_alerts")
    product = relationship("Product", back_populates="replenishment_alerts")

    def __repr__(self):
        return f"<ReplenishmentAlert(date={self.alert_date}, warehouse='{self.warehouse_id}', sku='{self.sku}', priority='{self.priority}')>"


# ============================================================================
# 4. CONFIGURATION MODELS
# ============================================================================

class BusinessConfig(Base):
    """
    Business Configuration Model.

    Stores key-value business configuration and thresholds.
    Examples:
    - ReportSchedule: 'Daily'
    - LossThreshold: 'Contribution < 0'
    - LowMarginThreshold: 'Margin < 15%'
    """
    __tablename__ = "business_config"

    config_id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), nullable=False, unique=True)
    config_value = Column(String(255), nullable=True)
    unit_threshold = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    def __repr__(self):
        return f"<BusinessConfig(key='{self.config_key}', value='{self.config_value}')>"


class SupplyChainConfig(Base):
    """
    Supply Chain Configuration Model.

    Stores supply chain related configuration and thresholds.
    Examples:
    - DemandWindow: '7' (days)
    - CriticalCoverageDays: '3' (days)
    - LowStockCoverageDays: '7' (days)
    - SafetyStock: '14' (days)
    """
    __tablename__ = "supply_chain_config"

    config_id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), nullable=False, unique=True)
    config_value = Column(String(255), nullable=True)
    unit_threshold = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    def __repr__(self):
        return f"<SupplyChainConfig(key='{self.config_key}', value='{self.config_value}')>"
