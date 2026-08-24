#!/usr/bin/env python3
"""Test comprehensive report generation with agent integration."""

import sys
from datetime import date
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database import SessionLocal
from backend.app.services.comprehensive_report_service import ComprehensiveReportService

def main():
    """Test comprehensive report generation."""
    db = SessionLocal()

    try:
        print("\n" + "=" * 80)
        print("TESTING COMPREHENSIVE REPORT GENERATION WITH AGENT INTEGRATION")
        print("=" * 80 + "\n")

        service = ComprehensiveReportService(db=db)

        # Generate report
        result = service.generate_full_report(
            start_date=date(2026, 8, 24),
            end_date=date(2026, 8, 24),
            report_type="executive_summary",
        )

        if result.get("success"):
            report_id = result.get("report_id")
            print(f"\n[OK] Report Generated Successfully: {report_id}\n")

            # Save PDF to disk
            pdf_bytes = result.get("pdf_bytes")
            pdf_path = Path("backend/reports") / f"{report_id}.pdf"
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            pdf_path.write_bytes(pdf_bytes)
            print(f"[OK] PDF saved: {pdf_path} ({len(pdf_bytes)} bytes)\n")

            # Display metrics
            metrics = result.get("metrics", {})
            print("Key Metrics:")
            print(f"  Revenue: Rs {metrics.get('revenue', 0):,.0f}")
            print(f"  Profit: Rs {metrics.get('profit', 0):,.0f}")
            print(f"  Profit Margin: {metrics.get('profit_margin', 0):.1f}%")
            print(f"  Orders: {metrics.get('orders', 0):,}")
            print(f"  Units: {metrics.get('units', 0):,}")
            print(f"  ROAS: {metrics.get('roas', 0):.2f}x\n")

            # Display insights
            insights = result.get("insights", [])
            print(f"Generated Insights: {len(insights)}")
            for insight in insights[:5]:
                print(f"  - {insight['title']} ({insight['priority']})")
            print()

            # Display recommendations
            recommendations = result.get("recommendations", [])
            print(f"Generated Recommendations: {len(recommendations)}")
            for rec in recommendations[:5]:
                print(f"  - {rec['action']}")
            print()

            print("=" * 80)
            print("[OK] TEST COMPLETE - Report generation with agents working!")
            print("=" * 80 + "\n")

            return 0
        else:
            print(f"[FAIL] Report generation failed: {result.get('error')}")
            return 1

    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
