import docx
from typing import List, Dict
from .models import TextBlock, PIIEntity, ReplacementMapping

class DocumentWriter:
    """Updates Word Document text content with synthetic replacements while preserving styling."""

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
            entities = block.entities if hasattr(block, 'entities') else block_entities.get(block.block_id, [])
            if not entities:
                continue

            # Sort entities from last to first so index offsets remain valid
            sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)
            paragraph = block.raw_element
            if not paragraph or not hasattr(paragraph, "runs"):
                continue

            current_text = block.text

            for entity in sorted_entities:
                key = (entity.entity_type, entity.text)
                if key not in replacement_map:
                    # Fallback lookup by text
                    match_val = next((v for (t, txt), v in replacement_map.items() if txt == entity.text), None)
                    if match_val:
                        replacement_text = match_val
                    else:
                        continue
                else:
                    replacement_text = replacement_map[key]

                # Update current_text string slice
                start, end = entity.start, entity.end
                if current_text[start:end] == entity.text:
                    current_text = current_text[:start] + replacement_text + current_text[end:]
                    total_replacements += 1

            # Update the paragraph runs cleanly
            self._update_paragraph_text(paragraph, block, sorted_entities, replacement_map)

        return total_replacements

    def _update_paragraph_text(
        self,
        paragraph: docx.text.paragraph.Paragraph,
        block: TextBlock,
        entities: List[PIIEntity],
        replacement_map: Dict[tuple, str],
    ):
        if not paragraph.runs:
            return

        # Attempt precise run-level replacement if entity fits inside single runs
        can_do_run_replacement = True
        run_replacements = []

        for entity in entities:
            key = (entity.entity_type, entity.text)
            replacement_text = replacement_map.get(key)
            if not replacement_text:
                replacement_text = next((v for (t, txt), v in replacement_map.items() if txt == entity.text), entity.text)

            # Find containing run
            target_run = None
            for run_span in block.runs:
                if run_span.start_char <= entity.start and entity.end <= run_span.end_char:
                    target_run = run_span
                    break

            if target_run:
                # Entity fits cleanly in one run
                rel_start = entity.start - target_run.start_char
                rel_end = entity.end - target_run.start_char
                run_replacements.append((target_run.run_obj, rel_start, rel_end, replacement_text, entity.text))
            else:
                can_do_run_replacement = False
                break

        if can_do_run_replacement and run_replacements:
            for run_obj, r_start, r_end, repl_txt, orig_txt in run_replacements:
                r_text = run_obj.text
                if r_text[r_start:r_end] == orig_txt:
                    run_obj.text = r_text[:r_start] + repl_txt + r_text[r_end:]
        else:
            # Re-construct entire text on first run to preserve primary formatting
            full_text = block.text
            for entity in sorted(entities, key=lambda e: e.start, reverse=True):
                key = (entity.entity_type, entity.text)
                repl_txt = replacement_map.get(key)
                if not repl_txt:
                    repl_txt = next((v for (t, txt), v in replacement_map.items() if txt == entity.text), entity.text)
                start, end = entity.start, entity.end
                if full_text[start:end] == entity.text:
                    full_text = full_text[:start] + repl_txt + full_text[end:]

            paragraph.runs[0].text = full_text
            for r in paragraph.runs[1:]:
                r.text = ""

    def save(self, output_filepath: str):
        self.doc.save(output_filepath)
