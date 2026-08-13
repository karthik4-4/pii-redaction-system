import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.document.reader import DocumentReader
from app.detection.engine import PIIDetectionEngine
from evaluation.evaluator import Evaluator

doc = DocumentReader("data/input/Red Herring Prospectus.docx")
blocks = doc.extract_blocks()

gt = json.load(open("evaluation/ground_truth.json", encoding="utf-8"))
gt_texts = [item["text"] for item in gt]

candidate_blocks = [b for b in blocks if any(t in b.text for t in gt_texts)]

engine = PIIDetectionEngine()
cand_detections = engine.detect_document(candidate_blocks)

all_entities = []
for entities in cand_detections.values():
    all_entities.extend(entities)

evaluator = Evaluator("evaluation/ground_truth.json")
results = evaluator.evaluate(all_entities)

print("--- MISSED GROUND TRUTH (False Negatives) ---")
matched_gt_indices = set()
matched_det_indices = set()

for gt_idx, item in enumerate(evaluator.ground_truth):
    gt_text = item["text"].strip().lower()
    gt_type = item["type"]

    match_found = False
    for det_idx, det in enumerate(all_entities):
        if det_idx in matched_det_indices:
            continue
        det_text = det.text.strip().lower()
        det_type = det.entity_type

        if (gt_text in det_text or det_text in gt_text) and (gt_type == det_type or evaluator._types_compatible(gt_type, det_type)):
            matched_gt_indices.add(gt_idx)
            matched_det_indices.add(det_idx)
            match_found = True
            break

    if not match_found:
        print(f"FN: '{item['text']}' ({item['type']})")

print("\n--- FALSE POSITIVES IN EVALUATED SECTIONS ---")
for det_idx, det in enumerate(all_entities):
    if det_idx not in matched_det_indices:
        det_text = det.text.strip().lower()
        is_cand = any((det_text in gt_item["text"].strip().lower() or gt_item["text"].strip().lower() in det_text) for gt_item in evaluator.ground_truth)
        if is_cand:
            print(f"FP: '{det.text}' ({det.entity_type}, score={det.confidence:.2f})")
