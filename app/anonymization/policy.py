"""
Privacy Policy module defining transformation rules for each PII category.
"""

from typing import Dict, Any
from .synthetic_data import SyntheticDataGenerator

class PrivacyPolicy:
    """Dispatches detected PII entity categories to synthetic data generation strategies."""

    def __init__(self, generator: SyntheticDataGenerator):
        # Attach synthetic generator instance
        self.generator = generator

    def transform(self, entity_type: str, original_text: str) -> str:
        """Transforms sensitive PII entity text into a realistic synthetic alternative."""
        if not original_text or not original_text.strip():
            return original_text

        # Delegate entity transformation to Faker synthetic generator
        return self.generator.generate(entity_type, original_text)
