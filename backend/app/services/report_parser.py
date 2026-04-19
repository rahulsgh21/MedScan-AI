"""
Report Parser — Converts raw PDF text into structured LabReport data using LLM.

This is the KEY INNOVATION of the project:
  Instead of writing brittle regex/rules for each lab format,
  we use an LLM to semantically parse the report.

Pipeline:
  1. PDFExtractor gives us raw text + tables
  2. This service sends that text to the LLM with a carefully crafted prompt
  3. The LLM returns structured JSON
  4. We validate the JSON against our Pydantic LabReport schema

Why LLM instead of regex?
  - Lal PathLabs format ≠ Apollo format ≠ Thyrocare format
  - Regex breaks on every new format
  - LLM handles format variability gracefully
  - The prompt engineering IS the parsing logic

Interview talking point:
  "We use the LLM as a semantic parser, not just a chatbot.
   The prompt is engineered to extract structured data from
   unstructured text, with Pydantic validation as a safety net."
"""

from app.schemas.lab_report import LabReport, TestResult, PatientInfo
from app.services.llm_client import get_llm_client
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ── The Parsing Prompt ─────────────────────────────────────────
# This prompt is the most critical piece of the entire application.
# It tells the LLM EXACTLY what to extract and in what format.

SYSTEM_INSTRUCTION = """You are a medical lab report parser. Your job is to extract 
structured data from laboratory test reports. You must be precise and accurate.

IMPORTANT RULES:
1. Extract EVERY test result from the report, not just abnormal ones.
2. For numeric values with commas (like "2,45,000"), remove commas and convert to a number (245000).
3. For reference ranges like "< 200", set reference_min to null and reference_max to 200.
4. For reference ranges like "> 40", set reference_min to 40 and reference_max to null.
5. For reference ranges like "13.0 - 17.0", set reference_min to 13.0 and reference_max to 17.0.
6. Determine status by comparing value to reference range:
   - "Normal" if within range
   - "Low" if below reference_min
   - "High" if above reference_max
   - "Critical" if extremely out of range (>2x the normal limit)
7. For categories, use: "CBC", "Lipid Profile", "Blood Sugar", "Thyroid", "Liver Function", 
   "Kidney Function", "Iron Studies", "Vitamin", or "Other".
8. If patient info is not found, use null for those fields.
9. Return ONLY valid JSON, no markdown formatting, no explanation."""

PARSE_PROMPT_TEMPLATE = """Parse the following lab report text into structured JSON.

Return a JSON object with this EXACT structure:
{{
  "patient": {{
    "name": "string or null",
    "age": number or null,
    "gender": "Male" or "Female" or "Other" or null,
    "patient_id": "string or null"
  }},
  "lab_name": "string or null",
  "report_date": "string in YYYY-MM-DD format or null",
  "test_results": [
    {{
      "test_name": "string",
      "value": number,
      "unit": "string",
      "reference_min": number or null,
      "reference_max": number or null,
      "status": "Normal" or "Low" or "High" or "Critical",
      "category": "string"
    }}
  ]
}}

--- LAB REPORT TEXT ---
{report_text}
--- END OF REPORT ---

Return ONLY the JSON object. No markdown, no explanations."""


class ReportParser:
    """
    Parses raw lab report text into structured LabReport using LLM.

    Usage:
        parser = ReportParser()
        lab_report = parser.parse(extracted_text)
        print(lab_report.abnormal_results)  # typed, validated data
    """

    def __init__(self):
        self.llm = get_llm_client()

    def parse(self, report_text: str) -> LabReport:
        """
        Parse raw report text into a validated LabReport.

        Args:
            report_text: Raw text from PDFExtractor.combined_text

        Returns:
            LabReport: Fully validated, structured report data

        Raises:
            ValueError: If LLM returns invalid/unparseable data
        """
        logger.info(f"Parsing report text ({len(report_text)} chars) with LLM...")

        # Build the prompt with the actual report text
        prompt = PARSE_PROMPT_TEMPLATE.format(report_text=report_text)

        # Call LLM to get structured JSON
        raw_json = self.llm.generate_json(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION,
            response_schema=LabReport
        )

        logger.debug(f"LLM returned JSON with {len(raw_json.get('test_results', []))} results")

        # ── Normalize qualitative statuses ──────────────────────────
        # Some tests (antibody/serology) use statuses like "Non-Reactive",
        # "Negative", "Positive", "Reactive" that don't match our schema.
        # Map them to our allowed values before Pydantic validation.
        STATUS_MAP = {
            "non-reactive": "Normal",
            "negative": "Normal",
            "reactive": "High",
            "positive": "High",
            "borderline": "High",
            "detected": "High",
            "not detected": "Normal",
            "within normal limits": "Normal",
            "abnormal": "High",
        }
        for test in raw_json.get("test_results", []):
            raw_status = test.get("status", "")
            normalized = STATUS_MAP.get(raw_status.lower().strip())
            if normalized:
                logger.debug(
                    f"Normalized status for {test.get('test_name')}: "
                    f"'{raw_status}' -> '{normalized}'"
                )
                test["status"] = normalized

            # Normalize null units to empty string (ratios, antibody tests)
            if test.get("unit") is None:
                test["unit"] = ""

        # Validate through Pydantic
        try:
            lab_report = LabReport(**raw_json)
        except Exception as e:
            logger.error(f"Pydantic validation failed: {e}")
            logger.debug(f"Raw JSON: {raw_json}")
            raise ValueError(
                f"LLM output failed validation: {e}. "
                f"This may be a transient issue — try again."
            )

        # Post-validation: sanity check the results
        self._validate_results(lab_report)

        logger.info(
            f"Parsed report: {lab_report.total_tests} tests, "
            f"{lab_report.abnormal_count} abnormal"
        )

        return lab_report

    def _validate_results(self, report: LabReport):
        """
        Additional validation beyond Pydantic schema.
        Catches logical errors the schema can't express.
        """
        for result in report.test_results:
            # Check that status matches the actual values
            if result.reference_min is not None and result.reference_max is not None:
                if result.value < result.reference_min and result.status == "Normal":
                    logger.warning(
                        f"Status mismatch for {result.test_name}: "
                        f"value {result.value} < min {result.reference_min} but status is Normal"
                    )
                    result.status = "Low"
                elif result.value > result.reference_max and result.status == "Normal":
                    logger.warning(
                        f"Status mismatch for {result.test_name}: "
                        f"value {result.value} > max {result.reference_max} but status is Normal"
                    )
                    result.status = "High"

            # Validate units aren't empty
            if not result.unit and result.test_name not in [
                "Total Cholesterol/HDL Ratio",
                "A/G Ratio",
            ]:
                logger.warning(f"Missing unit for {result.test_name}")
