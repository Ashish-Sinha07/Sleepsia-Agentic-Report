# Sleepsia Reporting Module Documentation

## Overview

The Reporting module provides comprehensive PDF and Excel report generation capabilities for Sleepsia's omni-channel e-commerce analytics platform.

**Key Responsibility**: Transform analytical results from the Analytics layer into professional, actionable reports for management and stakeholders.

**Module Owner**: Developer 4 (Reporting)

**Not Responsible For**:
- Calculating business metrics (Analytics layer)
- Storing/retrieving data from database (Backend/Analytics layers)
- Sending reports via email (Automation layer via Power Automate)
- User interface (Frontend layer)

## Architecture

### Data Flow

```
Analytics Layer
    ↓ (provides OmniChannelReport)
Reporting Module
    ├─ PDF Generator → PDF bytes
    └─ Excel Generator → Excel bytes
    ↓
Report Service
    ├─ Validates data
    ├─ Generates reports
    ├─ Saves files
    └─ Returns metadata
    ↓
Backend API / File Storage
    ↓
Power Automate (Distribution)
    ↓
Outlook / Teams
```

### Module Structure

```
reports/
├── __init__.py                          # Module exports
├── REPORTING_DOCUMENTATION.md           # This file
├── report_service.py                    # Main orchestration service
│
├── models/
│   ├── __init__.py
│   └── report_models.py                 # Data contract with Analytics
│
├── generators/
│   ├── __init__.py
│   ├── pdf_generator.py                 # PDF report generation
│   └── excel_generator.py               # Excel report generation
│
├── utils/
│   ├── __init__.py
│   └── formatting.py                    # Formatting utilities
│
├── sample-data/
│   ├── __init__.py
│   └── sample_data_generator.py         # Mock data for development
│
└── tests/
    ├── __init__.py
    ├── test_report_models.py            # Data model tests
    ├── test_report_service.py           # Service tests
    └── test_formatting.py               # Formatting tests
```

## Data Contract

### Input: OmniChannelReport

The Analytics layer must provide an `OmniChannelReport` object containing:

```python
class OmniChannelReport:
    # Metadata
    metadata: ReportMetadata
    
    # Platform-level summaries (one for each active platform)
    platforms: List[PlatformSummary]
    
    # Consolidated product metrics across all platforms
    consolidated_products: List[ConsolidatedProductMetrics]
    
    # P&L statement
    pnl: PnLStatement
    
    # Channel efficiency ranking
    channel_efficiency: List[ChannelEfficiency]
    
    # Executive summary and recommendations
    management_summary: Optional[ManagementSummary]
```

### Platform Summary Structure

Each platform contains:
- **Financial metrics**: Gross revenue, returns, net revenue, profit, margin
- **Advertising metrics**: Ad spend, TACoS, ROAS, ACOS
- **Operational metrics**: OTIF (On-Time In-Full), orders, units
- **Product breakdown**: Detailed metrics for each SKU on that platform

### Key Metrics Required

The Analytics layer must calculate (NOT the Reporting layer):

1. **Revenue Metrics**
   - Gross Revenue (invoiced sales)
   - Returns & Refunds (customer returns)
   - Net Realized Revenue (Gross - Returns)

2. **Advertising Metrics**
   - Ad Spend (total ad budget)
   - TACoS (Total Advertising Cost of Sales) = Ad Spend / Net Revenue
   - ROAS (Return on Ad Spend) = Ad-attributed Sales / Ad Spend
   - ACOS (Ad Cost of Sales) = Ad Spend / Ad-attributed Sales

3. **Profitability Metrics**
   - Contribution = Net Revenue - COGS - Fees - Ad Spend
   - Net Profit Margin = Contribution / Net Revenue

4. **Operational Metrics**
   - Return Rate = Returned Units / Sold Units
   - Fulfillment OTIF (On-Time In-Full)

See `.claude/business-rules.md` for complete formulas.

## API Reference

### ReportService

Main orchestration service for report generation.

#### Initialization

```python
from reports.report_service import ReportService

# Initialize with default directory
service = ReportService()

# Or specify custom output directory
service = ReportService(output_dir="/path/to/reports")
```

#### Generate PDF Report

```python
# Generate PDF bytes
pdf_bytes = service.generate_pdf_report(report_data)

# Or generate and save to disk in one call
pdf_path = service.save_pdf_report(report_data, pdf_bytes)

# Or use convenience method
pdf_path = service.save_pdf_report(
    report_data, 
    pdf_bytes,
    filename="custom_name.pdf"
)
```

#### Generate Excel Report

