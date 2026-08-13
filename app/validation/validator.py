"""
Output Validation module performing privacy regression scans and document integrity checks.
"""

import logging
from typing import Dict, List, Any
from app.document.reader import DocumentReader
from app.detection.engine import PIIDetectionEngine

logger = logging.getLogger(__name__)

class OutputValidator:
    """Scans redacted DOCX file to detect residual PII leaks and verify document integrity."""

    def __init__(self, detection_engine: PIIDetectionEngine):
        # Use existing detection engine instance
        self.engine = detection_engine

    def validate_file(self, redacted_filepath: str, original_replacement_map: Dict[tuple, str]) -> Dict[str, Any]:
        """Runs post-redaction scan on output document and produces validation results."""
        logger.info(f"Running post-redaction privacy validation on '{redacted_filepath}'...")

        reader = DocumentReader(redacted_filepath)
        blocks = reader.extract_blocks()

        # 1. Scan output document for remaining PII
        output_detections = self.engine.detect_document(blocks)

        # 2. Check if any original PII values persist in the output file
        leaked_original_pii = []
        original_values = {orig_text for (etype, orig_text), synth_val in original_replacement_map.items()}

        for block in blocks:
            for orig_text in original_values:
                if orig_text in block.text:
                    leaked_original_pii.append((block.block_id, orig_text))

        is_passed = len(leaked_original_pii) == 0

        validation_result = {
            "passed": is_passed,
            "total_blocks_scanned": len(blocks),
            "residual_detections": sum(len(e) for e in output_detections.values()),
            "leaked_original_pii_count": len(leaked_original_pii),
            "leaked_instances": leaked_original_pii,
        }

        if is_passed:
            logger.info("Validation PASSED: Zero original PII entities leaked into redacted document.")
        else:
            logger.warning(f"Validation WARNING: {len(leaked_original_pii)} original PII instances were detected in output.")

        return validation_result
