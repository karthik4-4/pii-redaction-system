import io
import hashlib
import re
from typing import Dict, Tuple, Optional, List, Any
from PIL import Image, ImageDraw, ImageFont
from app.document.models import TextBlock, PIIEntity

class DocxImageRedactor:
    """Redacts and pseudonymizes embedded document images with contextual entity mapping."""

    def __init__(self, replacement_map: Dict[Tuple[str, str], str]):
        self.replacement_map = replacement_map
        self.org_pairs = self._build_org_pairs()
        self.primary_org = self.org_pairs[0] if self.org_pairs else ("Company", "Synthetic Tech")
        self.image_cache: Dict[str, bytes] = {}

    def _build_org_pairs(self) -> List[Tuple[str, str]]:
        pairs = []
        for (etype, original), replacement in self.replacement_map.items():
            if etype in ("ORGANIZATION", "COMPANY"):
                pairs.append((original, replacement))
        return pairs

    def get_initials(self, name: str) -> str:
        stop_words = {"LIMITED", "LTD", "PRIVATE", "PVT", "INC", "LLC", "AND", "&", "OF", "THE", "FOR", "CORP", "CORPORATION"}
        words = [w for w in name.split() if w.upper() not in stop_words]
        if not words:
            words = name.split()
        if len(words) >= 2:
            return f"{words[0][0]}{words[1][0]}".upper()
        elif words:
            return words[0][:2].upper()
        return "SYN"

    def _extract_colors(self, img: Image.Image) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        try:
            small = img.resize((50, 50)).convert("RGB")
            colors = small.getcolors(2500)
            if not colors:
                return (245, 247, 250), (30, 60, 110)
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
            bg_color = sorted_colors[0][1]

            fg_color = (30, 60, 110)
            for count, col in sorted_colors[1:]:
                dist = abs(col[0] - bg_color[0]) + abs(col[1] - bg_color[1]) + abs(col[2] - bg_color[2])
                if dist > 100:
                    fg_color = col
                    break
            return bg_color, fg_color
        except Exception:
            return (245, 247, 250), (30, 60, 110)

    def generate_logo_bytes(
        self,
        image_bytes: bytes,
        content_type: str,
        org_replacement: str
    ) -> Optional[bytes]:
        img_hash = hashlib.sha256(image_bytes + org_replacement.encode("utf-8")).hexdigest()
        if img_hash in self.image_cache:
            return self.image_cache[img_hash]

        try:
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size

            if width > 1400 or height > 1400:
                return None

            mode = "RGBA" if "png" in content_type.lower() else "RGB"
            bg_color, fg_color = self._extract_colors(img)

            if mode == "RGBA":
                bg_rgba = bg_color + (255,)
                fg_rgba = fg_color + (255,)
                res = Image.new("RGBA", (width, height), bg_rgba)
                draw = ImageDraw.Draw(res)
                text_color = fg_rgba
            else:
                res = Image.new("RGB", (width, height), bg_color)
                draw = ImageDraw.Draw(res)
                text_color = fg_color

            margin = max(2, min(width, height) // 20)
            draw.rectangle(
                [(margin, margin), (width - margin, height - margin)],
                outline=text_color,
                width=max(2, min(width, height) // 40)
            )

            initials = self.get_initials(org_replacement)
            try:
                font_size = max(12, min(width, height) // 3)
                font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()

            draw.text((width // 2, height // 2), initials, fill=text_color, font=font, anchor="mm")

            output = io.BytesIO()
            fmt = "PNG" if "png" in content_type.lower() else "JPEG"
            res.save(output, format=fmt, quality=95)

            result_bytes = output.getvalue()
            self.image_cache[img_hash] = result_bytes
            return result_bytes
        except Exception:
            return None

    def process_document_images(
        self,
        doc,
        blocks: Optional[List[TextBlock]] = None,
        block_entities: Optional[Dict[str, List[PIIEntity]]] = None
    ) -> int:
        modified_count = 0
        part_org_map: Dict[Any, str] = {}

        # 1. Map paragraph & table cell drawing rIds to contextual organization entities
        if blocks:
            for b_idx, block in enumerate(blocks):
                raw = getattr(block, "raw_element", None)
                if not raw or not hasattr(raw, "_element"):
                    continue

                xml = raw._element.xml
                rids = re.findall(r'r:(?:embed|id)="(rId\d+)"', xml)
                if not rids:
                    continue

                # Find organization entity in surrounding 5 blocks
                assoc_org = None
                start_idx = max(0, b_idx - 3)
                end_idx = min(len(blocks), b_idx + 4)
                for idx in range(start_idx, end_idx):
                    entities = getattr(blocks[idx], "entities", None) or (block_entities.get(blocks[idx].block_id, []) if block_entities else [])
                    for e in entities:
                        if e.entity_type in ("ORGANIZATION", "COMPANY"):
                            assoc_org = e.text
                            break
                    if assoc_org:
                        break

                if assoc_org:
                    synth_name = self.replacement_map.get(("ORGANIZATION", assoc_org))
                    if not synth_name:
                        synth_name = next((v for (t, txt), v in self.replacement_map.items() if txt == assoc_org), None)

                    if synth_name:
                        for rid in rids:
                            if rid in doc.part.rels:
                                part = doc.part.rels[rid].target_part
                                part_org_map[part] = synth_name

        # 2. Also check headers and footers for embedded images
        for section in doc.sections:
            for container in (section.header, section.footer):
                if not container:
                    continue
                for rel in container.part.rels.values():
                    if "image" in rel.target_ref:
                        part = rel.target_part
                        if part not in part_org_map:
                            part_org_map[part] = self.primary_org[1]

        # 3. Apply referentially consistent logo pseudonymization to image blobs
        processed_parts = set()
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                image_part = rel.target_part
                if image_part in processed_parts:
                    continue
                processed_parts.add(image_part)

                target_synth_name = part_org_map.get(image_part, self.primary_org[1])
                new_blob = self.generate_logo_bytes(
                    image_part.blob,
                    image_part.content_type,
                    target_synth_name
                )
                if new_blob:
                    image_part._blob = new_blob
                    modified_count += 1

        return modified_count
