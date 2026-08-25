"""HTML email templates for Sleepsia reports.

Provides reusable HTML email templates for various report types.

Author: Claude Code
Date: 2026-08-25
"""

from datetime import datetime, date
from typing import Optional, Dict, Any


def generate_daily_report_html(
    report_id: str,
    report_date: date,
    kpi_data: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate HTML for daily report email."""
    timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')

    # Ensure kpi_data has defaults
    if not kpi_data:
        kpi_data = {}

    kpi_rows = ""
    metrics = [
        ("Revenue", f"₹{kpi_data.get('revenue', 0):,}", "#10b981"),
        ("Orders", f"{kpi_data.get('orders', 0):,}", "#3b82f6"),
        ("Profit", f"₹{kpi_data.get('profit', 0):,.0f}", "#8b5cf6"),
        ("Margin", f"{kpi_data.get('profit_margin', 0):.1f}%", "#f59e0b"),
    ]

    for label, value, color in metrics:
        kpi_rows += f"""
        <div style="display: inline-block; width: 22%; margin: 8px 1.5%; padding: 16px 12px; background-color: {color}; color: white; border-radius: 8px; text-align: center; vertical-align: top; box-sizing: border-box;">
            <div style="font-size: 11px; font-weight: 700; opacity: 0.9; margin-bottom: 8px; letter-spacing: 0.5px;">{label}</div>
            <div style="font-size: 20px; font-weight: bold; line-height: 1.2;">{value}</div>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Report - {report_date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background-color: #f3f4f6;
        }}
        .container {{
            max-width: 680px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .header {{
            background-color: #6366f1;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: #ffffff;
            padding: 50px 32px;
            text-align: center;
            border-bottom: 4px solid #4f46e5;
        }}
        .header h1 {{
            font-size: 30px;
            margin-bottom: 12px;
            font-weight: 800;
            letter-spacing: -0.8px;
            color: #ffffff;
            display: block;
        }}
        .header p {{
            font-size: 15px;
            opacity: 1;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.95);
            margin: 0;
        }}
        .content {{
            padding: 36px 32px;
        }}
        .greeting {{
            font-size: 15px;
            line-height: 1.7;
            margin-bottom: 28px;
            color: #374151;
        }}
        .greeting p {{
            margin: 0 0 8px 0;
        }}
        .section {{
            margin-bottom: 32px;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 3px solid #6366f1;
            display: inline-block;
        }}
        .metric-grid {{
            margin: 24px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: space-between;
        }}
        .feature-list {{
            list-style: none;
            margin: 16px 0;
        }}
        .feature-list li {{
            padding: 12px 0;
            padding-left: 28px;
            position: relative;
            color: #374151;
            font-size: 14px;
            line-height: 1.5;
        }}
        .feature-list li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #10b981;
            font-weight: bold;
            font-size: 18px;
            line-height: 1;
        }}
        .info-box {{
            background-color: #f8fafc;
            padding: 18px;
            border-left: 4px solid #6366f1;
            border-radius: 6px;
            margin-top: 18px;
            font-size: 13px;
            line-height: 1.8;
            color: #4b5563;
        }}
        .info-box strong {{
            color: #1f2937;
            font-weight: 600;
        }}
        .footer {{
            background-color: #f9fafb;
            padding: 32px;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
        }}
        .footer p {{
            margin: 0;
            line-height: 1.6;
        }}
        .footer strong {{
            color: #1f2937;
            font-weight: 600;
        }}
        .divider {{
            height: 1px;
            background-color: #e5e7eb;
            margin: 28px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 13px;
        }}
        th {{
            background-color: #1f2937;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 700;
            border: 1px solid #d1d5db;
        }}
        td {{
            padding: 10px 12px;
            border: 1px solid #d1d5db;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        tr:nth-child(odd) {{
            background-color: #ffffff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Daily Business Report</h1>
            <p>Your daily business intelligence analysis</p>
        </div>

        <!-- Main Content -->
        <div class="content">
            <!-- Greeting -->
            <div class="greeting">
                <p>Hello,</p>
                <p>Your daily business report for <strong>{report_date}</strong> is ready.</p>
            </div>

            <!-- Report Contents -->
            <div class="section">
                <div class="section-title">📋 Report Contents</div>
                <ul class="feature-list">
                    <li>Platform performance metrics</li>
                    <li>Product performance analysis</li>
                    <li>Advertising ROI and efficiency</li>
                    <li>Profitability analysis</li>
                    <li>Key recommendations</li>
                </ul>
            </div>

            <!-- Report Info -->
            <div class="info-box">
                <strong>Report ID:</strong> {report_id}<br>
                <strong>Date:</strong> {report_date}<br>
                <strong>Generated:</strong> {timestamp}
            </div>

            <div class="divider"></div>

            <!-- Footer Message -->
            <div style="text-align: center; margin: 28px 0; font-size: 14px; color: #6b7280;">
                <p>Questions about your business metrics? Contact support@sleepsia.com</p>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p style="margin-bottom: 12px;">
                <strong>Sleepsia Analytics System</strong><br>
                Intelligent Business Intelligence Platform
            </p>
            <p style="margin-top: 16px; opacity: 0.85;">
                This is an automated report. Do not reply to this email.
            </p>
        </div>
    </div>
</body>
</html>
    """.strip()


def generate_comprehensive_report_html(
    report_id: str,
    start_date: date,
    end_date: date,
    kpi_data: Optional[Dict[str, Any]] = None,
    detailed_data: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate HTML for comprehensive report email with detailed data tables."""
    timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')

    # Ensure kpi_data has defaults
    if not kpi_data:
        kpi_data = {}
    if not detailed_data:
        detailed_data = {}

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sleepsia Business Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background-color: #f3f4f6;
        }}
        .container {{
            max-width: 680px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .header {{
            background-color: #6366f1;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: #ffffff;
            padding: 50px 32px;
            text-align: center;
            border-bottom: 4px solid #4f46e5;
        }}
        .header h1 {{
            font-size: 32px;
            margin-bottom: 12px;
            font-weight: 800;
            letter-spacing: -0.8px;
            color: #ffffff;
            display: block;
        }}
        .header p {{
            font-size: 15px;
            opacity: 1;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.95);
            margin: 0;
        }}
        .content {{
            padding: 36px 32px;
        }}
        .greeting {{
            font-size: 15px;
            line-height: 1.7;
            margin-bottom: 28px;
            color: #374151;
        }}
        .greeting p {{
            margin: 0 0 8px 0;
        }}
        .section {{
            margin-bottom: 32px;
        }}
        .section:last-of-type {{
            margin-bottom: 24px;
        }}
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 3px solid #6366f1;
            display: inline-block;
        }}
        .metric-grid {{
            margin: 24px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: space-between;
        }}
        .metric-card {{
            flex: 1;
            min-width: 140px;
            padding: 18px 14px;
            border-radius: 10px;
            color: white;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .metric-label {{
            font-size: 11px;
            font-weight: 700;
            opacity: 0.92;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metric-value {{
            font-size: 22px;
            font-weight: 700;
            line-height: 1.3;
        }}
        .feature-list {{
            list-style: none;
            margin: 16px 0;
        }}
        .feature-list li {{
            padding: 12px 0;
            padding-left: 28px;
            position: relative;
            color: #374151;
            font-size: 14px;
            line-height: 1.5;
        }}
        .feature-list li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #10b981;
            font-weight: bold;
            font-size: 18px;
            line-height: 1;
        }}
        .file-formats {{
            margin: 18px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .file-format {{
            display: inline-block;
            background-color: #f0f4ff;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 12px;
            color: #4f46e5;
            font-weight: 600;
            border: 1px solid #e0e7ff;
        }}
        .info-box {{
            background-color: #f8fafc;
            padding: 18px;
            border-left: 4px solid #6366f1;
            border-radius: 6px;
            margin-top: 18px;
            font-size: 13px;
            line-height: 1.8;
            color: #4b5563;
        }}
        .info-box strong {{
            color: #1f2937;
            font-weight: 600;
        }}
        .footer {{
            background-color: #f9fafb;
            padding: 32px;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
        }}
        .footer p {{
            margin: 0;
            line-height: 1.6;
        }}
        .footer strong {{
            color: #1f2937;
            font-weight: 600;
        }}
        .divider {{
            height: 1px;
            background-color: #e5e7eb;
            margin: 28px 0;
        }}
        .cta-section {{
            text-align: center;
            margin: 28px 0;
        }}
        .cta-text {{
            color: #6b7280;
            font-size: 14px;
            margin-bottom: 12px;
        }}
        .cta-link {{
            color: #6366f1;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.2s;
        }}
        .cta-link:hover {{
            color: #4f46e5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Sleepsia Business Report</h1>
            <p>Your comprehensive business intelligence analysis</p>
        </div>

        <!-- Main Content -->
        <div class="content">
            <!-- Greeting -->
            <div class="greeting">
                <p>Hello,</p>
                <p>Please find your comprehensive business report attached. This analysis covers the period from <strong>{start_date}</strong> to <strong>{end_date}</strong>.</p>
            </div>

            <!-- Report Contents -->
            <div class="section">
                <div class="section-title">📋 Report Contents</div>
                <ul class="feature-list">
                    <li>Executive Summary with Key Performance Indicators</li>
                    <li>Platform Performance Analysis</li>
                    <li>Product Profitability Analysis</li>
                    <li>Advertising ROI and Efficiency Metrics</li>
                    <li>Detailed Data Sheets (Excel)</li>
                </ul>
            </div>

            <!-- File Formats -->
            <div class="section">
                <div class="section-title">📦 Included Formats</div>
                <div class="file-formats">
                    <span class="file-format">📄 PDF Report</span>
                    <span class="file-format">📊 Excel Sheets</span>
                    <span class="file-format">🔗 JSON Data</span>
                </div>
                <div class="info-box">
                    <strong>Report ID:</strong> {report_id}<br>
                    <strong>Period:</strong> {start_date} to {end_date}<br>
                    <strong>Generated:</strong> {timestamp}
                </div>
            </div>

            <div class="divider"></div>

            <!-- Call to Action -->
            <div class="cta-section">
                <p class="cta-text">Need help interpreting the data? Questions about your business metrics?</p>
                <a href="mailto:support@sleepsia.com" class="cta-link">Contact Support</a>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p style="margin-bottom: 12px;">
                <strong>Sleepsia Analytics System</strong><br>
                Intelligent Business Intelligence Platform
            </p>
            <p style="margin-top: 16px; opacity: 0.85;">
                This is an automated report. Do not reply to this email.<br>
                For questions, contact support@sleepsia.com
            </p>
        </div>
    </div>
</body>
</html>
    """.strip()
