from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Any, List
import json
from typing import Any
import tempfile
import os
import shutil
from pathlib import Path

from app.services.pdf_extractor import PDFExtractor
from app.services.report_parser import ReportParser
from app.services.report_analyzer import ReportAnalyzer
from app.schemas.lab_report import LabReport
from app.schemas.analysis import SummaryAnalysis
from app.core.db import get_db
from app.core.db_models import PatientReport
from sqlalchemy.orm import Session
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Instantiate services
# In a true production app, we might use FastAPI dependency injection
pdf_extractor = PDFExtractor()
report_parser = ReportParser()
report_analyzer = ReportAnalyzer()


class AnalysisResponse(BaseModel):
    """Response model for the full analysis endpoint."""
    id: int
    message: str
    lab_report: LabReport
    analysis: SummaryAnalysis

class ReportHistoryItem(BaseModel):
    id: int
    patient_name: str | None
    report_date: str | None
    created_at: str
    
    class Config:
        from_attributes = True

@router.post("/reports/upload", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def upload_and_analyze_report(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    1. Uploads the PDF.
    2. Extracts text/tables.
    3. Parses into structured lab report.
    4. Analyzes abnormal results using Hybrid RAG.
    5. Returns the structured lab report and the plain-English analysis.
    """
    logger.info(f"Received file upload: {file.filename}")
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files are supported."
        )

    # Save uploaded file to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = Path(tmp_file.name)
            
        logger.debug(f"Saved uploaded file to temp path: {tmp_path}")
        
        # Step 1: Extract PDF
        logger.info("Executing Phase 1: PDF Extraction")
        extraction_result = pdf_extractor.extract(tmp_path)
        if not extraction_result.combined_text.strip():
            raise ValueError("Could not extract any text from the PDF.")
        # Step 1.5: PII Scrubbing (Compliance Guardrail)
        from app.services.pii_scrubber import get_pii_scrubber
        logger.info("Executing Phase 1.5: PII Scrubbing (Presidio)")
        pii_scrubber = get_pii_scrubber()
        sanitized_text = pii_scrubber.anonymize(extraction_result.combined_text)
            
        # Step 2: Parse with LLM
        logger.info("Executing Phase 2: LLM Parsing")
        lab_report = report_parser.parse(sanitized_text)
        
        # Step 3: Analyze with RAG
        logger.info("Executing Phase 5: RAG-Augmented Analysis")
        analysis = report_analyzer.analyze(lab_report)
        
        # Step 4: Save to Database
        db_report = PatientReport(
            patient_name=lab_report.patient.name or "Unknown Patient",
            report_date=lab_report.report_date or "Unknown Date",
            lab_report_data=lab_report.model_dump_json(),
            analysis_data=analysis.model_dump_json()
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        
        logger.info(f"Analysis pipeline complete. Saved to DB with ID: {db_report.id}")
        
        return AnalysisResponse(
            id=db_report.id,
            message="Report analyzed successfully.",
            lab_report=lab_report,
            analysis=analysis
        )
        
    except ValueError as ve:
        error_msg = str(ve)
        logger.error(f"Validation error during processing: {ve}")

        # Detect non-medical documents (LLM returns null for patient/test_results)
        if "PatientInfo" in error_msg or "test_results" in error_msg:
            detail = (
                "This file does not appear to be a medical lab report. "
                "Please upload a diagnostic lab report (e.g., blood test, CBC, lipid profile)."
            )
        elif "validation" in error_msg.lower():
            detail = (
                "We couldn't parse this report. The format may be unsupported. "
                "Please try a different lab report PDF."
            )
        else:
            detail = error_msg

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
    except Exception as e:
        logger.exception(f"Unexpected error during processing: {e}")
        error_msg = str(e)
        # Give user a clear message for known Gemini API issues
        if "503" in error_msg or "UNAVAILABLE" in error_msg or "429" in error_msg:
            detail = "The AI model (Gemini) is temporarily overloaded. Please try again in 30 seconds."
        else:
            detail = f"An error occurred while processing the report: {error_msg[:200]}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE if ("503" in error_msg or "UNAVAILABLE" in error_msg) else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
    finally:
        # Clean up temp file
        if 'tmp_path' in locals() and tmp_path.exists():
            try:
                os.remove(tmp_path)
                logger.debug(f"Deleted temp file: {tmp_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {tmp_path}: {e}")

@router.get("/reports", response_model=List[ReportHistoryItem])
def get_reports_history(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Get history of all analyzed reports."""
    reports = db.query(PatientReport).order_by(PatientReport.created_at.desc()).offset(skip).limit(limit).all()
    # Convert datetime to string for easy serialization
    for r in reports:
        r.created_at = r.created_at.isoformat()
    return reports

@router.get("/reports/{report_id}", response_model=AnalysisResponse)
def get_report_by_id(report_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific parsed report and its analysis by ID."""
    report = db.query(PatientReport).filter(PatientReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # Reconstruct Pydantic models from JSON strings
    lab_report = LabReport.model_validate_json(report.lab_report_data)
    analysis = SummaryAnalysis.model_validate_json(report.analysis_data)
    
    return AnalysisResponse(
        id=report.id,
        message="Retrieved successfully.",
        lab_report=lab_report,
        analysis=analysis
    )
