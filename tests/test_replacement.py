"""
Unit tests for synthetic data generation and replacement.
"""

from app.anonymization.synthetic_data import SyntheticDataGenerator
from app.anonymization.policy import PrivacyPolicy

def test_synthetic_data_generator():
    gen = SyntheticDataGenerator(seed=42)
    
    fake_name = gen.generate("PERSON", "Sarthak Malvadkar")
    assert fake_name != "Sarthak Malvadkar"
    assert len(fake_name) > 0

    fake_email = gen.generate("EMAIL_ADDRESS", "cs.connect@kshinternational.com")
    assert fake_email.endswith("@example.com")
    assert fake_email != "cs.connect@kshinternational.com"

    fake_phone = gen.generate("PHONE_NUMBER", "+91 20 45053237")
    assert fake_phone.startswith("+91")

def test_privacy_policy():
    gen = SyntheticDataGenerator(seed=42)
    policy = PrivacyPolicy(gen)
    
    transformed = policy.transform("PERSON", "John Smith")
    assert transformed != "John Smith"
