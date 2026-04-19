"""
Test suite for pdf_extractor service.

Tests the foundational PDF extraction pipeline.
Run with: pytest tests/test_pdf_extractor.py -v
"""

import pytest
from pathlib import Path
from app.services.pdf_extractor import PDFExtractor, ExtractionResult


# Path to our sample report
SAMPLE_REPORT = Path(__file__).parent.parent / "sample_reports" / "sample_cbc_report.pdf"


@pytest.fixture
def extractor():
    """Create a PDFExtractor instance."""
    return PDFExtractor()


class TestPDFExtractor:
    """Test the PDF extraction pipeline."""

    def test_extract_sample_report_succeeds(self, extractor):
        """Basic test: can we extract text from our sample PDF?"""
        result = extractor.extract(SAMPLE_REPORT)
        assert isinstance(result, ExtractionResult)
        assert result.total_pages >= 1
        assert len(result.raw_text) > 0
        print(f"\n✅ Extracted {len(result.raw_text)} chars from {result.filename}")

    def test_extract_finds_patient_info(self, extractor):
        """Can we find patient demographic info in the extracted text?"""
        result = extractor.extract(SAMPLE_REPORT)
        text = result.combined_text.lower()

        # These should all be present in our sample report
        assert "rahul sharma" in text, "Patient name not found"
        assert "28" in result.combined_text, "Patient age not found"
        assert "male" in text, "Patient gender not found"
        print("\n✅ Patient info found in extracted text")

    def test_extract_finds_test_results(self, extractor):
        """Can we find actual biomarker names in the extracted text?"""
        result = extractor.extract(SAMPLE_REPORT)
        text = result.combined_text.lower()

        # Key biomarkers that MUST be present
        expected_biomarkers = [
            "hemoglobin",
            "cholesterol",
            "hba1c",
            "tsh",
            "platelet",
        ]

        for biomarker in expected_biomarkers:
            assert biomarker in text, f"Biomarker '{biomarker}' not found in extracted text"

        print(f"\n✅ All {len(expected_biomarkers)} key biomarkers found")

    def test_extract_finds_tables(self, extractor):
        """Does pdfplumber detect the table structures?"""
        result = extractor.extract(SAMPLE_REPORT)

        total_tables = sum(len(p.tables) for p in result.pages)
        assert total_tables > 0, "No tables detected in PDF"
        print(f"\n✅ Found {total_tables} table(s) in PDF")

    def test_extract_finds_reference_ranges(self, extractor):
        """Can we find reference range numbers in the extracted data?"""
        result = extractor.extract(SAMPLE_REPORT)
        text = result.combined_text

        # These specific reference values should be present
        assert "13.0" in text, "Hemoglobin reference min not found"
        assert "17.0" in text, "Hemoglobin reference max not found"
        assert "200" in text, "Cholesterol reference not found"
        print("\n✅ Reference ranges found in extracted text")

    def test_extract_file_not_found(self, extractor):
        """Should raise FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            extractor.extract("nonexistent_file.pdf")

    def test_extract_non_pdf(self, extractor):
        """Should raise ValueError for non-PDF files."""
        with pytest.raises(ValueError, match="Expected a PDF"):
            extractor.extract("test.txt")

    def test_combined_text_not_empty(self, extractor):
        """The combined text (for LLM input) should contain meaningful data."""
        result = extractor.extract(SAMPLE_REPORT)
        combined = result.combined_text

        # Should be substantial (a lab report has lots of data)
        assert len(combined) > 200, f"Combined text too short: {len(combined)} chars"

        # Print first 500 chars for manual inspection
        print(f"\n📄 Combined text preview (first 500 chars):\n{combined[:500]}")
