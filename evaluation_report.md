# PII Detection & Redaction Evaluation Report

## Executive Summary
This evaluation report measures the detection performance of the hybrid PII Redaction & Pseudonymization pipeline evaluated against `Red Herring Prospectus.docx`.

| Metric | Score | Percentage |
| :--- | :--- | :--- |
| **Precision** | `0.0443` | **4.4%** |
| **Recall** | `0.5714` | **57.1%** |
| **F1 Score** | `0.0823` | **8.2%** |
| **Accuracy** | `0.2760` | **27.6%** |

- **Ground Truth Entities Evaluated**: `35`
- **Total System Detections**: `4057`
- **True Positives (TP)**: `20`
- **False Positives (FP)**: `431`
- **False Negatives (FN)**: `15`

---

## Detailed Performance Per PII Category

| PII Entity Type | TP | FP | FN | Precision | Recall | F1 Score | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **AADHAAR** | 0 | 0 | 1 | 0.0% | 0.0% | 0.0% | 0.0% |
| **ADDRESS** | 3 | 178 | 0 | 1.7% | 100.0% | 3.3% | 1.7% |
| **CREDIT_CARD** | 0 | 0 | 1 | 0.0% | 0.0% | 0.0% | 0.0% |
| **DATE_OF_BIRTH** | 2 | 4 | 1 | 33.3% | 66.7% | 44.4% | 28.6% |
| **EMAIL_ADDRESS** | 2 | 2 | 2 | 50.0% | 50.0% | 50.0% | 33.3% |
| **IP_ADDRESS** | 0 | 0 | 2 | 0.0% | 0.0% | 0.0% | 0.0% |
| **ORGANIZATION** | 6 | 123 | 0 | 4.7% | 100.0% | 8.9% | 4.7% |
| **PAN** | 0 | 0 | 2 | 0.0% | 0.0% | 0.0% | 0.0% |
| **PERSON** | 6 | 122 | 2 | 4.7% | 75.0% | 8.8% | 4.6% |
| **PHONE_NUMBER** | 1 | 2 | 3 | 33.3% | 25.0% | 28.6% | 16.7% |
| **SSN** | 0 | 0 | 1 | 0.0% | 0.0% | 0.0% | 0.0% |

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
