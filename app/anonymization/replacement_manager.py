"""
Replacement Manager maintaining document-level referential mapping consistency.
"""

import logging
from typing import Dict, Tuple, List
from app.document.models import PIIEntity
from .policy import PrivacyPolicy

logger = logging.getLogger(__name__)

class ReplacementManager:
    """Stores and reuses global synthetic replacements for detected PII entities across document sections."""

    def __init__(self, policy: PrivacyPolicy):
        self.policy = policy
        # Global dictionary mapping (entity_type, original_text) -> synthetic_value
        self.replacement_map: Dict[Tuple[str, str], str] = {}

    def get_or_create_replacement(self, entity_type: str, original_text: str) -> str:
        """Returns existing synthetic replacement if mapped previously; generates a new one otherwise."""
        key = (entity_type, original_text)
        if key in self.replacement_map:
            # Reuse stored synthetic replacement to preserve document referential consistency
            return self.replacement_map[key]

        # Generate a new synthetic replacement via Privacy Policy
        synthetic_val = self.policy.transform(entity_type, original_text)
        self.replacement_map[key] = synthetic_val
        logger.debug(f"Mapped {entity_type}: '{original_text}' -> '{synthetic_val}'")
        return synthetic_val

    def process_entities(self, block_entities: Dict[str, List[PIIEntity]]) -> Dict[Tuple[str, str], str]:
        """Iterates through all detected document block entities and registers replacements."""
        for block_id, entities in block_entities.items():
            for entity in entities:
                self.get_or_create_replacement(entity.entity_type, entity.text)
        return self.replacement_map
