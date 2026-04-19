from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.db_models import PatientReport
from app.services.llm_client import get_llm_client
from app.schemas.lab_report import LabReport
from app.schemas.analysis import SummaryAnalysis
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    report_id: int
    message: str
    history: list[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str

CHAT_SYSTEM_PROMPT = """You are MedScan AI, a highly knowledgeable and empathetic medical assistant.
The user is asking a question about their lab report.
You have been provided with their extracted lab data and the detailed analysis we performed on it.

CRITICAL RULES:
1. Base your answer PRIMARILY on the provided report data and analysis.
2. Be conversational, empathetic, and reassuring.
3. Keep your answers concise unless the user asks for detail.
4. If a question is outside the scope of the lab report, you can answer using your general medical knowledge but add a disclaimer.
5. ALWAYS remind the user to consult their doctor for clinical decisions.
6. Return plain text/markdown, NOT JSON."""

@router.post("/chat", response_model=ChatResponse)
def chat_about_report(request: ChatRequest, db: Session = Depends(get_db)):
    """Follow-up questions on an analyzed report."""
    
    # 1. Fetch the report
    report = db.query(PatientReport).filter(PatientReport.id == request.report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    try:
        # 2. Build the context
        lab_report = LabReport.model_validate_json(report.lab_report_data)
        analysis = SummaryAnalysis.model_validate_json(report.analysis_data)
        
        # We only pass the abnormal findings and summary to save tokens, 
        # or the raw data. Since it's a small report, we can pass both.
        context = f"""
PATIENT: {lab_report.patient.name} (Age: {lab_report.patient.age}, Gender: {lab_report.patient.gender})

OVERALL SUMMARY:
{analysis.overall_summary}

ABNORMAL FINDINGS:
"""
        for finding in analysis.abnormal_findings:
            context += f"- {finding.test_name}: {finding.patient_value} {finding.unit} ({finding.status})\n"
            context += f"  Meaning: {finding.interpretation}\n"
            if finding.lifestyle_tips:
                context += f"  Tips: {', '.join(finding.lifestyle_tips)}\n"

        # Apply Sliding Window Strategy: Keep only the last 5 relevant conversational turns
        recent_history = request.history[-5:] if request.history else []
        history_text = "\n".join([f"{msg.role.upper()}: {msg.content}" for msg in recent_history])

        prompt = f"""
Context from Lab Report:
{context}

Previous Conversation (Last {len(recent_history)} turns):
{history_text if history_text else 'None'}

User Question: {request.message}
"""
        
        # 3. Call LLM using the provider-agnostic generate method
        llm = get_llm_client()
        response = llm.generate(prompt, system_instruction=CHAT_SYSTEM_PROMPT)
        
        return ChatResponse(response=response.strip())
        
    except Exception as e:
        logger.exception(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")
