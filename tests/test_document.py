"""
Unit tests for DOCX reading and writing.
"""

import os
import tempfile
import docx
from app.document.reader import DocumentReader
from app.document.writer import DocumentWriter
from app.document.models import PIIEntity

def test_document_reader_and_writer():
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = os.path.join(tmpdir, "test_doc.docx")

        # Create sample docx
        doc = docx.Document()
        doc.add_paragraph("Contact Person: Sarthak Malvadkar")
        doc.save(doc_path)

        # Read docx
        reader = DocumentReader(doc_path)
        blocks = reader.extract_blocks()
        assert len(blocks) == 1
        assert "Sarthak Malvadkar" in blocks[0].text

        # Apply replacement and save
        writer = DocumentWriter(reader.doc)
        entity = PIIEntity(
            entity_type="PERSON",
            text="Sarthak Malvadkar",
            start=16,
            end=33,
            confidence=0.95,
            source="test",
        )
        block_entities = {blocks[0].block_id: [entity]}
        replacement_map = {("PERSON", "Sarthak Malvadkar"): "John Doe"}

        writer.apply_replacements(blocks, block_entities, replacement_map)
        out_path = os.path.join(tmpdir, "redacted.docx")
        writer.save(out_path)

        # Re-read redacted docx
        out_reader = DocumentReader(out_path)
        out_blocks = out_reader.extract_blocks()
        assert "John Doe" in out_blocks[0].text
        assert "Sarthak Malvadkar" not in out_blocks[0].text