```python
# Generate Excel bytes
excel_bytes = service.generate_excel_report(report_data)

# Or save directly
excel_path = service.save_excel_report(report_data, excel_bytes)
```

#### Generate Both Reports

```python
# Convenient method to generate and save both formats
results = service.generate_and_save_reports(
    report_data,
    formats=['pdf', 'excel']  # or ['pdf'] or ['excel']
)

# Results contain file paths
print(results['pdf'])      # "/path/to/report.pdf"
print(results['excel'])    # "/path/to/report.xlsx"
```

#### Validate Report Data

```python
try:
    service.validate_report_data(report_data)
    print("Report data is valid")
except ValueError as e:
    print(f"Validation error: {e}")
```

#### Extract Metadata

```python
metadata = service.get_report_metadata(report_data)
# Returns: {
#     'report_type': '...',
#     'audit_date': '2026-08-20',
#     'organization': 'Sleepsia India',
#     'total_platforms': 4,
#     'total_products': 8,
#     ...
# }
```

## Report Sections

### PDF Report Structure

1. **Cover Page**
   - Report title
   - Organization
   - Audit date
   - Scope
   - Status

2. **Executive Summary**
   - Summary narrative
   - Key findings (top 5)
   - Alerts and opportunities

3. **Platform Performance (1.1-1.6)**
   - One section per active platform
   - Platform-level KPIs
   - Product breakdown table

4. **Consolidated Analysis (Section 2)**
   - All products aggregated across platforms
   - Stock days of cover
   - Product rankings

5. **P&L Statement (Section 3)**
   - Complete profit and loss statement
   - Gross GMV → Net profit
   - Percentage breakdowns

6. **Channel Efficiency Rankings**
   - Platform ranking by profitability
   - Key metrics for comparison
   - OTIF and margin percentages

7. **Recommendations**
   - Actionable recommendations
   - Strategic opportunities
   - Risk alerts

### Excel Report Structure

Multiple worksheets:

1. **Cover** - Report metadata
2. **Executive Summary** - Text summary, key findings, alerts, opportunities
3. **[Platform Name]** - One sheet per platform with detailed breakdown
4. **Consolidated Products** - Product analysis across all channels
5. **P&L Statement** - Financial summary
6. **Channel Efficiency** - Platform rankings
7. **Recommendations** - All recommendations and alerts

Excel format allows for:
- Filtering and sorting
- Further analysis
- Custom calculations
- Distribution via email

## Formatting Standards

### Currency

Uses Indian numbering conventions:

```
₹10,000,000 → ₹1.00Cr (Crore)
₹100,000 → ₹1.00L (Lakh)
₹5,000 → ₹5,000
```

### Percentages

- Displayed with 2 decimal places: `23.45%`
- For TACOS and margins: `23.45%`
- For return rates: `2.45%`

### Units

- Millions: `1.50M`
- Thousands: `45.50K`
- Regular: `500`

### Status Indicators

- ✓ Healthy / Profitable / Efficient
- ⚠ Low / Warning / Review
- ✗ Critical / Loss-making / Inefficient
- — Data unavailable

## Usage Examples

### Complete Workflow

```python
from reports import ReportService, generate_sample_report_data

# 1. Get report data from Analytics layer
report_data = analytics_layer.get_omnichannel_report(
    start_date='2026-08-01',
    end_date='2026-08-20'
)

# 2. Create report service
service = ReportService()

# 3. Generate and save reports
results = service.generate_and_save_reports(
    report_data,
    formats=['pdf', 'excel']
)

# 4. Now results contain file paths ready for distribution
print(f"PDF: {results['pdf']}")
print(f"Excel: {results['excel']}")

# 5. (Optional) Get metadata for email template
metadata = service.get_report_metadata(report_data)
# Use metadata to populate email subject, date, etc.
```

### Using Sample Data for Development

```python
from reports import ReportService, generate_sample_report_data

# Generate mock data (mirrors reference audit report)
sample_report = generate_sample_report_data()

# Test report generation without Analytics layer
service = ReportService()
results = service.generate_and_save_reports(sample_report)

# Files are ready for testing, validation, etc.
```

### Error Handling

```python
from reports import ReportService
from reports.models.report_models import OmniChannelReport

service = ReportService()

try:
    # Validate first
    service.validate_report_data(report_data)
    
    # Generate
    pdf_bytes = service.generate_pdf_report(report_data)
    excel_bytes = service.generate_excel_report(report_data)
    
except ValueError as e:
    print(f"Data validation error: {e}")
    # Handle invalid report structure
    
except RuntimeError as e:
    print(f"Generation error: {e}")
    # Handle PDF/Excel generation failure
```

## Integration with Analytics Layer

### What Analytics Must Provide

