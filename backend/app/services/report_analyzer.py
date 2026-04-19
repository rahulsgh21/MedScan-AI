"""
Report Analyzer Service.

This service acts as the orchestrator:
1. It takes a structured LabReport.
2. Identifies abnormal tests.
3. Queries the Hybrid RAG Engine for each abnormal test to get medical context.
4. Uses the LLM to generate a patient-friendly summary grounded ONLY in the retrieved context.
"""

from app.schemas.lab_report import LabReport
from app.schemas.analysis import SummaryAnalysis, AbnormalResultAnalysis
from app.services.llm_client import get_llm_client
from app.services.rag_engine import get_rag_engine
from app.utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_INSTRUCTION = """You are an empathetic, highly knowledgeable clinical AI assistant. 
Your goal is to explain laboratory test results to a patient in plain, accessible language.

CRITICAL RULES:
1. You MUST base your explanations and lifestyle tips ONLY on the provided "Medical Context". 
2. Do NOT invent or hallucinate medical advice. If the context doesn't mention it, don't invent it.
3. Be reassuring. Emphasize that lab tests are just one piece of the puzzle and they should consult their doctor.
4. Keep explanations EXTREMELY concise, strictly 1 sentence per finding.
5. Provide a maximum of 2 possible causes and 2 actionable lifestyle/dietary tips per finding.
6. Return your analysis strictly in the requested JSON format."""

ANALYSIS_PROMPT_TEMPLATE = """Patient Name: {patient_name}
Age/Gender: {patient_age} / {patient_gender}

Below is a list of abnormal lab results, along with retrieved Medical Context for each.
Please analyze these results and provide a structured JSON response.

{abnormal_results_text}

---
Return ONLY a valid JSON object matching this schema:
{{
  "patient_name": "string",
  "report_date": "string",
  "overall_summary": "A 2-3 sentence overview of their health based on these results.",
  "abnormal_findings": [
    {{
      "test_name": "string",
      "patient_value": number,
      "unit": "string",
      "status": "string (e.g., High, Low)",
      "interpretation": "Plain language explanation",
      "possible_causes": ["Cause 1", "Cause 2"],
      "lifestyle_tips": ["Tip 1", "Tip 2"]
    }}
  ],
  "questions_for_doctor": [
    "Question 1",
    "Question 2"
  ]
}}
"""

class ReportAnalyzer:
    """Combines structured lab data, RAG context, and LLM reasoning."""

    def __init__(self):
        self.llm = get_llm_client()
        self.rag = get_rag_engine()

    def analyze(self, lab_report: LabReport) -> SummaryAnalysis:
        """
        Perform RAG-augmented analysis on a LabReport.
        """
        abnormal_tests = lab_report.abnormal_results
        
        if not abnormal_tests:
            logger.info("No abnormal tests found. Skipping deep analysis.")
            # We could return a "Everything looks great!" summary here, but for now:
            return SummaryAnalysis(
                patient_name=lab_report.patient.name,
                report_date=lab_report.report_date,
                overall_summary="Great news! All extracted test results are within normal reference ranges.",
                abnormal_findings=[],
                questions_for_doctor=["When should I schedule my next routine checkup?"]
            )

        logger.info(f"Analyzing {len(abnormal_tests)} abnormal results via RAG...")
        
        # 1. Gather Context via Hybrid Search
        abnormal_results_text = ""
        for test in abnormal_tests:
            logger.debug(f"Retrieving context for: {test.test_name}")
            
            # Formulate a targeted query for the RAG engine
            query = f"What causes {test.status} {test.test_name} and what are the lifestyle recommendations?"
            rag_results = self.rag.hybrid_search(query, top_k=2)
            
            context_text = "\n".join([doc["content"] for doc in rag_results])
            
            abnormal_results_text += f"--- {test.test_name} ---\n"
            abnormal_results_text += f"Result: {test.value} {test.unit} (Status: {test.status})\n"
            abnormal_results_text += f"Reference Range: {test.reference_min} - {test.reference_max}\n"
            abnormal_results_text += f"Medical Context:\n{context_text}\n\n"

        # 2. Build the LLM prompt
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            patient_name=lab_report.patient.name or "Unknown",
            patient_age=lab_report.patient.age or "Unknown",
            patient_gender=lab_report.patient.gender or "Unknown",
            abnormal_results_text=abnormal_results_text
        )

        # 3. Call the LLM
        raw_json = self.llm.generate_json(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION,
            response_schema=SummaryAnalysis
        )

        # 4. Validate output with Pydantic
        analysis = SummaryAnalysis(**raw_json)
        logger.info("Analysis complete and validated.")
        
        return analysis
