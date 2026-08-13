"""
Metrics Calculator computing entity-level Precision, Recall, F1 Score, and Accuracy.
"""

from typing import Dict, Any, List

class MetricsCalculator:
    """Computes statistical metrics (Precision, Recall, Accuracy, F1) for PII detection."""

    @staticmethod
    def calculate_entity_metrics(tp: int, fp: int, fn: int, tn: int = 0) -> Dict[str, float]:
        """Calculates Precision, Recall, F1, and Accuracy for given TP, FP, FN, TN counts."""
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        total = tp + fp + fn + tn
        accuracy = (tp + tn) / total if total > 0 else 0.0

        return {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "accuracy": round(accuracy, 4),
        }

    @staticmethod
    def summarize_per_type(type_counts: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
        """Computes metrics per entity category."""
        summary = {}
        for etype, counts in type_counts.items():
            summary[etype] = MetricsCalculator.calculate_entity_metrics(
                tp=counts.get("tp", 0),
                fp=counts.get("fp", 0),
                fn=counts.get("fn", 0),
                tn=counts.get("tn", 0),
            )
        return summary
