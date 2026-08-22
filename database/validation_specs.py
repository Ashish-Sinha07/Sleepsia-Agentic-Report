"""Business validation specifications for each Sleepsia data table."""

from agents.validation_agent import DatasetSpec

PRODUCT_MASTER_SPEC = DatasetSpec(
    required_columns=(
        "SKU", "ProductName", "ProductType", "Material",
        "SellingPrice_INR", "ProductCost_INR", "TargetMarginPct", "Active"
    ),
    non_nullable_columns=(
        "SKU", "ProductName", "ProductType", "Material",
        "SellingPrice_INR", "ProductCost_INR", "TargetMarginPct", "Active"
    ),
    numeric_columns=("SellingPrice_INR", "ProductCost_INR", "TargetMarginPct"),
    non_negative_columns=("SellingPrice_INR", "ProductCost_INR", "TargetMarginPct"),
    unique_columns=("SKU",),
    allowed_values={"Active": frozenset({"Yes", "No"})},
)

PLATFORM_MASTER_SPEC = DatasetSpec(
    required_columns=("PlatformID", "Platform", "SalesChannelType", "DefaultPlatformFeePct", "Active"),
    non_nullable_columns=("PlatformID", "Platform", "SalesChannelType", "DefaultPlatformFeePct", "Active"),
    numeric_columns=("DefaultPlatformFeePct",),
    non_negative_columns=("DefaultPlatformFeePct",),
    unique_columns=("PlatformID", "Platform"),
    allowed_values={"Active": frozenset({"Yes", "No"})},
)

DAILY_SALES_SPEC = DatasetSpec(
    required_columns=(
        "Date", "PlatformID", "Platform", "SKU", "ProductName",
        "Orders", "UnitsSold", "GrossSales_INR", "NetSales_INR"
    ),
    non_nullable_columns=(
        "Date", "PlatformID", "Platform", "SKU", "ProductName",
        "Orders", "UnitsSold", "GrossSales_INR", "NetSales_INR"
    ),
    date_columns=("Date",),
    numeric_columns=(
        "Orders", "UnitsSold", "GrossSales_INR", "Discount_INR",
        "NetSales_INR", "AdAttributedUnits", "AdAttributedSales_INR"
    ),
    non_negative_columns=(
        "Orders", "UnitsSold", "GrossSales_INR", "Discount_INR",
        "NetSales_INR", "AdAttributedUnits", "AdAttributedSales_INR"
    ),
    reconciliation=("GrossSales_INR", "NetSales_INR", 0.5),
)

ADVERTISING_SPEC = DatasetSpec(
    required_columns=(
        "Date", "PlatformID", "Platform", "SKU", "ProductName",
        "Impressions", "Clicks", "AttributedOrders", "AttributedUnits",
        "AttributedSales_INR", "AdSpend_INR", "ROAS", "ACOS_Pct"
    ),
    non_nullable_columns=(
        "Date", "PlatformID", "Platform", "SKU", "ProductName",
        "Impressions", "Clicks", "AttributedOrders", "AttributedUnits",
        "AttributedSales_INR", "AdSpend_INR", "ROAS", "ACOS_Pct"
    ),
    date_columns=("Date",),
    numeric_columns=(
        "Impressions", "Clicks", "AttributedOrders", "AttributedUnits",
        "AttributedSales_INR", "AdSpend_INR", "CTR_Pct", "ROAS", "ACOS_Pct"
    ),
    non_negative_columns=(
        "Impressions", "Clicks", "AttributedOrders", "AttributedUnits",
        "AttributedSales_INR", "AdSpend_INR", "CTR_Pct", "ROAS", "ACOS_Pct"
    ),
)

RETURNS_SPEC = DatasetSpec(
    required_columns=(
        "ReturnID", "ReturnDate", "PlatformID", "Platform", "SKU",
        "ProductName", "UnitsReturned", "RefundAmount_INR", "Status"
    ),
    non_nullable_columns=(
        "ReturnID", "ReturnDate", "PlatformID", "Platform", "SKU",
        "ProductName", "UnitsReturned", "RefundAmount_INR", "Status"
    ),
    date_columns=("ReturnDate",),
    numeric_columns=("UnitsReturned", "RefundAmount_INR"),
    non_negative_columns=("UnitsReturned", "RefundAmount_INR"),
    unique_columns=("ReturnID",),
    allowed_values={"Status": frozenset({"Completed", "Processing", "Pending"})},
)

CANCELLATIONS_SPEC = DatasetSpec(
    required_columns=(
        "CancellationID", "CancellationDate", "PlatformID", "Platform",
        "SKU", "ProductName", "UnitsCancelled"
    ),
    non_nullable_columns=(
        "CancellationID", "CancellationDate", "PlatformID", "Platform",
        "SKU", "ProductName", "UnitsCancelled"
    ),
    date_columns=("CancellationDate",),
    numeric_columns=("UnitsCancelled",),
    non_negative_columns=("UnitsCancelled",),
    unique_columns=("CancellationID",),
)

