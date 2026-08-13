import re
from typing import List, Optional
from presidio_analyzer import PatternRecognizer, Pattern

def luhn_check(card_num: str) -> bool:
    """Validates credit card numbers using the Luhn algorithm."""
    digits = [int(c) for c in card_num if c.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += digit
    return checksum % 10 == 0


class CreditCardLuhnRecognizer(PatternRecognizer):
    """Credit Card Recognizer with Luhn checksum validation."""

    def __init__(self):
        patterns = [
            Pattern(
                name="credit_card_pattern",
                regex=r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
                score=0.85,
            ),
            Pattern(
                name="credit_card_formatted",
                regex=r"\b(?:\d{4}[-\s]){3}\d{4}\b",
                score=0.85,
            ),
        ]
        super().__init__(
            supported_entity="CREDIT_CARD",
            patterns=patterns,
            context=["credit", "card", "cardholder", "cvv", "mastercard", "visa", "amex"],
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        clean_text = re.sub(r"\D", "", pattern_text)
        return luhn_check(clean_text)


class IndianPhoneRecognizer(PatternRecognizer):
    """Recognizer for Indian phone and mobile numbers."""

    def __init__(self):
        patterns = [
            Pattern(
                name="indian_phone_international",
                regex=r"\+91[\s\-]?[6-9]\d{9}",
                score=0.85,
            ),
            Pattern(
                name="indian_landline_std",
                regex=r"\+91[\s\-]?\d{2,4}[\s\-]?\d{6,8}",
                score=0.80,
            ),
            Pattern(
                name="indian_std_code",
                regex=r"\b0\d{2,4}[\s\-]\d{6,8}\b",
                score=0.75,
            ),
            Pattern(
                name="indian_mobile_bare",
                regex=r"\b[6-9]\d{9}\b",
                score=0.45,  # Lower base score, boosted by context
            ),
        ]
        super().__init__(
            supported_entity="PHONE_NUMBER",
            patterns=patterns,
            context=["tel", "telephone", "phone", "mobile", "contact", "fax", "call", "board"],
        )


class CompanyRecognizer(PatternRecognizer):
    """Recognizer for Corporate and Organization Names."""

    def __init__(self):
        patterns = [
            Pattern(
                name="company_suffix_ltd",
                regex=r"\b[A-Z][A-Za-z0-9&\.\s]{2,40}\s(?:Limited|Ltd|Pvt\.?\s?Ltd|Private\sLimited|Inc\.?|LLC|Corporation|Corp\.?)\b",
                score=0.85,
            ),
            Pattern(
                name="financial_institution",
                regex=r"\b[A-Z][A-Za-z0-9&\.\s]{2,40}\s(?:Securities|Capital|Investments|Finance|Bank|Broking|Services)\s(?:Limited|Ltd|Pvt\.?\s?Ltd|Private\sLimited)\b",
                score=0.90,
            ),
        ]
        super().__init__(
            supported_entity="ORGANIZATION",
            patterns=patterns,
            context=["company", "promoter", "issuer", "underwriter", "registrar", "lead manager", "corporate"],
        )


class IndianAddressRecognizer(PatternRecognizer):
    """Recognizer for Physical and Mailing Addresses."""

    def __init__(self):
        patterns = [
            Pattern(
                name="address_pin_pattern",
                regex=r"\b[A-Za-z0-9\s,\-\.\/]{10,120}(?:Pin|PIN|Pincode|Pin\sCode)?[\s\:\-\–]*\d{3}\s?\d{3}\b",
                score=0.80,
            ),
            Pattern(
                name="address_keywords_pattern",
                regex=r"\b(?:Plot|No\.|Building|Wing|Floor|Street|Road|Marg|Chakan|Taluka|District|Village|Industrial\sArea|Complex)[\s,A-Za-z0-9\-\.\/]{5,100}(?:Mumbai|Pune|Maharashtra|Delhi|Bengaluru|India)\b",
                score=0.85,
            ),
        ]
        super().__init__(
            supported_entity="ADDRESS",
            patterns=patterns,
            context=["registered office", "corporate office", "address", "residing at", "location", "premise"],
        )


class DOBRecognizer(PatternRecognizer):
    """Contextual Date of Birth Recognizer."""

    def __init__(self):
        patterns = [
            Pattern(
                name="dob_formatted_date",
                regex=r"\b(?:0?[1-9]|[12][0-9]|3[01])[\/\-\.\s](?:0?[1-9]|1[012]|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\/\-\.\s](?:19|20)\d{2}\b",
                score=0.50,
            ),
            Pattern(
                name="dob_verbose_date",
                regex=r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s(?:0?[1-9]|[12][0-9]|3[01]),?\s(?:19|20)\d{2}\b",
                score=0.50,
            ),
        ]
        super().__init__(
            supported_entity="DATE_OF_BIRTH",
            patterns=patterns,
            context=["date of birth", "dob", "born on", "birth date", "birthdate", "age"],
        )


class PANRecognizer(PatternRecognizer):
    """Recognizer for Indian Permanent Account Number (PAN)."""

    def __init__(self):
        patterns = [
            Pattern(
                name="pan_pattern",
                regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
                score=0.85,
            ),
        ]
        super().__init__(
            supported_entity="PAN",
            patterns=patterns,
            context=["pan", "permanent account number", "income tax"],
        )


class AadhaarRecognizer(PatternRecognizer):
    """Recognizer for Indian Aadhaar Card Numbers."""

    def __init__(self):
        patterns = [
            Pattern(
                name="aadhaar_pattern",
                regex=r"\b[2-9]{1}\d{3}[\s\-]?\d{4}[\s\-]?\d{4}\b",
                score=0.80,
            ),
        ]
        super().__init__(
            supported_entity="AADHAAR",
            patterns=patterns,
            context=["aadhaar", "uid", "unique identification"],
        )


class PersonLabelRecognizer(PatternRecognizer):
    """Recognizer for Person Names following contextual field labels like 'Contact Person:'."""

    def __init__(self):
        patterns = [
            Pattern(
                name="person_label_pattern",
                regex=r"\b(?:Contact Person|Promoter|Director|Key Managerial Personnel|Company Secretary|Compliance Officer|Mr\.|Ms\.|Shri)[\:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b",
                score=0.85,
            ),
        ]
        super().__init__(
            supported_entity="PERSON",
            patterns=patterns,
            context=["contact person", "promoter", "director", "officer", "secretary", "manager"],
        )


def get_custom_recognizers() -> List[PatternRecognizer]:
    """Factory returning all specialized custom recognizers."""
    return [
        CreditCardLuhnRecognizer(),
        IndianPhoneRecognizer(),
        CompanyRecognizer(),
        IndianAddressRecognizer(),
        DOBRecognizer(),
        PANRecognizer(),
        AadhaarRecognizer(),
        PersonLabelRecognizer(),
    ]
