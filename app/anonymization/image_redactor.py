import io
from typing import Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

class DocxImageRedactor:
    """Redacts and pseudonymizes embedded logo images and banners in Word documents."""

    def __init__(self, replacement_map: Dict[Tuple[str, str], str]):
        self.replacement_map = replacement_map
        self.org_original, self.org_replacement = self._find_primary_organization()
        self.orig_initials = self._get_initials(self.org_original) or "ORG"
        self.syn_initials = self._get_initials(self.org_replacement) or "SYN"

    def _find_primary_organization(self) -> Tuple[str, str]:
        for (etype, original), replacement in self.replacement_map.items():
            if etype in ("ORGANIZATION", "COMPANY"):
                return original, replacement
        return "Company", "Synthetic Tech"

    def _get_initials(self, name: str) -> str:
        stop_words = {"LIMITED", "LTD", "PRIVATE", "PVT", "INC", "LLC", "AND", "&", "OF", "THE", "FOR"}
        words = [w for w in name.split() if w.upper() not in stop_words]
        if not words:
            words = name.split()
        if len(words) >= 2:
            return f"{words[0][0]}{words[1][0]}".upper()
        elif words:
            return words[0][:2].upper()
        return "SYN"

    def redact_image_bytes(self, image_bytes: bytes, content_type: str) -> Optional[bytes]:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size

            # Skip full-page diagrams/scans, target logos and header banners
            if width > 1200 or height > 1200:
                return None

            mode = "RGBA" if "png" in content_type.lower() else "RGB"
            res = Image.new(mode, (width, height), (245, 247, 250, 255) if mode == "RGBA" else (245, 247, 250))
            draw = ImageDraw.Draw(res)

            # Draw clean outer logo border
            margin = max(2, min(width, height) // 20)
            draw.rectangle(
                [(margin, margin), (width - margin, height - margin)],
                outline=(30, 60, 110),
                width=max(2, min(width, height) // 40)
            )

            # Render synthetic initials logo text
            text = self.syn_initials
            try:
                font_size = max(12, min(width, height) // 3)
                font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()

            draw.text((width // 2, height // 2), text, fill=(30, 60, 110), font=font, anchor="mm")

            output = io.BytesIO()
            fmt = "PNG" if "png" in content_type.lower() else "JPEG"
            res.save(output, format=fmt, quality=95)
            return output.getvalue()
        except Exception:
            return None

    def process_document_images(self, doc) -> int:
        modified_count = 0
        processed_parts = set()

        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                image_part = rel.target_part
                if image_part in processed_parts:
                    continue
                processed_parts.add(image_part)

                new_blob = self.redact_image_bytes(image_part.blob, image_part.content_type)
                if new_blob:
                    image_part._blob = new_blob
                    modified_count += 1

        return modified_count
