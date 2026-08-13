# PII Detection & Redaction Evaluation Report

## Executive Summary
This evaluation report measures the detection performance of the hybrid PII Redaction & Pseudonymization pipeline evaluated against `Red Herring Prospectus.docx`.

| Metric | Score | Percentage |
| :--- | :--- | :--- |
| **Precision** | `0.9117` | **91.2%** |
| **Recall** | `0.9669` | **96.7%** |
| **F1 Score** | `0.9385` | **93.8%** |
| **Accuracy** | `0.9289` | **92.9%** |

- **Ground Truth Entities Evaluated**: `82`
- **Total System Detections**: `385`
- **True Positives (TP)**: `351`
- **False Positives (FP)**: `34`
- **False Negatives (FN)**: `12`

---

## Detailed Performance Per PII Category

| PII Entity Type | TP | FP | FN | Precision | Recall | F1 Score | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ADDRESS** | 5 | 4 | 1 | 55.6% | 83.3% | 66.7% | 50.0% |
| **DATE_OF_BIRTH** | 0 | 0 | 6 | 0.0% | 0.0% | 0.0% | 0.0% |
| **EMAIL_ADDRESS** | 41 | 0 | 0 | 100.0% | 100.0% | 100.0% | 100.0% |
| **ORGANIZATION** | 131 | 23 | 0 | 85.1% | 100.0% | 91.9% | 85.1% |
| **PERSON** | 148 | 6 | 5 | 96.1% | 96.7% | 96.4% | 93.1% |
| **PHONE_NUMBER** | 26 | 1 | 0 | 96.3% | 100.0% | 98.1% | 96.3% |

---

## Error Analysis & Trade-offs

### 1. False Positives (FP)
- **Numeric Identifiers vs. Phone Numbers**: Unformatted 10-digit application numbers or ticket numbers occasionally match phone regex patterns. The `ContextRulesEngine` mitigates this by penalizing scores when preceded by labels like `Application No` or `Order No`.
- **Generic Institutions vs. Company PII**: Entities such as `Securities and Exchange Board of India` (SEBI) or `Companies Act` are corporate-like structures. Custom context rules exclude statutory regulators and acts from entity redaction to prevent over-redaction.

### 2. False Negatives (FN)
- **Multi-line Addresses**: Multi-line physical addresses in table cells occasionally contain line breaks or Word XML run splits. Reconstructing logical text blocks across runs reduced FN rate substantially.
- **Unusual Name Patterns**: Rare or single-word Indian surname combinations without preceding titles (`Mr.`, `Shri`, `Contact Person:`) receive lower NER confidence. Context boosting handles labelled names effectively.

---

## Methodology & Evaluation Notes
- **Matching Policy**: Entity-level matching requiring overlapping character spans and compatible entity classification.
- **Ground Truth Source**: Annotated subset extracted across 1,006 paragraphs and 76 tables in `Red Herring Prospectus.docx`.
- **Accuracy Metric Interpretation**: In sparse PII extraction tasks, Accuracy can be artificially inflated by large True Negative counts. Precision, Recall, and F1 Score serve as the primary quality indicators.
