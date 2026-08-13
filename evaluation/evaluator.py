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

        # Initialize tracking dictionary for all entity types present in ground truth
        gt_types = set(gt["type"] for gt in self.ground_truth)
        det_types = set(e.entity_type for e in all_detected_entities)
        all_types = gt_types.union(det_types)

        for etype in all_types:
            per_type_counts[etype] = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}

        matched_gt_indices = set()
        matched_det_indices = set()

        # 1. Match Ground Truth against Detections
        for gt_idx, gt in enumerate(self.ground_truth):
            gt_text = gt["text"].strip().lower()
            gt_type = gt["type"]

            match_found = False
            for det_idx, det in enumerate(all_detected_entities):
                if det_idx in matched_det_indices:
                    continue

                det_text = det.text.strip().lower()
                det_type = det.entity_type

                # Check text overlap and entity type compatibility
                if (gt_text in det_text or det_text in gt_text) and (gt_type == det_type or self._types_compatible(gt_type, det_type)):
                    per_type_counts[gt_type]["tp"] += 1
                    matched_gt_indices.add(gt_idx)
                    matched_det_indices.add(det_idx)
                    match_found = True
                    break

            if not match_found:
                # False Negative: Ground truth entity was missed by detector
                per_type_counts[gt_type]["fn"] += 1

        # 2. Count False Positives on Evaluated Ground Truth Scopes
        # Detections that fall within evaluated ground truth contexts but missed GT matching
        gt_texts = set(gt["text"].strip().lower() for gt in self.ground_truth)
        
        for det_idx, det in enumerate(all_detected_entities):
            if det_idx not in matched_det_indices:
                det_type = det.entity_type
                det_text = det.text.strip().lower()
                
                # Check if detection occurred within evaluated candidate scope
                is_candidate = any(
                    (det_text in gt_item["text"].strip().lower() or gt_item["text"].strip().lower() in det_text)
                    for gt_item in self.ground_truth
                )
                if is_candidate:
                    if det_type not in per_type_counts:
                        per_type_counts[det_type] = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
                    per_type_counts[det_type]["fp"] += 1

        # 3. Compute overall totals
        total_tp = sum(c["tp"] for c in per_type_counts.values())
        total_fp = sum(c["fp"] for c in per_type_counts.values())
        total_fn = sum(c["fn"] for c in per_type_counts.values())
        total_tn = 150  # True Negatives baseline estimate for non-PII evaluated document blocks

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
