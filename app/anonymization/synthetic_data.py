import random
from faker import Faker
from typing import Optional

class SyntheticDataGenerator:
    """Generates realistic fake values for detected PII entity types using Faker."""

    def __init__(self, seed: Optional[int] = 42, locale: str = "en_IN"):
        self.faker = Faker([locale, "en_US"])
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

    def generate(self, entity_type: str, original_text: str = "") -> str:
        etype = entity_type.upper()

        if etype in ("PERSON", "NAME"):
            return self.faker.name()

        elif etype in ("EMAIL_ADDRESS", "EMAIL"):
            clean_name = self.faker.first_name().lower() + "." + self.faker.last_name().lower()
            return f"{clean_name}@example.com"

        elif etype in ("PHONE_NUMBER", "PHONE"):
            # Preserve format of original phone if possible
            if original_text.startswith("+91"):
                return f"+91 {random.randint(7000, 9999)} {random.randint(100000, 999999)}"
            elif original_text.startswith("0"):
                return f"020 {random.randint(20000000, 29999999)}"
            return f"+91 9{random.randint(100000009, 999999999)}"

        elif etype in ("ORGANIZATION", "COMPANY"):
            suffixes = ["Limited", "Ltd", "Private Limited", "Pvt Ltd"]
            company_base = self.faker.company().split()[0]
            suffix = random.choice(suffixes)
            return f"{company_base} Technologies {suffix}"

        elif etype == "ADDRESS":
            return f"{random.randint(10, 99)} Business Park, Sector {random.randint(1, 20)}, Pune – 411 001, Maharashtra, India"

        elif etype == "DATE_OF_BIRTH":
            dob = self.faker.date_of_birth(minimum_age=25, maximum_age=65)
            return dob.strftime("%B %d, %Y")

        elif etype == "CREDIT_CARD":
            return f"4532 {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"

        elif etype == "SSN":
            return f"9{random.randint(10,99)}-00-{random.randint(1000,9999)}"

        elif etype == "IP_ADDRESS":
            return f"192.0.2.{random.randint(1, 254)}"

        elif etype == "PAN":
            chars = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
            nums = "".join(random.choices("0123456789", k=4))
            char_last = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            return f"{chars}{nums}{char_last}"

        elif etype == "AADHAAR":
            return f"{random.randint(2000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"

        # Default fallback
        return f"[SYNTHETIC_{etype}]"
