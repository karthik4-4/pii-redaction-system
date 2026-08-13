"""
Unit tests for PII Detection Engine.
"""

import pytest
from app.document.models import TextBlock
from app.detection.engine import PIIDetectionEngine

@pytest.fixture
def detection_engine():
    # Initialize engine for testing
    return PIIDetectionEngine(spacy_model="en_core_web_lg")

def test_email_detection(detection_engine):
    block = TextBlock(
        block_id="test_1",
        block_type="paragraph",
        text="Contact us at cs.connect@kshinternational.com for investor relations.",
    )
    entities = detection_engine.detect_block(block)
    assert len(entities) >= 1
    email_entity = next((e for e in entities if e.entity_type == "EMAIL_ADDRESS"), None)
    assert email_entity is not None
    assert email_entity.text == "cs.connect@kshinternational.com"

def test_phone_detection(detection_engine):
    block = TextBlock(
        block_id="test_2",
        block_type="paragraph",
        text="Please call Telephone: +91 20 45053237 during office hours.",
    )
    entities = detection_engine.detect_block(block)
    phone_entity = next((e for e in entities if e.entity_type == "PHONE_NUMBER"), None)
    assert phone_entity is not None
    assert "+91 20 45053237" in phone_entity.text or "45053237" in phone_entity.text

def test_person_detection(detection_engine):
    block = TextBlock(
        block_id="test_3",
        block_type="paragraph",
        text="Contact Person: Sarthak Malvadkar, Company Secretary and Compliance Officer.",
    )
    entities = detection_engine.detect_block(block)
    person_entity = next((e for e in entities if e.entity_type == "PERSON"), None)
    assert person_entity is not None
    assert "Sarthak Malvadkar" in person_entity.text
