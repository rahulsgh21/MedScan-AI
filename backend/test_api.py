"""Test the actual HTTP API endpoint - simulates browser upload."""
import requests
import json

print("Uploading Scanned Document.pdf to API...")
with open(r"C:\Users\rs725\Desktop\New_projects\Scanned Document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/reports/upload",
        files={"file": ("Scanned Document.pdf", f, "application/pdf")},
        timeout=120
    )

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Report ID: {data['id']}")
    print(f"Patient: {data['lab_report']['patient']['name']}")
    print(f"Tests: {len(data['lab_report']['test_results'])}")
    print(f"Findings: {len(data['analysis']['abnormal_findings'])}")
    print(f"Summary: {data['analysis']['overall_summary'][:300]}")
    print()
    print("API UPLOAD TEST PASSED!")
else:
    print(f"FAILED: {response.text[:500]}")
