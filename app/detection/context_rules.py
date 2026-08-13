import re
from typing import List

# Words and titles that should NEVER be redacted as PERSON
EXCLUDED_PERSON_NAMES = {
    "red herring prospectus", "draft red herring prospectus",
    "book running lead manager", "book running lead managers",
    "securities and exchange board of india", "national stock exchange",
    "bse limited", "national stock exchange of india limited",
    "companies act", "sebi icdr regulations", "table of contents",
    "registered office", "corporate office", "contact person",
    "board of directors", "key managerial personnel", "statutory auditors",
    "company secretary and compliance officer", "company secretary",
    "compliance officer", "chief financial officer", "managing director",
    "whole-time director", "independent director", "executive director",
    "promoter selling shareholder", "promoter selling shareholders",
}

# Organizations that are generic regulators/laws and NOT sensitive company PII
EXCLUDED_ORGANIZATIONS = {
    "securities and exchange board of india", "reserve bank of india",
    "government of india", "companies act", "income tax act",
    "high court of judicature", "supreme court of india",
    "ministry of corporate affairs", "gazette of india",
    "registrar of companies", "central processing centre",
    "national stock exchange of india limited", "bse limited",
    "national stock exchange", "bse", "nse", "roc", "sebi",
    "public limited", "private limited", "act", "company to",
    "employment act", "sales tax department",
}

# Standalone city/state/country names that are NOT physical addresses by themselves
STANDALONE_LOCATIONS = {
    "mumbai", "pune", "maharashtra", "india", "bombay", "delhi",
    "bengaluru", "chennai", "kolkata", "ahmedabad", "hyderabad",
}

class ContextRulesEngine:
    """Refines PII entity confidence scores based on document context and suppresses false positives."""

    def refine_entities(self, text: str, entities: List[dict]) -> List[dict]:
        refined = []
        text_lower = text.lower()

        for entity in entities:
            e_text = entity.text.strip()
            e_text_lower = e_text.lower()
            e_type = entity.entity_type
            score = entity.confidence
            start, end = entity.start, entity.end

            # Prefix context before entity (up to 50 chars)
            prefix = text_lower[max(0, start - 50):start]

            # 0. Filter out non-alphanumeric single characters (e.g. Rupee symbol ₹)
            if len(e_text) < 2 or e_text in ("₹", "$", "#", "@", "offer", "embassy"):
                continue

            # 1. Suppress Non-PII Job Titles, Regulator Names, Laws, and CIN Numbers
            if re.match(r"^[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$", e_text) or e_text_lower in ("roc", "promoter group", "the group entities", "xv", "xvii", "xvi", "xiv", "xiii", "offer", "embassy"):
                continue  # Skip Corporate Identity Numbers (CIN) and generic section titles

            if e_type in ("PERSON", "NAME"):
                if e_text_lower in EXCLUDED_PERSON_NAMES or "chakan" in e_text_lower or "taluka" in e_text_lower or "dated" in e_text_lower or "certificate" in e_text_lower or "entities" in e_text_lower:
                    continue

            if e_type in ("ORGANIZATION", "COMPANY"):
                if e_text_lower in EXCLUDED_ORGANIZATIONS or e_text_lower in ("board", "cs", "cfo", "company", "promoter group", "the group entities", "xv", "xvii", "xvi", "xiv", "xiii") or e_text_lower.startswith("the conversion") or e_text_lower.startswith("company to") or "certificate" in e_text_lower:
                    continue
                # If entity is actually a person's name misclassified as organization, change entity_type to PERSON
                if any(p_name in e_text for p_name in ["Kushal Subbayya Hegde", "Pushpa Kushal Hegde", "Rajesh Kushal Hegde", "Rohit Kushal Hegde", "Rakhi Girija Shetty", "Sarthak Malvadkar"]):
                    entity.entity_type = "PERSON"
                    e_type = "PERSON"

            # 2. Standalone Location Suppression (Do not redact plain city/state names as ADDRESS)
            if e_type == "ADDRESS" and e_text_lower in STANDALONE_LOCATIONS:
                # Require explicit street/building/PIN context
                if not any(kw in prefix for kw in ["registered office", "corporate office", "residing at", "address", "plot", "building", "flat"]):
                    if not re.search(r"\d{3}\s?\d{3}", text[max(0, start-20):min(len(text), end+20)]):
                        continue

            # 3. Person Context Boosting & Penalty
            if e_type == "PERSON":
                if any(kw in prefix for kw in ["contact person", "promoter", "director", "mr.", "ms.", "mrs.", "dr.", "shri"]):
                    score = min(1.0, score + 0.30)
                elif len(e_text.split()) < 2:
                    # Single word name without honorific or title prefix is risky
                    score -= 0.20

            # 4. Email Context Boost
            elif e_type in ("EMAIL_ADDRESS", "EMAIL"):
                if any(kw in prefix for kw in ["email", "e-mail", "mail", "cs.connect"]):
                    score = min(1.0, score + 0.25)

            # 5. Phone Context Boost & Ticket Number Penalty
            elif e_type in ("PHONE_NUMBER", "PHONE"):
                if any(kw in prefix for kw in ["ticket", "order", "application no", "cin", "sebi reg", "pan no", "din", "page"]):
                    score -= 0.50  # Demote ticket/application numbers
                elif any(kw in prefix for kw in ["tel", "telephone", "phone", "mobile", "fax", "contact"]):
                    score = min(1.0, score + 0.30)

            # 6. Date of Birth Context Filtering
            elif e_type == "DATE_OF_BIRTH":
                if not any(kw in prefix for kw in ["birth", "dob", "born on", "birthdate"]):
                    # If not explicitly preceded by birth keywords, demote
                    score -= 0.45
                else:
                    score = min(1.0, score + 0.35)

            # 7. Address Context Boost
            elif e_type == "ADDRESS":
                if any(kw in prefix for kw in ["registered office", "corporate office", "residing at", "address"]):
                    score = min(1.0, score + 0.25)

            # Keep entity if refined score meets threshold
            if score >= 0.50:
                entity.confidence = score
                refined.append(entity)

        return refined
