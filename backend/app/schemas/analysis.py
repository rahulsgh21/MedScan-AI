from pydantic import BaseModel, Field
from typing import List, Optional

class AbnormalResultAnalysis(BaseModel):
    """Analysis of a single abnormal result."""
    test_name: str
    patient_value: float
    unit: str
    status: str
    interpretation: str = Field(..., description="Plain language explanation of what this result means.")
    possible_causes: List[str] = Field(..., description="Possible lifestyle or medical causes based on the knowledge base.")
    lifestyle_tips: List[str] = Field(..., description="Actionable lifestyle and dietary tips.")

class SummaryAnalysis(BaseModel):
    """The complete RAG-augmented analysis for a patient."""
    patient_name: Optional[str]
    report_date: Optional[str]
    overall_summary: str = Field(..., description="A 2-3 sentence overall health summary.")
    abnormal_findings: List[AbnormalResultAnalysis]
    questions_for_doctor: List[str] = Field(..., description="3-4 pertinent questions the patient should ask their doctor.")
