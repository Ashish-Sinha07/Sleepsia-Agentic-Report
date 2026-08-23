from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from pydantic import BaseModel

from app.database import get_db
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


class GenerateReportRequest(BaseModel):
    """Request to generate a business report."""
    report_type: str  # executive_summary, platform_analysis, product_analysis, profitability, advertising, inventory
    start_date: date
    end_date: date
    format: str = "pdf"  # pdf, excel, html
    include_recommendations: bool = True
    platform_filter: Optional[str] = None
    warehouse_filter: Optional[str] = None


class ReportMetadata(BaseModel):
    """Metadata about a report."""
    report_id: str
    report_type: str
    created_at: str
    start_date: date
    end_date: date
    status: str  # pending, completed, failed
    file_size: Optional[int] = None
    download_url: Optional[str] = None


class ReportListResponse(BaseModel):
    """List of reports."""
    reports: List[ReportMetadata]
    total: int


@router.get("", response_model=ReportListResponse)
async def list_reports(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict:
    """Get list of generated reports."""
    reports = ReportService.list_reports(db, limit, offset)
    return reports


@router.post("", response_model=ReportMetadata)
async def generate_report(
    request: GenerateReportRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Generate a new business report.

    Supported report types:
    - executive_summary: KPIs and top insights
    - platform_analysis: Performance by platform
    - product_analysis: Product profitability analysis
    - profitability: Detailed margin analysis
    - advertising: Ad efficiency and ROI analysis
    - inventory: Warehouse and stock analysis
    - management_monthly: Comprehensive monthly report
    """
    try:
        report = ReportService.generate_report(
            db=db,
            report_type=request.report_type,
            start_date=request.start_date,
            end_date=request.end_date,
            format=request.format,
            include_recommendations=request.include_recommendations,
            platform_filter=request.platform_filter,
            warehouse_filter=request.warehouse_filter,
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{report_id}", response_model=ReportMetadata)
async def get_report(
    report_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Get report details."""
    report = ReportService.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    format: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Download a generated report."""
    from fastapi.responses import FileResponse

    file_path = ReportService.get_report_file(db, report_id, format)
    if not file_path:
        raise HTTPException(status_code=404, detail=f"Report file not found")

    return FileResponse(
        path=file_path,
        media_type="application/pdf" if format == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"{report_id}.{format or 'pdf'}"
    )


@router.post("/{report_id}/email")
async def email_report(
    report_id: str,
    email_to: str = Query(...),
    db: Session = Depends(get_db),
) -> dict:
    """Email a report to recipients."""
    try:
        result = ReportService.email_report(db, report_id, email_to)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Delete a report."""
    success = ReportService.delete_report(db, report_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return {"success": True, "message": f"Report {report_id} deleted"}
