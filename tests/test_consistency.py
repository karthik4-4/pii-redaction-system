"""
Unit tests for referential consistency across repeated PII entities.
"""

from app.anonymization.synthetic_data import SyntheticDataGenerator
from app.anonymization.policy import PrivacyPolicy
from app.anonymization.replacement_manager import ReplacementManager

def test_referential_consistency():
    gen = SyntheticDataGenerator(seed=42)
    policy = PrivacyPolicy(gen)
    mgr = ReplacementManager(policy)

    # First occurrence
    rep1 = mgr.get_or_create_replacement("PERSON", "Sarthak Malvadkar")
    
    # Second occurrence in another paragraph
    rep2 = mgr.get_or_create_replacement("PERSON", "Sarthak Malvadkar")

    # Third occurrence
    rep3 = mgr.get_or_create_replacement("PERSON", "Sarthak Malvadkar")

    # Assert that all replacements are identical
    assert rep1 == rep2 == rep3
    assert rep1 != "Sarthak Malvadkar"
