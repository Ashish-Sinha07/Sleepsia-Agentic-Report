"""
Sleepsia Reporting Module

Provides comprehensive PDF and Excel report generation capabilities for omni-channel
e-commerce analytics and financial reporting.

Key Components:
- OmniChannelReport: Data model defining the contract between Analytics and Reporting
- ReportService: Main orchestration service for report generation
- PDFReportGenerator: Generates professional PDF reports
- ExcelReportGenerator: Generates comprehensive Excel workbooks
- Sample Data Generator: Provides mock data for development and testing

Usage:
    from reports.report_service import ReportService
    from reports.sample_data.sample_data_generator import generate_sample_report_data

    # Generate sample data (or use real data from Analytics layer)
    report_data = generate_sample_report_data()

    # Create report service
    service = ReportService()

    # Generate and save reports
    results = service.generate_and_save_reports(report_data, formats=['pdf', 'excel'])
    print(f"PDF saved to: {results['pdf']}")
    print(f"Excel saved to: {results['excel']}")

Data Contract:
The Analytics layer must provide OmniChannelReport objects with:
- Platform-level financial and operational metrics
- Product-level performance across platforms
- Consolidated P&L statement
- Channel efficiency rankings
- Management summary with recommendations

All metrics must be calculated according to business rules in .claude/business-rules.md

No business logic belongs in the Reporting layer - only data transformation and presentation.
"""

from reports.models.report_models import (
    OmniChannelReport,
    ReportData,
    PlatformSummary,
    ProductMetrics,
    ConsolidatedProductMetrics,
    PnLStatement,
    ChannelEfficiency,
    ReportMetadata,
    ManagementSummary,
)

from reports.report_service import ReportService

from reports.sample_data.sample_data_generator import generate_sample_report_data

__all__ = [
    "OmniChannelReport",
    "ReportData",
    "PlatformSummary",
    "ProductMetrics",
    "ConsolidatedProductMetrics",
    "PnLStatement",
    "ChannelEfficiency",
    "ReportMetadata",
    "ManagementSummary",
    "ReportService",
    "generate_sample_report_data",
]

__version__ = "1.0.0"
