"""
Pydantic schemas for lab report data.

These models define the STRUCTURED OUTPUT that our LLM must produce.
This is a core design decision:
  - Raw LLM output is unpredictable text
  - Pydantic models FORCE the output into validated, typed JSON
  - If the LLM returns bad data, Pydantic catches it immediately

Interview talking point: "We use Pydantic to validate LLM output,
turning unreliable text generation into type-safe structured data."
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import date


class TestResult(BaseModel):
    """
    A single biomarker test result extracted from a lab report.

    Example:
        test_name: "Hemoglobin"
        value: 12.5
        unit: "g/dL"
        reference_min: 13.0
        reference_max: 17.0
        status: "Low"
    """

    test_name: str = Field(
        description="Name of the test, e.g., 'Hemoglobin', 'Total Cholesterol'"
    )
    value: float = Field(
        description="The numeric result value"
    )
    unit: str = Field(
        default="",
        description="Unit of measurement, e.g., 'g/dL', 'mg/dL', 'cells/cumm'"
    )
    reference_min: Optional[float] = Field(
        default=None,
        description="Lower bound of the normal reference range"
    )
    reference_max: Optional[float] = Field(
        default=None,
        description="Upper bound of the normal reference range"
    )
    status: Literal["Normal", "Low", "High", "Critical"] = Field(
        description="Status based on reference range comparison"
    )
    category: Optional[str] = Field(
        default=None,
        description="Test category, e.g., 'CBC', 'Lipid Profile', 'Liver Function'"
    )


class PatientInfo(BaseModel):
    """Patient demographic information from the report header."""

    name: Optional[str] = Field(default=None, description="Patient name")
    age: Optional[int] = Field(default=None, description="Patient age in years")
    gender: Optional[Literal["Male", "Female", "Other"]] = Field(
        default=None, description="Patient gender"
    )
    patient_id: Optional[str] = Field(
        default=None, description="Patient/Sample ID from the lab"
    )


class LabReport(BaseModel):
    """
    Complete parsed lab report — the output of our PDF → LLM pipeline.

    This is what the report_parser service produces:
    1. pdfplumber extracts raw text from PDF
    2. LLM parses raw text into THIS structure
    3. Pydantic validates every field
    """

    patient: PatientInfo = Field(description="Patient demographics")
    lab_name: Optional[str] = Field(
        default=None, description="Name of the diagnostic lab"
    )
    report_date: Optional[str] = Field(
        default=None, description="Date of the report (YYYY-MM-DD if possible)"
    )
    test_results: list[TestResult] = Field(
        description="List of all test results in the report"
    )

    @property
    def abnormal_results(self) -> list[TestResult]:
        """Get only the abnormal (non-Normal) test results."""
        return [r for r in self.test_results if r.status != "Normal"]

    @property
    def total_tests(self) -> int:
        """Total number of tests in the report."""
        return len(self.test_results)

    @property
    def abnormal_count(self) -> int:
        """Count of abnormal results."""
        return len(self.abnormal_results)
