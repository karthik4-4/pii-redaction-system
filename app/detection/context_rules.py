import re
from typing import List
from .models_import import PIIEntity  # We will import cleanly

EXCLUDED_PERSON_NAMES = {
    "red herring prospectus", "draft red herring prospectus",
    "book running lead manager", "book running lead managers",
    "securities and exchange board of india", "national stock exchange",
    "bse limited", "national stock exchange of india limited",
    "companies act", "sebi icdr regulations", "table of contents",
    "registered office", "corporate office", "contact person",
    "board of directors", "key managerial personnel", "statutory auditors",
}

EXCLUDED_ORGANIZATIONS = {
    "securities and exchange board of india", "reserve bank of india",
    "government of india", "companies act", "income tax act",
    "high court of judicature", "supreme court of india",
    "ministry of corporate affairs", "gazette of india",
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

            # Prefix context before entity (up to 40 chars)
            prefix = text_lower[max(0, start - 40):start]

            # 1. Suppress Non-PII Headers / Excluded terms
            if e_type in ("PERSON", "NAME") and e_text_lower in EXCLUDED_PERSON_NAMES:
                continue

            if e_type in ("ORGANIZATION", "COMPANY") and e_text_lower in EXCLUDED_ORGANIZATIONS:
                continue

            # 2. Person Context Boost
            if e_type in ("PERSON", "PER"):
                if any(kw in prefix for kw in ["contact person", "promoter", "director", "mr.", "ms.", "mrs.", "dr.", "shri"]):
                    score = min(1.0, score + 0.25)
                elif len(e_text.split()) < 2:
                    # Single word name without title/context gets slight penalty
                    score -= 0.15

            # 3. Email Context Boost
            elif e_type in ("EMAIL_ADDRESS", "EMAIL"):
                if any(kw in prefix for kw in ["email", "e-mail", "mail", "cs.connect"]):
                    score = min(1.0, score + 0.20)

            # 4. Phone Context / Ticket Number Suppression
            elif e_type in ("PHONE_NUMBER", "PHONE"):
                if any(kw in prefix for kw in ["ticket", "order", "application no", "cin", "sebi reg", "pan no"]):
                    score -= 0.40  # Penalty for non-phone numerical IDs
                elif any(kw in prefix for kw in ["tel", "telephone", "phone", "mobile", "fax", "contact"]):
                    score = min(1.0, score + 0.25)

            # 5. Date of Birth Context Filtering
            elif e_type == "DATE_OF_BIRTH":
                if any(kw in prefix for kw in ["incorporation", "prospectus", "ended", "period", "dated", "as on"]):
                    score -= 0.50  # Demote document / incorporation dates
                elif any(kw in prefix for kw in ["birth", "dob", "born"]):
                    score = min(1.0, score + 0.30)

            # 6. Address Context Boost
            elif e_type == "ADDRESS":
                if any(kw in prefix for kw in ["registered office", "corporate office", "residing at", "address"]):
                    score = min(1.0, score + 0.20)

            # Update score if above threshold
            if score >= 0.40:
                entity.confidence = score
                refined.append(entity)

        return refined
