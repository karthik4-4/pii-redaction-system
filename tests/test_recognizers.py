"""
Unit tests for custom recognizers (Credit Card Luhn, Indian Phone, PAN, Aadhaar).
"""

from app.detection.custom_recognizers import luhn_check, CreditCardLuhnRecognizer, PANRecognizer, AadhaarRecognizer

def test_luhn_check():
    # Valid credit card number (sample test card)
    assert luhn_check("4532015112830366") == True
    # Invalid card number
    assert luhn_check("4532015112830367") == False

def test_pan_recognizer():
    rec = PANRecognizer()
    results = rec.analyze("My PAN number is ABCDE1234F for tax filing.", ["PAN"])
    assert len(results) == 1
    assert results[0].start == 17
    assert results[0].end == 27

def test_aadhaar_recognizer():
    rec = AadhaarRecognizer()
    results = rec.analyze("Aadhaar: 9876 5432 1098 submitted.", ["AADHAAR"])
    assert len(results) == 1
    assert "9876 5432 1098" in "Aadhaar: 9876 5432 1098 submitted."[results[0].start:results[0].end]
