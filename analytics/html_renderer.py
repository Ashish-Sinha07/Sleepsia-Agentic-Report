"""HTML report renderer."""

from analytics.report_models import Report


class HTMLRenderer:
    """Renders reports to professional HTML format."""

    @staticmethod
    def render(report: Report) -> str:
        """Render a report to HTML string."""
        html = []

        html.append("<!DOCTYPE html>")
        html.append("<html lang=\"en\">")
        html.append("<head>")
        html.append("<meta charset=\"UTF-8\">")
        html.append("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
        html.append(f"<title>{report.title}</title>")
        html.append(HTMLRenderer._get_styles())
        html.append("</head>")
        html.append("<body>")

        html.append(HTMLRenderer._render_header(report))
        html.append(HTMLRenderer._render_executive_summary(report))
        html.append(HTMLRenderer._render_overall_metrics(report))

        if report.product_sections:
            html.append(HTMLRenderer._render_product_sections(report))

        if report.platform_sections:
            html.append(HTMLRenderer._render_platform_sections(report))

        if report.advertising_section:
            html.append(HTMLRenderer._render_advertising_section(report))

        if report.profitability_section:
            html.append(HTMLRenderer._render_profitability_section(report))

        if report.quality_section:
            html.append(HTMLRenderer._render_quality_section(report))

        if report.insights:
            html.append(HTMLRenderer._render_insights(report))

        if report.recommendations:
            html.append(HTMLRenderer._render_recommendations(report))

        html.append(HTMLRenderer._render_footer(report))

        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    @staticmethod
    def _get_styles() -> str:
        """Return CSS styles for the report."""
        return """<style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        header {
            border-bottom: 3px solid #2c3e50;
            margin-bottom: 30px;
            padding-bottom: 20px;
        }
        h1 {
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 10px;
        }
        h2 {
            color: #34495e;
            font-size: 20px;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }
        h3 {
            color: #34495e;
            font-size: 16px;
            margin-top: 15px;
            margin-bottom: 10px;
        }
        .section {
            margin-bottom: 30px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
        }
        .metric-card h4 {
            font-size: 13px;
            color: #7f8c8d;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .metric-card .value {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        .metric-card .unit {
            font-size: 12px;
            color: #95a5a6;
            margin-left: 5px;
        }
        .status-healthy {
            color: #27ae60;
        }
        .status-at-risk {
            color: #f39c12;
        }
        .status-critical {
            color: #e74c3c;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th {
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        tr:nth-child(even) {
            background: #f8f9fa;
        }
        .insight {
            background: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .insight-title {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .insight-priority {
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            display: inline-block;
            margin-left: 10px;
        }
        .recommendation {
            background: #f0f8e8;
            border-left: 4px solid #27ae60;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .recommendation-action {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        footer {
            border-top: 1px solid #ecf0f1;
            margin-top: 30px;
            padding-top: 15px;
            font-size: 12px;
            color: #95a5a6;
        }
        @media print {
            body {
                background: white;
            }
            .container {
                box-shadow: none;
                padding: 0;
            }
        }
        </style>"""

    @staticmethod
    def _render_header(report: Report) -> str:
        """Render report header."""
        return f"""<div class="container">
        <header>
            <h1>{report.title}</h1>
            <div style="color: #7f8c8d; font-size: 13px;">
                Report ID: {report.report_id} | Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </header>"""

    @staticmethod
    def _render_executive_summary(report: Report) -> str:
        """Render executive summary section."""
        return f"""<section class="section">
        <h2>Executive Summary</h2>
        <p>{report.executive_summary}</p>
        <p style="font-size: 13px; color: #7f8c8d; margin-top: 10px;">
            Data Completeness: {report.data_completeness_pct:.0f}%
        </p>
        </section>"""

    @staticmethod
    def _render_overall_metrics(report: Report) -> str:
        """Render overall metrics."""
        metrics = report.overall_metrics
        html = ["<section class=\"section\">"]
        html.append("<h2>Overall Metrics</h2>")
        html.append("<div class=\"metrics-grid\">")

        html.append(f"""<div class="metric-card">
            <h4>Orders</h4>
            <div class="value">{metrics.total_orders}</div>
        </div>""")

        html.append(f"""<div class="metric-card">
            <h4>Units Sold</h4>
            <div class="value">{metrics.total_units_sold}</div>
        </div>""")

        html.append(f"""<div class="metric-card">
            <h4>Net Sales</h4>
            <div class="value">₹{metrics.total_net_sales_inr:,.0f}</div>
        </div>""")

        status_class = "status-healthy" if metrics.overall_profit_margin_pct >= 15 else "status-critical"
        html.append(f"""<div class="metric-card">
            <h4>Profit Margin</h4>
            <div class="value {status_class}">{metrics.overall_profit_margin_pct:.1f}%</div>
        </div>""")

        html.append(f"""<div class="metric-card">
            <h4>Ad Spend</h4>
            <div class="value">₹{metrics.total_ad_spend_inr:,.0f}</div>
        </div>""")

        html.append(f"""<div class="metric-card">
            <h4>Organic Share</h4>
            <div class="value">{metrics.organic_share_pct:.1f}%</div>
        </div>""")

        html.append("</div></section>")
        return "\n".join(html)

    @staticmethod
    def _render_product_sections(report: Report) -> str:
        """Render product sections."""
        html = ["<section class=\"section\">"]
        html.append("<h2>Product Performance</h2>")

        for product in report.product_sections:
            status_class = "status-healthy" if product.profit_margin_pct >= 15 else "status-critical"
            html.append(f"""<h3>{product.product_name} ({product.sku})</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Units Sold</td>
                    <td>{product.units_sold}</td>
                </tr>
                <tr>
                    <td>Net Sales</td>
                    <td>₹{product.net_sales_inr:,.0f}</td>
                </tr>
                <tr>
                    <td>Ad Spend</td>
                    <td>₹{product.ad_spend_inr:,.0f}</td>
                </tr>
                <tr>
                    <td>ROAS</td>
                    <td>{product.roas:.2f}x</td>
                </tr>
                <tr>
                    <td>ACOS</td>
                    <td>{product.acos_pct:.1f}%</td>
                </tr>
                <tr>
                    <td>Profit Margin</td>
                    <td class="{status_class}">{product.profit_margin_pct:.1f}%</td>
                </tr>
                <tr>
                    <td>Return Rate</td>
                    <td>{product.return_rate_pct:.1f}%</td>
                </tr>
                <tr>
                    <td>Cancellation Rate</td>
                    <td>{product.cancellation_rate_pct:.1f}%</td>
                </tr>
            </table>""")

        html.append("</section>")
        return "\n".join(html)

    @staticmethod
    def _render_platform_sections(report: Report) -> str:
        """Render platform sections."""
        html = ["<section class=\"section\">"]
        html.append("<h2>Platform Performance</h2>")

        for platform in report.platform_sections:
            html.append(f"""<h3>{platform.platform_name}</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Products</td>
                    <td>{platform.product_count}</td>
                </tr>
                <tr>
                    <td>Total Units</td>
                    <td>{platform.total_units_sold}</td>
                </tr>
                <tr>
                    <td>Total Sales</td>
                    <td>₹{platform.total_net_sales_inr:,.0f}</td>
                </tr>
                <tr>
                    <td>Platform ROAS</td>
                    <td>{platform.platform_roas:.2f}x</td>
                </tr>
                <tr>
                    <td>Profit Margin</td>
                    <td>{platform.overall_profit_margin_pct:.1f}%</td>
                </tr>
            </table>""")

        html.append("</section>")
        return "\n".join(html)

    @staticmethod
    def _render_advertising_section(report: Report) -> str:
        """Render advertising section."""
        ad = report.advertising_section
        return f"""<section class="section">
        <h2>Advertising Performance</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Ad Spend</td>
                <td>₹{ad.total_ad_spend_inr:,.0f}</td>
            </tr>
            <tr>
                <td>Attributed Sales</td>
                <td>₹{ad.total_attributed_sales_inr:,.0f}</td>
            </tr>
            <tr>
                <td>ROAS</td>
                <td>{ad.overall_roas:.2f}x</td>
            </tr>
            <tr>
                <td>ACOS</td>
                <td>{ad.overall_acos_pct:.1f}%</td>
            </tr>
            <tr>
                <td>Attributed Units</td>
                <td>{ad.attributed_units}</td>
            </tr>
        </table>
        </section>"""

    @staticmethod
    def _render_profitability_section(report: Report) -> str:
        """Render profitability section."""
        prof = report.profitability_section
        return f"""<section class="section">
        <h2>Profitability Analysis</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Net Sales</td>
                <td>₹{prof.total_net_sales_inr:,.0f}</td>
            </tr>
            <tr>
                <td>Total Cost</td>
                <td>₹{prof.total_cost_inr:,.0f}</td>
            </tr>
            <tr>
                <td>Total Contribution</td>
                <td>₹{prof.total_contribution_inr:,.0f}</td>
            </tr>
            <tr>
                <td>Profit Margin</td>
                <td>{prof.overall_profit_margin_pct:.1f}%</td>
            </tr>
            <tr>
                <td>Products (Healthy / At-Risk / Unprofitable)</td>
                <td>{prof.products_healthy} / {prof.products_at_risk} / {prof.products_unprofitable}</td>
            </tr>
        </table>
        </section>"""

    @staticmethod
    def _render_quality_section(report: Report) -> str:
        """Render quality section."""
        quality = report.quality_section
        return f"""<section class="section">
        <h2>Quality Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Total Units Sold</td>
                <td>{quality.total_units_sold}</td>
            </tr>
            <tr>
                <td>Units Returned</td>
                <td>{quality.total_units_returned}</td>
            </tr>
            <tr>
                <td>Return Rate</td>
                <td>{quality.overall_return_rate_pct:.1f}%</td>
            </tr>
            <tr>
                <td>Total Refunds</td>
                <td>₹{quality.total_refund_amount_inr:,.0f}</td>
            </tr>
            <tr>
                <td>Units Cancelled</td>
                <td>{quality.total_units_cancelled}</td>
            </tr>
            <tr>
                <td>Cancellation Rate</td>
                <td>{quality.overall_cancellation_rate_pct:.1f}%</td>
            </tr>
        </table>
        </section>"""

    @staticmethod
    def _render_insights(report: Report) -> str:
        """Render insights section."""
        html = ["<section class=\"section\">"]
        html.append("<h2>Key Insights</h2>")

        for insight in report.insights:
            html.append(f"""<div class="insight">
                <div class="insight-title">
                    {insight.title}
                    <span class="insight-priority">{insight.priority}</span>
                </div>
                <div>{insight.description}</div>
            </div>""")

        html.append("</section>")
        return "\n".join(html)

    @staticmethod
    def _render_recommendations(report: Report) -> str:
        """Render recommendations section."""
        html = ["<section class=\"section\">"]
        html.append("<h2>Recommendations</h2>")

        for rec in report.recommendations:
            html.append(f"""<div class="recommendation">
                <div class="recommendation-action">
                    {rec.action}
                    <span class="insight-priority" style="background: #27ae60; color: white; padding: 2px 6px; border-radius: 3px;">
                        {rec.priority}
                    </span>
                </div>
                <div><strong>Rationale:</strong> {rec.rationale}</div>
                <div><strong>Owner:</strong> {rec.owner}</div>
            </div>""")

        html.append("</section>")
        return "\n".join(html)

    @staticmethod
    def _render_footer(report: Report) -> str:
        """Render footer."""
        return f"""</div>
        <footer>
            <p>Report generated by Sleepsia Agentic Reporting System</p>
            <p>This report contains proprietary business information. Treat as confidential.</p>
        </footer>"""
