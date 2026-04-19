"""
PDF Extractor Service — Extracts raw text and table data from lab report PDFs.

This is the FIRST stage of the pipeline:
  PDF file → pdfplumber → raw text + table data → ready for LLM parsing
  If pdfplumber returns no text (scanned/image PDF), we fall back to
  Gemini Vision to OCR each page image.

Design Decisions:
  1. We use pdfplumber (not camelot) because lab reports often have
     borderless tables that camelot can't handle.
  2. We extract BOTH raw text AND structured tables, then combine them.
     This gives the LLM the best chance of understanding the layout.
  3. We DON'T try to parse the table structure ourselves with regex.
     That's brittle. We let the LLM do semantic parsing in the next step.
  4. For scanned/image PDFs, we convert pages to PNG using PyMuPDF (fitz)
     and send them to Gemini Vision. This avoids Tesseract OCR system deps
     and gives better accuracy on complex lab report layouts.

Interview talking point:
  "We decouple extraction from parsing. pdfplumber handles the PDF layer,
   then the LLM handles the semantic understanding. For scanned PDFs,
   we use Gemini's multimodal vision to read page images directly —
   no Tesseract, no system dependencies."
"""

from pathlib import Path
from dataclasses import dataclass
import pdfplumber
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Minimum characters threshold — if pdfplumber extracts less than this,
# we assume it's a scanned PDF and fall back to vision OCR.
MIN_TEXT_THRESHOLD = 50


@dataclass
class ExtractedPage:
    """Data extracted from a single PDF page."""
    page_number: int
    text: str
    tables: list[list[list[str | None]]]  # list of tables, each table is a list of rows


@dataclass
class ExtractionResult:
    """Complete extraction result from a PDF file."""
    filename: str
    total_pages: int
    pages: list[ExtractedPage]
    raw_text: str  # combined text from all pages
    raw_tables_text: str  # tables formatted as text for LLM
    extraction_method: str  # 'pdfplumber' or 'gemini_vision'

    @property
    def combined_text(self) -> str:
        """
        Combine raw text and table text into a single string for LLM parsing.
        This gives the LLM maximum context to understand the report.
        """
        parts = [self.raw_text]
        if self.raw_tables_text:
            parts.append("\n\n--- EXTRACTED TABLES ---\n")
            parts.append(self.raw_tables_text)
        return "\n".join(parts)


