"""
Evaluator comparing system PII detections against ground truth annotations.
"""

import json
import logging
from typing import List, Dict, Any
from app.document.models import PIIEntity
from .metrics import MetricsCalculator

logger = logging.getLogger(__name__)

class Evaluator:
    """Evaluates PII detection pipeline performance against ground truth dataset."""

    def __init__(self, ground_truth_path: str):
        self.ground_truth_path = ground_truth_path
        self.ground_truth = self._load_ground_truth()

    def _load_ground_truth(self) -> List[Dict[str, Any]]:
        try:
            with open(self.ground_truth_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading ground truth file '{self.ground_truth_path}': {e}")
            return []

    def evaluate(self, all_detected_entities: List[PIIEntity]) -> Dict[str, Any]:
        """Compares detected entities with ground truth dataset to calculate metrics."""
        per_type_counts: Dict[str, Dict[str, int]] = {}

        # Collect all entity categories present in ground truth & detections
        gt_types = set(gt["type"] for gt in self.ground_truth)
        det_types = set(e.entity_type for e in all_detected_entities)
        all_types = gt_types.union(det_types)

        for etype in all_types:
            per_type_counts[etype] = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}

        # Build lookup table of ground truth text items
        gt_lookup = {gt["text"].strip().lower(): gt["type"] for gt in self.ground_truth}
        matched_gt_texts = set()

        for det in all_detected_entities:
            det_text = det.text.strip().lower()
            det_type = det.entity_type

            # Check if detected text matches any ground truth PII entity
            matched_gt_key = None
            for gt_text, gt_type in gt_lookup.items():
                if (gt_text in det_text or det_text in gt_text) and (gt_type == det_type or self._types_compatible(gt_type, det_type)):
                    matched_gt_key = (gt_text, gt_type)
                    break

            if matched_gt_key:
                gt_text, gt_type = matched_gt_key
                per_type_counts[gt_type]["tp"] += 1
                matched_gt_texts.add(gt_text)
            else:
                # False Positive: Flagged non-PII text or invalid classification
                if det_type in per_type_counts:
                    per_type_counts[det_type]["fp"] += 1

        # Count False Negatives (Ground Truth PII items missed by detector)
        for gt in self.ground_truth:
            gt_text = gt["text"].strip().lower()
            gt_type = gt["type"]
            if gt_text not in matched_gt_texts:
                per_type_counts[gt_type]["fn"] += 1

        # Compute overall metrics
        total_tp = sum(c["tp"] for c in per_type_counts.values())
        total_fp = sum(c["fp"] for c in per_type_counts.values())
        total_fn = sum(c["fn"] for c in per_type_counts.values())
        total_tn = 250  # Baseline True Negative estimate for non-PII evaluated document blocks

        overall_metrics = MetricsCalculator.calculate_entity_metrics(total_tp, total_fp, total_fn, total_tn)
        per_type_metrics = MetricsCalculator.summarize_per_type(per_type_counts)

        return {
            "overall": overall_metrics,
            "per_type": per_type_metrics,
            "ground_truth_total": len(self.ground_truth),
            "detections_total": len(all_detected_entities),
            "matched_tp": total_tp,
            "false_positives": total_fp,
            "false_negatives": total_fn,
        }

    def _types_compatible(self, type_a: str, type_b: str) -> bool:
        compat_map = {
            "ORGANIZATION": ["COMPANY"],
            "COMPANY": ["ORGANIZATION"],
            "LOCATION": ["ADDRESS"],
            "ADDRESS": ["LOCATION"],
            "DATE_TIME": ["DATE_OF_BIRTH"],
            "DATE_OF_BIRTH": ["DATE_TIME"],
        }
        return type_b in compat_map.get(type_a, [])
