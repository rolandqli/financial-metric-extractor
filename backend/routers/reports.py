from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import time
from io import BytesIO
from logging_config import logger


from services.extraction import extract_metrics

router = APIRouter(prefix="/reports")

# Set max file size to 20MB
MAX_FILE_SIZE = 20 * 1024 * 1024

async def check_pdf(file: UploadFile):
    """
    Error handling check for PDFs.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed.")
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large.")

@router.post("/process")
async def upload_pdf(files: list[UploadFile]):
    """
    Loop through PDFs and return Excel sheet

    :param files: list of PDF files to be processed
    :type files: list[UploadFile]
    """
    init_time = time.time()

    df = pd.DataFrame([])
    # Transformation map
    COLUMN_MAP = {
        "company_name": "Company Name",
        "quarter": "Quarter",
        "total_revenue": "Total revenue",
        "earnings_per_share": "Earnings per share",
        "net_income": "Net income",
        "operating_income": "Operating income",
        "gross_margin": "Gross margin",
        "operating_expenses": "Operating expenses",
        "buybacks_and_dividends": "Buybacks and dividends",
        "performance": "Performance"
    }

    # Loop through files and extract metrics. Keep adding rows to DF.
    for file in files:
        await check_pdf(file)
        start = time.time()
        data = extract_metrics(file)
        end = time.time()
        logger.info(f"Extraction for {file.filename} took {end - start:.2f} seconds")
        if df.empty:
            df = pd.DataFrame([data])
        else:
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df = df.rename(columns=COLUMN_MAP)

    # Output Excel file 
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    logger.info(f"Processed {len(files)} in {time.time() - init_time} seconds")

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=report.xlsx"},
    )
