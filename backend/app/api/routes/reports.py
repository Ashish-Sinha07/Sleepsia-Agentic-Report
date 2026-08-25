from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from pydantic import BaseModel
from io import BytesIO

from app.database import get_db
from app.services.report_service import ReportService
from app.services.comprehensive_report_service import ComprehensiveReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


class GenerateReportRequest(BaseModel):
    """Request to generate a business report."""
    report_type: str = "executive_summary"
    start_date: date
    end_date: date
    format: str = "pdf"
    include_recommendations: bool = True
    platform_filter: Optional[str] = None
    warehouse_filter: Optional[str] = None


class ComprehensiveReportRequest(BaseModel):
    """Request to generate a comprehensive report with insights and recommendations."""
    start_date: date
    end_date: date
    report_type: str = "executive_summary"


class ReportMetadata(BaseModel):
    """Metadata about a report."""
    report_id: str
    report_type: str
    created_at: str
    start_date: date
    end_date: date
    status: str
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


@router.post("")
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
    import logging
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Generating report: type={request.report_type}, format={request.format}")
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
        logger.info(f"Report generated successfully: {report.get('report_id')}")
        return report
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.post("/comprehensive/generate")
async def generate_comprehensive_report(
    request: ComprehensiveReportRequest,
    db: Session = Depends(get_db),
):
    """
    Generate a comprehensive professional report with insights and recommendations.

    This endpoint generates a high-quality PDF report that includes:
    - Executive summary
    - KPIs and key metrics
    - Platform performance analysis
    - Product profitability analysis
    - Advertising performance analysis
    - Business insights (using insight engine)
    - Strategic recommendations (using recommendation engine)
    - Professional formatting with tables and sections

    Returns: PDF file download
    """
    try:
        service = ComprehensiveReportService(db=db)

        result = service.generate_full_report(
            start_date=request.start_date,
            end_date=request.end_date,
            report_type=request.report_type,
        )

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))

        # Return PDF as download
        pdf_bytes = result.get("pdf_bytes")
        report_id = result.get("report_id")

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{report_id}.pdf"'
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comprehensive/json")
async def generate_comprehensive_report_json(
    request: ComprehensiveReportRequest,
    db: Session = Depends(get_db),
):
    """
    Generate a comprehensive report and return as JSON (for preview/processing).

    Returns: JSON with report metadata, metrics, insights, and recommendations
    """
    try:
        service = ComprehensiveReportService(db=db)

        result = service.generate_full_report(
            start_date=request.start_date,
            end_date=request.end_date,
            report_type=request.report_type,
        )

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))

        # Return JSON response (without PDF bytes)
        return {
            "report_id": result.get("report_id"),
            "start_date": result.get("start_date"),
            "end_date": result.get("end_date"),
            "metrics": result.get("metrics"),
            "insights": result.get("insights"),
            "recommendations": result.get("recommendations"),
            "generated_at": result.get("generated_at"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{report_id}")
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
    file_path = ReportService.get_report_file(db, report_id, format)
    if not file_path:
        raise HTTPException(status_code=404, detail=f"Report file not found")

    actual_format = file_path.rsplit('.', 1)[-1].lower()
    media_types = {
        "json": "application/json",
        "pdf": "application/pdf",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    return FileResponse(
        path=file_path,
        media_type=media_types.get(actual_format, "application/octet-stream"),
        filename=f"{report_id}.{actual_format}"
    )


@router.post("/{report_id}/email")
async def email_report(
    report_id: str,
    email_to: str = Query(...),
    cc: Optional[str] = Query(None),
    bcc: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> dict:
    """Email a report to recipients."""
    try:
        result = ReportService.email_report(db, report_id, email_to, cc, bcc, format)
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
