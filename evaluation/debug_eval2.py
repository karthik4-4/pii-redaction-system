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

gt_lookup = {gt["text"].strip().lower(): gt["type"] for gt in evaluator.ground_truth}
matched_gt_texts = set()

fps = []
for det in all_entities:
    det_text = det.text.strip().lower()
    det_type = det.entity_type

    matched_gt = None
    for gt_text, gt_type in gt_lookup.items():
        if (gt_text in det_text or det_text in gt_text) and (gt_type == det_type or evaluator._types_compatible(gt_type, det_type)):
            matched_gt = (gt_text, gt_type)
            break

    if matched_gt:
        matched_gt_texts.add(matched_gt[0])
    else:
        fps.append((det.text, det.entity_type, det.confidence))

with open("debug_fps.txt", "w", encoding="utf-8") as out:
    out.write("=== TOP FALSE POSITIVES IN CANDIDATE BLOCKS ===\n")
    for text, etype, conf in fps:
        out.write(f"FP: '{text}' ({etype}, score={conf:.2f})\n")

    out.write("\n=== MISSED GROUND TRUTH (FNs) ===\n")
    for gt_item in evaluator.ground_truth:
        gt_text = gt_item["text"].strip().lower()
        if gt_text not in matched_gt_texts:
            out.write(f"FN: '{gt_item['text']}' ({gt_item['type']})\n")

print("Wrote debug results to debug_fps.txt")
