import docx
from typing import List, Dict
from .models import TextBlock, PIIEntity
from app.anonymization.image_redactor import DocxImageRedactor

class DocumentWriter:
    """Updates Word Document text content and embedded images with synthetic replacements."""

    def __init__(self, reader_doc: docx.Document):
        self.doc = reader_doc

    def apply_replacements(
        self,
        blocks: List[TextBlock],
        block_entities: Dict[str, List[PIIEntity]],
        replacement_map: Dict[tuple, str],
    ) -> int:
        total_replacements = 0

        for block in blocks:
            entities = getattr(block, 'entities', None) or block_entities.get(block.block_id, [])
            if not entities:
                continue

            paragraph = block.raw_element
            if not paragraph:
                continue

            sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)
            full_text = block.text
            replaced_in_block = False

            for entity in sorted_entities:
                key = (entity.entity_type, entity.text)
                replacement_text = replacement_map.get(key)
                if not replacement_text:
                    replacement_text = next((v for (t, txt), v in replacement_map.items() if txt == entity.text), None)

                if not replacement_text:
                    continue

                start, end = entity.start, entity.end
                if full_text[start:end] == entity.text:
                    full_text = full_text[:start] + replacement_text + full_text[end:]
                    total_replacements += 1
                    replaced_in_block = True

            if replaced_in_block:
                paragraph.text = full_text

        # Redact and pseudonymize embedded document logo images with contextual entity mapping
        image_redactor = DocxImageRedactor(replacement_map)
        image_redactor.process_document_images(self.doc, blocks, block_entities)

        return total_replacements

    def save(self, output_filepath: str):
        self.doc.save(output_filepath)
