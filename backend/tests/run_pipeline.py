"""
Test the final analysis service (Phase 5).
This tests the full stack: PDF -> Extractor -> Parser -> Analyzer (which calls RAG).
"""

from pathlib import Path
from app.services.pdf_extractor import PDFExtractor
from app.services.report_parser import ReportParser
from app.services.report_analyzer import ReportAnalyzer

SAMPLE_REPORT = Path(__file__).parent.parent / "sample_reports" / "sample_cbc_report.pdf"

def test_full_analysis_pipeline():
    """
    RUN THIS MANUALLY to see the final output.
    """
    print("\n\n" + "="*80)
    print("STARTING FULL MEDSCAN AI PIPELINE")
    print("="*80)
    
    # 1. Extract
    print("\n1. EXTRACTING PDF...")
    extractor = PDFExtractor()
    extraction = extractor.extract(SAMPLE_REPORT)
    print(f"   Done. Extracted {len(extraction.combined_text)} characters.")
    
    # 2. Parse
    print("\n2. PARSING WITH LLM (Structured JSON)...")
    parser = ReportParser()
    lab_report = parser.parse(extraction.combined_text)
    print(f"   Done. Found {lab_report.total_tests} tests. {lab_report.abnormal_count} abnormal.")
    
    # 3. Analyze
    print("\n3. ANALYZING WITH RAG ENGINE...")
    analyzer = ReportAnalyzer()
    analysis = analyzer.analyze(lab_report)
    
    # 4. Display Results beautifully
    print("\n" + "="*80)
    print("FINAL MEDSCAN AI ANALYSIS")
    print("="*80)
    print(f"Patient: {analysis.patient_name}")
    print(f"Date: {analysis.report_date}")
    print(f"\nOVERALL SUMMARY:")
    print(f"{analysis.overall_summary}")
    
    print("\nABNORMAL FINDINGS EXPLAINED:")
    for finding in analysis.abnormal_findings:
        print(f"\n>> {finding.test_name}: {finding.patient_value} {finding.unit} ({finding.status})")
        print(f"   Interpretation: {finding.interpretation}")
        if finding.possible_causes:
            print(f"   Possible Causes: {', '.join(finding.possible_causes)}")
        if finding.lifestyle_tips:
            print(f"   Lifestyle Tips:  {', '.join(finding.lifestyle_tips)}")
            
    print("\nQUESTIONS FOR YOUR DOCTOR:")
    for q in analysis.questions_for_doctor:
        print(f" - {q}")
        
    print("\n" + "="*80)

if __name__ == "__main__":
    test_full_analysis_pipeline()
