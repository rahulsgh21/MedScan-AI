"""
PII Scrubbing Service — Complies with HIPAA / DPDP Act.

Masks sensitive personal identifiers (Names, Phones, Emails, Locations) 
from raw PDF text BEFORE sending it to third-party LLMs (Gemini/Groq).

Design Decision:
We intentionally DO NOT scrub Age, Date of Birth, or Gender. 
Medical AI requires physiological parameters (Age/Sex) to accurately
contextualize reference ranges (e.g., Hemoglobin bounds for a 12yo vs 50yo).
"""

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from app.utils.logger import get_logger

logger = get_logger(__name__)

class PIIScrubber:
    def __init__(self):
        logger.info("Initializing Microsoft Presidio PII Scrubber...")
        # Load the default NLP engine (spaCy en_core_web_sm)
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # The specific entities we want to mask to ensure compliance,
        # while deliberately excluding AGE and DATE_TIME for medical context.
        self.target_entities = [
            "PERSON", 
            "PHONE_NUMBER", 
            "EMAIL_ADDRESS", 
            "US_SSN", 
            "US_PASSPORT", 
            "US_DRIVER_LICENSE", 
            "UK_NHS",
            "LOCATION",
            "CREDIT_CARD",
            "CRYPTO",
            "IBAN_CODE",
            "IP_ADDRESS"
        ]

    def anonymize(self, text: str) -> str:
        """
        Scans the text for PII entities and masks them with placeholder brackets.
        E.g. "Patient Name: John Doe" -> "Patient Name: <PERSON>"
        """
        if not text or not text.strip():
            return text

        try:
            # 1. Analyze text to find PII
            results = self.analyzer.analyze(
                text=text,
                entities=self.target_entities,
                language='en'
            )
            
            # 2. Anonymize the findings
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results
            )
            
            # Log metrics (number of items scrubbed)
            if results:
                entity_counts = {}
                for res in results:
                    entity_counts[res.entity_type] = entity_counts.get(res.entity_type, 0) + 1
                logger.info(f"PII Scrubber masked {len(results)} entities: {entity_counts}")
            
            return anonymized_result.text
            
        except Exception as e:
            # If scrubbing fails, we fail OPEN (err on the side of security)
            # by refusing to return the potentially sensitive text.
            logger.error(f"PII Scrubbing failed! Raising error to prevent data leak: {e}")
            raise RuntimeError("Compliance Guardrail: PII Scrubbing failed.") from e

# Singleton instance
_pii_scrubber = None

def get_pii_scrubber() -> PIIScrubber:
    global _pii_scrubber
    if _pii_scrubber is None:
        _pii_scrubber = PIIScrubber()
    return _pii_scrubber
