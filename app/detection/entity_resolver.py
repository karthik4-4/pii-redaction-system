from typing import List
from app.document.models import PIIEntity

class EntityResolver:
    """Deduplicates overlapping entity spans, resolves classification conflicts, and applies thresholds."""

    def __init__(self, thresholds: dict = None):
        self.thresholds = thresholds or {
            "PERSON": 0.65,
            "EMAIL_ADDRESS": 0.70,
            "PHONE_NUMBER": 0.65,
            "ORGANIZATION": 0.65,
            "ADDRESS": 0.60,
            "DATE_OF_BIRTH": 0.75,
            "CREDIT_CARD": 0.85,
            "SSN": 0.85,
            "IP_ADDRESS": 0.85,
            "PAN": 0.80,
            "AADHAAR": 0.80,
        }
        self.default_threshold = 0.65

    def resolve(self, entities: List[PIIEntity]) -> List[PIIEntity]:
        if not entities:
            return []

        # 1. Filter by threshold
        valid_entities = []
        for e in entities:
            thresh = self.thresholds.get(e.entity_type, self.default_threshold)
            if e.confidence >= thresh:
                valid_entities.append(e)

        if not valid_entities:
            return []

        # 2. Sort by start index (asc) then length (desc) then confidence (desc)
        sorted_entities = sorted(
            valid_entities,
            key=lambda x: (x.start, -(x.end - x.start), -x.confidence)
        )

        # 3. Non-overlapping selection
        resolved: List[PIIEntity] = []
        for current in sorted_entities:
            overlap = False
            for idx, existing in enumerate(resolved):
                # Check for character span overlap
                if max(current.start, existing.start) < min(current.end, existing.end):
                    overlap = True
                    # If current has higher confidence or longer span, replace existing
                    current_len = current.end - current.start
                    existing_len = existing.end - existing.start
                    if (current.confidence > existing.confidence + 0.1) or (current_len > existing_len and current.confidence >= existing.confidence):
                        resolved[idx] = current
                    break
            if not overlap:
                resolved.append(current)

        # Return sorted by character start position
        return sorted(resolved, key=lambda x: x.start)
