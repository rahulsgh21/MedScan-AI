"""Full end-to-end pipeline test for MedScan AI with scanned PDF."""
import sys, os
sys.path.insert(0, ".")
os.environ["PYTHONIOENCODING"] = "utf8"

# Force reload .env
from dotenv import load_dotenv
load_dotenv(override=True)

print("=" * 50)
print("MEDSCAN AI - FULL E2E TEST (Scanned PDF)")
print("=" * 50)

# PHASE 1: Extract
print("\n--- PHASE 1: PDF Extraction ---")
from app.services.pdf_extractor import PDFExtractor
extractor = PDFExtractor()
result = extractor.extract(r"C:\Users\rs725\Desktop\New_projects\Scanned Document.pdf")
print(f"  Method: {result.extraction_method}")
print(f"  Extracted: {len(result.combined_text)} chars")
assert len(result.combined_text) > 100, "FAIL: Too few chars extracted"
print("  PHASE 1: PASSED")

# PHASE 2: Parse
print("\n--- PHASE 2: LLM Parsing ---")
from app.services.report_parser import ReportParser
parser = ReportParser()
lab_report = parser.parse(result.combined_text)
print(f"  Patient: {lab_report.patient.name}")
print(f"  Lab: {lab_report.lab_name}")
print(f"  Total tests: {lab_report.total_tests}")
print(f"  Abnormal: {lab_report.abnormal_count}")
for r in lab_report.abnormal_results:
    print(f"    - {r.test_name}: {r.value} {r.unit} ({r.status})")
assert lab_report.total_tests > 0, "FAIL: No tests parsed"
print("  PHASE 2: PASSED")

# PHASE 3: Analyze
print("\n--- PHASE 3: RAG Analysis ---")
from app.services.report_analyzer import ReportAnalyzer
analyzer = ReportAnalyzer()
analysis = analyzer.analyze(lab_report)
print(f"  Findings: {len(analysis.abnormal_findings)}")
print(f"  Summary: {analysis.overall_summary[:250]}")
print("  PHASE 3: PASSED")

print("\n" + "=" * 50)
print("ALL 3 PHASES PASSED - APP IS WORKING!")
print("=" * 50)