The Analytics module (Developer 2) must:

1. Calculate all business metrics per `.claude/business-rules.md`
2. Create an `OmniChannelReport` object
3. Populate all required fields
4. Call `report.validate()` before returning

### What Reporting Does With It

The Reporting module (Developer 4):

1. Receives `OmniChannelReport` from Analytics
2. Validates the structure
3. Generates PDF using PDFReportGenerator
4. Generates Excel using ExcelReportGenerator
5. Returns file paths or bytes
6. Does NOT recalculate any metrics

### API Endpoint (Backend)

The FastAPI backend will expose:

```python
# POST /api/reports/generate
{
    "report_type": "Management Summary",  # or other types
    "start_date": "2026-08-01",
    "end_date": "2026-08-20",
    "platforms": ["all"],  # or specific platforms
    "formats": ["pdf", "excel"]
}

# Returns:
{
    "pdf": "s3://bucket/reports/Sleepsia_Report_2026-08-20.pdf",
    "excel": "s3://bucket/reports/Sleepsia_Report_2026-08-20.xlsx",
    "generated_at": "2026-08-21T10:30:00Z"
}
```

## Testing

### Run All Tests

```bash
# From project root
pytest reports/tests/ -v
```

### Run Specific Test Suite

```bash
pytest reports/tests/test_report_service.py -v
pytest reports/tests/test_report_models.py -v
pytest reports/tests/test_formatting.py -v
```

### Test Coverage

- Data model validation
- Report service orchestration
- PDF generation
- Excel generation
- Formatting functions
- File saving
- Error handling

All tests use sample data (no database dependency).

## Dependencies

### Required Python Packages

```
openpyxl>=3.0.0          # Excel generation
reportlab>=4.0.0         # PDF generation
pydantic>=1.10.0         # Data validation (implicit)
```

### Optional/Development

```
pytest>=7.0.0            # Testing
pytest-cov>=4.0.0        # Coverage reporting
```

### Installation

```bash
pip install -r reports/requirements.txt
```

## Troubleshooting

### PDF Generation Fails

**Symptom**: `RuntimeError: Failed to generate PDF report`

**Causes**:
1. reportlab not installed: `pip install reportlab`
2. Report data missing required fields
3. Corrupted Decimal values

**Solution**: Check report validation passes first

### Excel Generation Fails

**Symptom**: `RuntimeError: Failed to generate Excel report`

**Causes**:
1. openpyxl not installed: `pip install openpyxl`
2. Unicode/encoding issues
3. File permission on output directory

**Solution**: Verify openpyxl version and output directory permissions

### Validation Fails

**Symptom**: `ValueError: [specific validation error]`

**Check**:
1. All platforms have platform_name
2. All metrics are Decimal type
3. Consolidated products list is not empty
4. P&L statement is present

### Files Not Saved

**Causes**:
1. Output directory doesn't exist or no write permissions
2. Disk full
3. Invalid filename characters

**Solution**: Verify `ReportService.output_dir` exists and is writable

## Performance Considerations

### Large Reports

- Reports with 1000+ products take ~5-10 seconds to generate
- Memory usage: ~50-100MB for complete report data in memory
- File size: 
  - PDF: 2-5 MB
  - Excel: 1-2 MB

### Optimization

For very large reports:
1. Filter by platform to generate per-platform reports
2. Use Excel format instead of PDF (smaller, faster)
3. Consider pagination in PDF generator

## Future Enhancements

Potential improvements (not in MVP):

1. **Report Types**
   - Platform-specific reports
   - Product-specific deep dives
   - Inventory exception reports

2. **Formatting**
   - Branded PDF header/footer
   - Custom color schemes
   - Logo embedding

3. **Delivery**
   - Scheduled report generation
   - Email delivery integration
   - Cloud storage (S3, Azure)

4. **Interactivity**
   - Interactive Excel with charts
   - PDF with hyperlinks
   - Dynamic drilldowns

## Reference Files

- `.claude/CLAUDE.md` - Project overview
- `.claude/business-rules.md` - Metric calculation rules
- `.claude/development-plan.md` - Development timeline
- `reports/sample_data_generator.py` - Reference data structure
- PDF audit report (reference) - Layout and content model

## Support

For issues or questions:
1. Check this documentation
2. Review test cases for usage examples
3. Check sample data for data structure
4. Review error messages - they are descriptive
5. Check existing GitHub issues

## Version History

**v1.0.0** (2026-08-21)
- Initial MVP implementation
- PDF generation (reportlab-based)
- Excel generation (openpyxl-based)
- Report service orchestration
- Comprehensive test suite
- Formatting utilities
- Sample data generator
