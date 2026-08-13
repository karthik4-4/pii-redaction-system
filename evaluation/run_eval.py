import json
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.document.reader import DocumentReader
from app.detection.engine import PIIDetectionEngine
from evaluation.evaluator import Evaluator
from evaluation.report import ReportGenerator

def main():
    print("Extracting document blocks from Red Herring Prospectus.docx...")
    doc = DocumentReader("data/input/Red Herring Prospectus.docx")
    blocks = doc.extract_blocks()

    gt = json.load(open("evaluation/ground_truth.json", encoding="utf-8"))
    gt_texts = [item["text"] for item in gt]

    # Evaluate on blocks containing ground truth sections & context
    candidate_blocks = [b for b in blocks if any(t in b.text for t in gt_texts)]
    print(f"Evaluated Candidate Blocks: {len(candidate_blocks)} / {len(blocks)}")

    print("Executing PII Detection Engine...")
    engine = PIIDetectionEngine()
    cand_detections = engine.detect_document(candidate_blocks)

    all_entities = []
    for entities in cand_detections.values():
        all_entities.extend(entities)

    print(f"Total Detected Entities in Evaluated Sections: {len(all_entities)}")

    evaluator = Evaluator("evaluation/ground_truth.json")
    results = evaluator.evaluate(all_entities)

    print("\n=================================================================")
    print("           QUANTITATIVE EVALUATION RESULTS SUMMARY               ")
    print("=================================================================")
    print(f"Precision : {results['overall']['precision']*100:.1f}%")
    print(f"Recall    : {results['overall']['recall']*100:.1f}%")
    print(f"F1 Score  : {results['overall']['f1']*100:.1f}%")
    print(f"Accuracy  : {results['overall']['accuracy']*100:.1f}%")
    print("-----------------------------------------------------------------")
    print(f"True Positives (TP) : {results['matched_tp']}")
    print(f"False Positives (FP): {results['false_positives']}")
    print(f"False Negatives (FN): {results['false_negatives']}")
    print("=================================================================\n")

    # Generate Markdown Report
    ReportGenerator.generate_report(results, "evaluation_report.md")
    print("Updated 'evaluation_report.md' successfully.")

if __name__ == "__main__":
    main()
