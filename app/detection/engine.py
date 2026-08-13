import logging
from typing import List, Dict
from app.document.models import TextBlock, PIIEntity, DetectionResult
from .presidio_detector import PresidioDetector
from .custom_recognizers import get_custom_recognizers
from .context_rules import ContextRulesEngine
from .entity_resolver import EntityResolver

logger = logging.getLogger(__name__)

# Standard entity mapping
PRESIDIO_TO_STANDARD = {
    "PERSON": "PERSON",
    "EMAIL_ADDRESS": "EMAIL_ADDRESS",
    "PHONE_NUMBER": "PHONE_NUMBER",
    "ORGANIZATION": "ORGANIZATION",
    "LOCATION": "ADDRESS",
    "ADDRESS": "ADDRESS",
    "DATE_TIME": "DATE_OF_BIRTH",
    "DATE_OF_BIRTH": "DATE_OF_BIRTH",
    "CREDIT_CARD": "CREDIT_CARD",
    "US_SSN": "SSN",
    "SSN": "SSN",
    "IP_ADDRESS": "IP_ADDRESS",
    "PAN": "PAN",
    "AADHAAR": "AADHAAR",
}

class PIIDetectionEngine:
    """Master PII detection engine orchestrating Presidio, custom recognizers, contextual rules, and entity resolution."""

    def __init__(self, spacy_model: str = "en_core_web_lg", thresholds: dict = None):
        self.presidio = PresidioDetector(spacy_model=spacy_model)
        for recognizer in get_custom_recognizers():
            self.presidio.add_recognizer(recognizer)

        self.context_rules = ContextRulesEngine()
        self.resolver = EntityResolver(thresholds=thresholds)

    def detect_block(self, block: TextBlock) -> List[PIIEntity]:
        if not block.text or not block.text.strip():
            return []

        # 1. Presidio analyze
        results = self.presidio.analyze(block.text, score_threshold=0.30)
        entities: List[PIIEntity] = []

        for r in results:
            std_type = PRESIDIO_TO_STANDARD.get(r.entity_type, r.entity_type)
            matched_text = block.text[r.start:r.end]
            entities.append(
                PIIEntity(
                    entity_type=std_type,
                    text=matched_text,
                    start=r.start,
                    end=r.end,
                    confidence=r.score,
                    source="presidio_recognizer",
                )
            )

        # 2. Refine with context rules
        refined = self.context_rules.refine_entities(block.text, entities)

        # 3. Resolve overlaps & filter by threshold
        resolved = self.resolver.resolve(refined)
        return resolved

    def detect_document(self, blocks: List[TextBlock]) -> Dict[str, List[PIIEntity]]:
        results: Dict[str, List[PIIEntity]] = {}
        for block in blocks:
            detected = self.detect_block(block)
            if detected:
                results[block.block_id] = detected
        return results