DAILY_COSTS_SPEC = DatasetSpec(
    required_columns=(
        "Date", "PlatformID", "Platform", "SKU", "ProductName",
        "ProductCost_INR", "PlatformFee_INR", "ShippingCost_INR",
        "PaymentFee_INR", "OtherVariableCost_INR"
    ),
    non_nullable_columns=(
        "Date", "PlatformID", "Platform", "SKU", "ProductName",
        "ProductCost_INR", "PlatformFee_INR", "ShippingCost_INR",
        "PaymentFee_INR", "OtherVariableCost_INR"
    ),
    date_columns=("Date",),
    numeric_columns=(
        "ProductCost_INR", "PlatformFee_INR", "ShippingCost_INR",
        "PaymentFee_INR", "OtherVariableCost_INR"
    ),
    non_negative_columns=(
        "ProductCost_INR", "PlatformFee_INR", "ShippingCost_INR",
        "PaymentFee_INR", "OtherVariableCost_INR"
    ),
)

WAREHOUSE_MASTER_SPEC = DatasetSpec(
    required_columns=(
        "WarehouseID", "Region", "Zone", "City", "StorageCapacity_Units", "Status"
    ),
    non_nullable_columns=(
        "WarehouseID", "Region", "Zone", "City", "StorageCapacity_Units", "Status"
    ),
    numeric_columns=("StorageCapacity_Units",),
    non_negative_columns=("StorageCapacity_Units",),
    unique_columns=("WarehouseID",),
    allowed_values={"Status": frozenset({"Active", "Inactive", "Maintenance"})},
)

INVENTORY_DAILY_SPEC = DatasetSpec(
    required_columns=(
        "Date", "WarehouseID", "SKU", "ProductName",
        "OpeningStock_Units", "ClosingStock_Units", "Demand_Units",
        "Fulfilled_Units", "DaysOfCover", "StockStatus"
    ),
    non_nullable_columns=(
        "Date", "WarehouseID", "SKU", "ProductName",
        "OpeningStock_Units", "ClosingStock_Units", "Demand_Units",
        "Fulfilled_Units", "DaysOfCover", "StockStatus"
    ),
    date_columns=("Date",),
    numeric_columns=(
        "OpeningStock_Units", "InboundStock_Units", "Demand_Units",
        "Fulfilled_Units", "ClosingStock_Units", "AvgDailyDemand_7D",
        "DaysOfCover", "ReorderPoint_Units", "RecommendedReorderQty"
    ),
    non_negative_columns=(
        "OpeningStock_Units", "InboundStock_Units", "Demand_Units",
        "Fulfilled_Units", "ClosingStock_Units", "AvgDailyDemand_7D",
        "DaysOfCover", "ReorderPoint_Units", "RecommendedReorderQty"
    ),
    allowed_values={
        "StockStatus": frozenset({"Healthy", "Low Stock", "Critical", "Stockout"}),
        "Stockout": frozenset({"Yes", "No"}),
    },
)

REGIONAL_SALES_SPEC = DatasetSpec(
    required_columns=(
        "Date", "WarehouseID", "Region", "SKU", "ProductName",
        "UnitsSold", "NetSales_INR"
    ),
    non_nullable_columns=(
        "Date", "WarehouseID", "Region", "SKU", "ProductName",
        "UnitsSold", "NetSales_INR"
    ),
    date_columns=("Date",),
    numeric_columns=("UnitsSold", "NetSales_INR"),
    non_negative_columns=("UnitsSold", "NetSales_INR"),
)

DAILY_KPI_SPEC = DatasetSpec(
    required_columns=(
        "Date", "PlatformID", "SKU", "ProductName",
        "Orders", "UnitsSold", "GrossSales_INR", "NetSales_INR",
        "Contribution_INR", "ProfitMargin_Pct", "ProfitabilityStatus"
    ),
    non_nullable_columns=(
        "Date", "PlatformID", "SKU", "ProductName",
        "Orders", "UnitsSold", "GrossSales_INR", "NetSales_INR",
        "Contribution_INR", "ProfitMargin_Pct", "ProfitabilityStatus"
    ),
    date_columns=("Date",),
    numeric_columns=(
        "Orders", "UnitsSold", "GrossSales_INR", "NetSales_INR",
        "AdSpend_INR", "ROAS", "ACOS_Pct", "ProductCost_INR",
        "PlatformFee_INR", "ShippingCost_INR", "PaymentFee_INR",
        "OtherVariableCost_INR", "UnitsReturned", "RefundAmount_INR",
        "UnitsCancelled", "OrganicUnits", "OrganicSales_INR",
        "Contribution_INR", "ProfitMargin_Pct", "ReturnRate_Pct",
        "CancellationRate_Pct", "OrganicShare_Pct"
    ),
    non_negative_columns=(
        "Orders", "UnitsSold", "GrossSales_INR", "NetSales_INR",
        "AdSpend_INR", "ROAS", "ACOS_Pct", "ProductCost_INR",
        "PlatformFee_INR", "ShippingCost_INR", "PaymentFee_INR",
        "OtherVariableCost_INR", "UnitsReturned", "RefundAmount_INR",
        "UnitsCancelled", "OrganicUnits", "OrganicSales_INR",
        "Contribution_INR", "ProfitMargin_Pct", "ReturnRate_Pct",
        "CancellationRate_Pct", "OrganicShare_Pct"
    ),
    allowed_values={
        "ProfitabilityStatus": frozenset({"Healthy", "At Risk", "Unprofitable"}),
    },
)
