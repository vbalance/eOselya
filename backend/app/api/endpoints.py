from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models import InvestmentInput
from app.services.calculation import calculate_all
from app.services.export import generate_excel_report

router = APIRouter()

@router.post("/calculate")
async def calculate_investment(input_data: InvestmentInput):
    """
    Calculate investment metrics and cashflows for all scenarios.
    """
    try:
        results = calculate_all(input_data)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export")
async def export_report(input_data: InvestmentInput):
    """
    Generate and download Excel report.
    """
    try:
        excel_file = generate_excel_report(input_data)
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=eOselya_Report.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
