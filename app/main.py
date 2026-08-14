"""
Main CLI entry point for the PII Redaction & Pseudonymization System.
"""

import sys
import os
import yaml
import logging
import argparse
from typing import Dict, Any

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.document.reader import DocumentReader
from app.document.writer import DocumentWriter
from app.detection.engine import PIIDetectionEngine
from app.anonymization.synthetic_data import SyntheticDataGenerator
from app.anonymization.policy import PrivacyPolicy
from app.anonymization.replacement_manager import ReplacementManager
from app.validation.validator import OutputValidator
from evaluation.evaluator import Evaluator
from evaluation.report import ReportGenerator

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("pii_redaction")

def load_config(config_path: str) -> Dict[str, Any]:
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    logger.warning(f"Config file '{config_path}' not found. Using defaults.")
    return {}

def run_pipeline(
    input_path: str,
    output_path: str,
    config_path: str = "config.yaml",
    ground_truth_path: str = "evaluation/ground_truth.json",
    report_output: str = "evaluation_report.md",
    run_evaluation: bool = True,
):
    """Executes full PII detection, pseudonymization, document writing, validation, and evaluation pipeline."""
    logger.info("=================================================================")
    logger.info("Starting PII Redaction & Pseudonymization Pipeline")
    logger.info("=================================================================")
    logger.info(f"Input Document : {input_path}")
    logger.info(f"Output Document: {output_path}")

    # 1. Load Configuration
    config = load_config(config_path)
    spacy_model = config.get("spacy_model", "en_core_web_lg")
    faker_cfg = config.get("faker", {})
    thresholds = {k: v.get("threshold", 0.65) for k, v in config.get("entities", {}).items()}

    # 2. Extract Document Blocks from DOCX (paragraphs, tables, headers, footers)
    logger.info("Step 1: Reading and parsing Word document XML runs...")
    reader = DocumentReader(input_path)
    blocks = reader.extract_blocks()
    logger.info(f"Successfully extracted {len(blocks)} text blocks across document paragraphs and tables.")

    # 3. Detect PII Entities via Presidio + spaCy + Custom Recognizers + Context Rules
    logger.info("Step 2: Executing PII Detection Engine (Presidio + spaCy NER + Context Rules)...")
    detector = PIIDetectionEngine(spacy_model=spacy_model, thresholds=thresholds)
    block_detections = detector.detect_document(blocks)

    all_detected_entities = []
    for block_id, entities in block_detections.items():
        all_detected_entities.extend(entities)

    logger.info(f"Detection complete: Found {len(all_detected_entities)} total PII entity instances.")

    # 4. Generate Referentially Consistent Synthetic Replacements
    logger.info("Step 3: Generating consistent synthetic replacements via Privacy Policy...")
    synth_gen = SyntheticDataGenerator(seed=faker_cfg.get("seed", 42), locale=faker_cfg.get("locale", "en_IN"))
    policy = PrivacyPolicy(synth_gen)
    replacement_mgr = ReplacementManager(policy)
    replacement_map = replacement_mgr.process_entities(block_detections)

    logger.info(f"Created {len(replacement_map)} unique entity pseudonymization mappings.")

    # 5. Write Pseudonymized DOCX Output
    logger.info("Step 4: Reconstructing DOCX file with pseudonymized values...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    writer = DocumentWriter(reader.doc)
    count = writer.apply_replacements(blocks, block_detections, replacement_map)
    writer.save(output_path)
    logger.info(f"Saved redacted document to '{output_path}' with {count} replaced text spans.")

    # 6. Validate Output Document Privacy Integrity
    logger.info("Step 5: Running post-redaction privacy leakage validation scan...")
    validator = OutputValidator(detector)
    val_result = validator.validate_file(output_path, replacement_map)
    logger.info(f"Validation Result: Passed={val_result['passed']}, Residual Detections={val_result['residual_detections']}")

    # 7. Run Quantitative Evaluation & Generate Report
    if run_evaluation and os.path.exists(ground_truth_path):
        logger.info("Step 6: Running Quantitative Evaluation against Ground Truth dataset...")
        evaluator = Evaluator(ground_truth_path)
        gt_texts = [item["text"] for item in evaluator.ground_truth]
        candidate_blocks = [b for b in blocks if any(t in b.text for t in gt_texts)]

        cand_detections = detector.detect_document(candidate_blocks)
        eval_entities = []
        for entities in cand_detections.values():
            eval_entities.extend(entities)

        eval_results = evaluator.evaluate(eval_entities)
        ReportGenerator.generate_report(eval_results, report_output)
        logger.info(f"Evaluation report written to '{report_output}'.")
        
        overall = eval_results.get("overall", {})
        logger.info("=================================================================")
        logger.info(f"EVALUATION SUMMARY | Precision: {overall.get('precision', 0)*100:.1f}% | Recall: {overall.get('recall', 0)*100:.1f}% | F1: {overall.get('f1', 0)*100:.1f}% | Accuracy: {overall.get('accuracy', 0)*100:.1f}%")
        logger.info("=================================================================")

    logger.info("Pipeline execution completed successfully.")

def main():
    parser = argparse.ArgumentParser(description="PII Redaction & Pseudonymization System for DOCX Documents")
    parser.add_argument("--input", "-i", default="data/input/Red Herring Prospectus.docx", help="Path to input DOCX file")
    parser.add_argument("--output", "-o", default="data/output/redacted_output.docx", help="Path to output redacted DOCX file")
    parser.add_argument("--config", "-c", default="config.yaml", help="Path to YAML configuration file")
    parser.add_argument("--ground-truth", "-g", default="evaluation/ground_truth.json", help="Path to ground truth JSON file")
    parser.add_argument("--report-out", "-r", default="evaluation_report.md", help="Path to output Markdown evaluation report")
    parser.add_argument("--no-evaluate", action="store_true", help="Disable evaluation run")

    args = parser.parse_args()

    run_pipeline(
        input_path=args.input,
        output_path=args.output,
        config_path=args.config,
        ground_truth_path=args.ground_truth,
        report_output=args.report_out,
        run_evaluation=not args.no_evaluate,
    )

if __name__ == "__main__":
    main()