class PDFExtractor:
    """
    Extracts text and table data from lab report PDFs.

    Strategy:
      1. Try pdfplumber first (fast, works for digitally generated PDFs).
      2. If pdfplumber returns very little text, assume it's a scanned
         image PDF and fall back to Gemini Vision OCR.

    Usage:
        extractor = PDFExtractor()
        result = extractor.extract("path/to/report.pdf")
        print(result.combined_text)  # send this to LLM for parsing
    """

    def extract(self, file_path: str | Path) -> ExtractionResult:
        """
        Extract all text and tables from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            ExtractionResult with raw text, tables, and combined output

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file is not a valid PDF or is empty
        """
        file_path = Path(file_path)

        if file_path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file, got: {file_path.suffix}")

        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        logger.info(f"Extracting PDF: {file_path.name}")

        # Step 1: Try pdfplumber (fast, digital PDFs)
        result = self._extract_with_pdfplumber(file_path)

        # Step 2: Check if we got meaningful text
        total_text_len = len(result.raw_text.strip()) + len(result.raw_tables_text.strip())

        if total_text_len >= MIN_TEXT_THRESHOLD:
            logger.info(f"pdfplumber extracted {total_text_len} chars — using digital extraction.")
            return result

        # Step 3: pdfplumber got nothing useful → fall back to Gemini Vision
        logger.warning(
            f"pdfplumber extracted only {total_text_len} chars — "
            f"falling back to Gemini Vision OCR for scanned PDF."
        )
        return self._extract_with_vision_ocr(file_path)

    def _extract_with_pdfplumber(self, file_path: Path) -> ExtractionResult:
        """Fast extraction for digitally-generated PDFs using pdfplumber."""
        pages: list[ExtractedPage] = []
        all_text_parts: list[str] = []
        all_tables_text_parts: list[str] = []
        total_pages = 0

        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"PDF has {total_pages} page(s)")

                for i, page in enumerate(pdf.pages):
                    page_num = i + 1

                    # Extract raw text
                    text = page.extract_text() or ""
                    all_text_parts.append(text)

                    # Extract tables
                    tables = page.extract_tables() or []
                    page_tables: list[list[list[str | None]]] = []

                    for table_idx, table in enumerate(tables):
                        page_tables.append(table)
                        table_text = self._format_table_as_text(
                            table, page_num, table_idx + 1
                        )
                        all_tables_text_parts.append(table_text)

                    pages.append(
                        ExtractedPage(
                            page_number=page_num,
                            text=text,
                            tables=page_tables,
                        )
                    )

                    logger.debug(
                        f"Page {page_num}: {len(text)} chars, {len(tables)} table(s)"
                    )

        except Exception as e:
            logger.error(f"Failed to extract PDF with pdfplumber: {e}")
            raise ValueError(f"Failed to process PDF file: {e}")

        raw_text = "\n\n".join(all_text_parts).strip()
        raw_tables_text = "\n\n".join(all_tables_text_parts).strip()

        result = ExtractionResult(
            filename=file_path.name,
            total_pages=total_pages,
            pages=pages,
            raw_text=raw_text,
            raw_tables_text=raw_tables_text,
            extraction_method="pdfplumber",
        )

        logger.info(
            f"pdfplumber extraction: {len(raw_text)} chars text, "
            f"{sum(len(p.tables) for p in pages)} table(s)"
        )

        return result

    def _extract_with_vision_ocr(self, file_path: Path) -> ExtractionResult:
        """
        Fallback extraction for scanned/image PDFs using Vision LLMs.

        Strategy:
          1. Convert each PDF page to a PNG image (using PyMuPDF/fitz).
          2. Try Groq Vision (Llama 3.2 90B) first — free, reliable.
          3. If Groq fails, fall back to Gemini Vision.
          4. Combine all page extractions into a single ExtractionResult.
        """
        import fitz  # PyMuPDF
        import base64
        from app.core.config import settings

        logger.info("Starting Vision OCR extraction for scanned PDF...")

        # Open PDF with PyMuPDF and convert pages to images
        doc = fitz.open(str(file_path))
        total_pages = len(doc)
        all_text_parts: list[str] = []
        pages: list[ExtractedPage] = []

        vision_prompt = (
            "You are an expert medical document reader. "
            "This image is a page from an Indian diagnostic lab report. "
            "Extract ALL text content from this image exactly as it appears, "
            "preserving the structure of tables. "
            "For any tables, format them as pipe-separated values like this:\n"
            "Test Name | Result | Unit | Reference Range | Status\n"
            "Hemoglobin | 12.5 | g/dL | 13.0 - 17.0 | Low\n\n"
            "Include patient information, lab name, date, and ALL test results. "
            "Return ONLY the extracted text, nothing else."
        )

        for i in range(total_pages):
            page_num = i + 1
            logger.debug(f"Vision OCR: Processing page {page_num}/{total_pages}")

            # Render page at 2x zoom, then convert to JPEG to keep size manageable.
            # Scanned PDFs produce massive PNGs (11MB+) but JPEG at quality 85
            # is only ~1.3MB — well within Groq's API limits, and still perfectly
            # readable for Vision OCR.
            page = doc[i]
            mat = fitz.Matrix(2, 2)  # 2x zoom ≈ 150 DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to JPEG using Pillow for massive size reduction
            from PIL import Image
            import io
            png_img = Image.open(io.BytesIO(pix.tobytes("png")))
            jpg_buffer = io.BytesIO()
            png_img.save(jpg_buffer, format="JPEG", quality=85)
            img_bytes = jpg_buffer.getvalue()
            img_mime = "image/jpeg"
            logger.debug(f"Page {page_num} image: {len(img_bytes)//1024}KB JPEG")

            # Try Groq Vision first, then Gemini as fallback
            page_text = self._ocr_with_groq(img_bytes, vision_prompt, settings)
            
            if not page_text:
                logger.warning(f"Groq Vision failed on page {page_num}, trying Gemini...")
                page_text = self._ocr_with_gemini(img_bytes, vision_prompt, settings)

            if page_text:
                logger.debug(f"Vision OCR page {page_num}: extracted {len(page_text)} chars")
            else:
                logger.error(f"All Vision OCR methods failed on page {page_num}")

            all_text_parts.append(page_text)
            pages.append(
                ExtractedPage(
                    page_number=page_num,
                    text=page_text,
                    tables=[],  # Vision extracts tables inline as text
                )
            )

        doc.close()

        raw_text = "\n\n".join(all_text_parts).strip()

        if not raw_text:
            raise ValueError(
                "Could not extract any text from this PDF, even with Vision OCR. "
                "The file may be corrupted or contain no readable content."
            )

        result = ExtractionResult(
            filename=file_path.name,
            total_pages=total_pages,
            pages=pages,
            raw_text=raw_text,
            raw_tables_text="",  # Vision puts tables inline in raw_text
            extraction_method="vision_ocr",
        )

        logger.info(
            f"Vision OCR extraction complete: {len(raw_text)} chars "
            f"from {total_pages} page(s)"
        )

        return result

    @staticmethod
    def _ocr_with_groq(img_bytes: bytes, prompt: str, settings) -> str:
        """OCR a single page image using Groq Vision (Llama 3.2 90B)."""
        try:
            import base64
            from groq import Groq

            if not settings.groq_api_key:
                return ""

            client = Groq(api_key=settings.groq_api_key)
            b64_image = base64.b64encode(img_bytes).decode("utf-8")

            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{b64_image}"
                                },
                            },
                        ],
                    }
                ],
                temperature=0.1,
                max_tokens=4096,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"Groq Vision OCR error: {e}")
            return ""

    @staticmethod
    def _ocr_with_gemini(img_bytes: bytes, prompt: str, settings) -> str:
        """OCR a single page image using Gemini Vision (fallback)."""
        try:
            from google import genai
            from google.genai import types

            if not settings.gemini_api_key:
                return ""

            client = genai.Client(api_key=settings.gemini_api_key)
            image_part = types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")

            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=[prompt, image_part],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=8192,
                ),
            )
            return response.text or ""

        except Exception as e:
            logger.error(f"Gemini Vision OCR error: {e}")
            return ""

    def extract_from_bytes(self, pdf_bytes: bytes, filename: str = "upload.pdf") -> ExtractionResult:
        """
        Extract from in-memory PDF bytes (for API uploads).
        Writes to a temp file, then delegates to self.extract().

        Args:
            pdf_bytes: Raw bytes of the PDF file
            filename: Original filename for logging

        Returns:
            ExtractionResult
        """
        import tempfile
        import os

        logger.info(f"Extracting PDF from bytes: {filename} ({len(pdf_bytes)} bytes)")

        # Write bytes to temp file so both pdfplumber and fitz can read it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = Path(tmp.name)

        try:
            result = self.extract(tmp_path)
            result.filename = filename  # Use original name
            return result
        finally:
            if tmp_path.exists():
                os.remove(tmp_path)

    @staticmethod
    def _format_table_as_text(
        table: list[list[str | None]], page_num: int, table_idx: int
    ) -> str:
        """
        Format an extracted table as human-readable text for LLM consumption.

        Instead of raw list-of-lists, we format it as a pipe-separated table
        that the LLM can easily understand.

        Example output:
            [Page 1, Table 1]
            Test Name | Result | Unit | Reference Range
            Hemoglobin | 12.5 | g/dL | 13.0 - 17.0
        """
        lines = [f"[Page {page_num}, Table {table_idx}]"]
        for row in table:
            # Replace None with empty string, strip whitespace
            cleaned_row = [
                (cell.strip() if cell else "") for cell in row
            ]
            lines.append(" | ".join(cleaned_row))
        return "\n".join(lines)
