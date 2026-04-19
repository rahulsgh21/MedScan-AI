import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from app.services.pii_scrubber import get_pii_scrubber

text = """
Patient Name: John Doe
Patient Phone: 9876543210
Patient Email: john.doe@email.com
Age: 45
Sex: Male
Doctor: Dr. Ramesh
Location: Mumbai, India
Test: Hemoglobin 14.2 g/dL
"""

scrubber = get_pii_scrubber()
res = scrubber.anonymize(text)
print("--- Original ---")
print(text.strip())
print("\n--- Scrubbed ---")
print(res.strip())
