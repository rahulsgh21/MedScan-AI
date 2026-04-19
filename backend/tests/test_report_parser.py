"""
End-to-end test: PDF → Extract → LLM Parse → Structured LabReport

This is the FULL PIPELINE test:
  1. Read a sample PDF
  2. Extract text with pdfplumber
  3. Send to Gemini for structured parsing
  4. Validate the output with Pydantic

Run with: pytest tests/test_report_parser.py -v -s
(use -s to see print output)
"""

import pytest
from pathlib import Path
from app.services.pdf_extractor import PDFExtractor
from app.services.report_parser import ReportParser
from app.schemas.lab_report import LabReport


SAMPLE_REPORT = Path(__file__).parent.parent / "sample_reports" / "sample_cbc_report.pdf"


@pytest.fixture
def extractor():
    return PDFExtractor()


@pytest.fixture
def parser():
    return ReportParser()


class TestReportParser:
    """Test the LLM-powered report parsing pipeline."""

    def test_full_pipeline_pdf_to_structured(self, extractor, parser):
        """
        THE BIG TEST: PDF → text → LLM → LabReport

        This tests the entire Phase 1+2 pipeline end-to-end.
        """
        # Step 1: Extract text from PDF
        extraction = extractor.extract(SAMPLE_REPORT)
        combined_text = extraction.combined_text

        print(f"\n{'='*60}")
        print(f"STEP 1: Extracted {len(combined_text)} chars from PDF")
        print(f"{'='*60}")

        # Step 2: Parse with LLM
        report = parser.parse(combined_text)

        print(f"\n{'='*60}")
        print(f"STEP 2: LLM parsed into LabReport")
        print(f"{'='*60}")

        # Step 3: Validate the result
        assert isinstance(report, LabReport)
        assert report.total_tests > 0, "No test results parsed!"

        # Print the parsed report
        print(f"\n--- PARSED REPORT ---")
        print(f"Patient: {report.patient.name}")
        print(f"Age/Gender: {report.patient.age} / {report.patient.gender}")
        print(f"Lab: {report.lab_name}")
        print(f"Date: {report.report_date}")
        print(f"Total Tests: {report.total_tests}")
        print(f"Abnormal: {report.abnormal_count}")

        print(f"\n--- ALL RESULTS ---")
        for r in report.test_results:
            flag = " <<<" if r.status != "Normal" else ""
            print(
                f"  {r.test_name:30s} {r.value:>10} {r.unit:>15s}  "
                f"[{r.reference_min or '?':>6} - {r.reference_max or '?':>6}]  "
                f"{r.status:>8s}{flag}"
            )

    def test_patient_info_extracted(self, extractor, parser):
        """Verify patient demographics are correctly parsed."""
        extraction = extractor.extract(SAMPLE_REPORT)
        report = parser.parse(extraction.combined_text)

        assert report.patient.name is not None, "Patient name not extracted"
        assert report.patient.age is not None, "Patient age not extracted"
        assert report.patient.gender is not None, "Patient gender not extracted"

        print(f"\nPatient: {report.patient.name}, "
              f"Age: {report.patient.age}, "
              f"Gender: {report.patient.gender}")

    def test_abnormal_results_detected(self, extractor, parser):
        """Verify that abnormal results are correctly flagged."""
        extraction = extractor.extract(SAMPLE_REPORT)
        report = parser.parse(extraction.combined_text)

        abnormal = report.abnormal_results
        assert len(abnormal) > 0, "No abnormal results detected (our sample has several!)"

        print(f"\n--- ABNORMAL RESULTS ({len(abnormal)}) ---")
        for r in abnormal:
            print(f"  {r.test_name}: {r.value} {r.unit} [{r.status}]")

        # Our sample report has these known abnormals:
        abnormal_names = [r.test_name.lower() for r in abnormal]

        # Hemoglobin should be flagged as Low (11.2, range 13-17)
        assert any("hemoglobin" in name for name in abnormal_names), \
            "Hemoglobin (11.2, clearly low) should be flagged as abnormal"

    def test_categories_assigned(self, extractor, parser):
        """Verify tests are categorized (CBC, Lipid, etc.)."""
        extraction = extractor.extract(SAMPLE_REPORT)
        report = parser.parse(extraction.combined_text)

        categories = set(r.category for r in report.test_results if r.category)
        print(f"\nCategories found: {categories}")

        # Should have at least 2 categories
        assert len(categories) >= 2, \
            f"Expected multiple categories, got: {categories}"

    def test_minimum_test_count(self, extractor, parser):
        """Our sample report has ~25 tests — verify we got most of them."""
        extraction = extractor.extract(SAMPLE_REPORT)
        report = parser.parse(extraction.combined_text)

        # We have CBC (15) + Lipid (6) + Sugar (2) + Thyroid (3) = 26 tests
        # Allow some flexibility — LLM might merge/skip a few
        assert report.total_tests >= 15, \
            f"Expected at least 15 tests, got {report.total_tests}"

        print(f"\nTotal tests parsed: {report.total_tests} (expected ~26)")
