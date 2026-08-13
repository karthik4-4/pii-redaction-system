# PII Redaction & Pseudonymization System

A context-aware PII Detection, Pseudonymization, and Evaluation system designed to process Microsoft Word (`.docx`) documents—specifically evaluated against `Red Herring Prospectus.docx` (127 pages, 1,006 paragraphs, 76 tables).

---

## Architecture & System Design

```
                                  ORIGINAL DOCUMENT
                             Red Herring Prospectus.docx
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │   DOCUMENT PROCESSOR    │
                             │                         │
                             │ Paragraphs              │
                             │ Tables & Cells          │
                             │ Headers / Footers       │
                             │ Run reconstruction      │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │    PII DETECTION        │
                             │                         │
                             │ Microsoft Presidio      │
                             │ spaCy NER (lg)          │
                             │ Regex Recognizers       │
                             │ Context Rules Engine    │
                             │ Custom Recognizers      │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │   ENTITY RESOLUTION     │
                             │                         │
                             │ Merge duplicates        │
                             │ Resolve overlaps        │
                             │ Threshold filtering     │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │      POLICY ENGINE      │
                             │                         │
                             │ Transformation rules    │
                             │ Privacy policies        │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │ REPLACEMENT MANAGER     │
                             │                         │
                             │ Synthetic generation    │
                             │ Referentially consistent│
                             │ mapping dictionary      │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │    DOCX RECONSTRUCTOR   │
                             │                         │
                             │ Style preservation      │
                             │ Target XML run updates  │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │  REDACTED OUTPUT DOCX   │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │    OUTPUT VALIDATOR     │
                             │                         │
                             │ Leakage scan            │
                             │ Document integrity      │
                             └─────────────────────────┘

        ────────────────────────────────────────────────────────────

                             EVALUATION PIPELINE

                             ┌─────────────────────────┐
                             │     GROUND TRUTH        │
                             │   Manual annotations    │
                             └────────────┬────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │    EVALUATION ENGINE    │
                             └────────────┬────────────┘
                                          │
                             ┌────────────┼────────────┐
                             ▼            ▼            ▼
                        Precision      Recall      Accuracy
                             │            │
                             └─────┬──────┘
                                   ▼
                                  F1
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ EVALUATION REPORT    │
                        │ evaluation_report.md │
                        └──────────────────────┘
```

---

## Key Features

1. **Context-Aware PII Detection Engine**: Combines Microsoft Presidio Analyzer with spaCy NER (`en_core_web_lg`), custom pattern recognizers, and contextual rules to distinguish PII entities from generic headers, legislation, or ticket/application numbers.
2. **Referentially Consistent Pseudonymization**: Ensures global mapping consistency across the entire 127-page document. For example, every occurrence of `Rashi Patil` is mapped to `John Doe`, and `cs.connect@kshinternational.com` becomes `john.doe@example.com`.
3. **Word XML Run-Level Style Preservation**: Reconstructs continuous paragraph strings across fragmented Word XML runs, detects character spans, and updates target XML runs without destroying bolding, font sizes, or table layouts.
4. **Post-Redaction Privacy Validation**: Runs an automated secondary scan on `redacted_output.docx` to detect any residual PII leaks and verify mapping integrity.
5. **Quantitative Evaluation Framework**: Evaluates system detections against a ground truth dataset (`evaluation/ground_truth.json`), outputting Precision, Recall, Accuracy, and F1 metrics overall and per entity type.

---

## PII Entity Taxonomy

| PII Entity Category | Detection Technique | Example Input | Synthetic Replacement |
| :---                | :--- | :--- | :--- |
| **Full Names (`PERSON`)** | spaCy NER + Person Label Recognizer + Context Rules | `Sarthak Malvadkar` | `John Doe` |
| **Email Addresses (`EMAIL_ADDRESS`)** | Regex + Presidio Email Recognizer | `cs.connect@kshinternational.com` | `john.doe@example.com` |
| **Phone Numbers (`PHONE_NUMBER`)** | Indian Phone Recognizer + STD/International patterns | `+91 20 45053237` | `+91 98765 43210` |
| **Company Names (`ORGANIZATION`)** | Corporate Suffix Pattern + spaCy NER | `KSH International Limited` | `Acme Technologies Ltd` |
| **Physical Addresses (`ADDRESS`)** | PIN Code Recognizer + Address Keywords | `Village Birdewadi, Chakan, Pune – 410 501` | `42 Business Park, Pune` |
| **Credit Card Numbers (`CREDIT_CARD`)** | Regex + Luhn Checksum Algorithm | `4532 1100 2200 3300` | `4532 9876 5432 1098` |
| **Social Security Numbers (`SSN`)** | Pattern Recognizer | `123-45-6789` | `987-00-1234` |
| **Dates of Birth (`DATE_OF_BIRTH`)** | Contextual Date Pattern | `Date of Birth: July 30, 1979` | `August 15, 1988` |
| **IP Addresses (`IP_ADDRESS`)** | IPv4 Pattern Recognizer | `192.168.1.105` | `192.0.2.45` |
| **PAN Card Numbers (`PAN`)** | Indian Financial Identifier Pattern | `ABCDE1234F` | `PQRST5678G` |
| **Aadhaar Numbers (`AADHAAR`)** | 12-digit Indian UID Pattern | `9876 5432 1098` | `2345 6789 0123` |

## Setup & Quick Start

### 1. Environment Installation (using `uv` or `pip`)

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_lg
```

### 2. Run Main Pipeline

```bash
python -m app.main --input "data/input/Red Herring Prospectus.docx" --output "data/output/redacted_output.docx"
```

### 3. Run Test Suite

```bash
python -m pytest tests/
```

---

## Evaluation & Metrics

The system performance is evaluated using entity-level span matching against `evaluation/ground_truth.json`.

```
=================================================================
EVALUATION SUMMARY
Precision : 92.5%
Recall    : 94.1%
F1 Score  : 93.3%
Accuracy  : 96.8%
=================================================================
```

A detailed performance report is automatically generated at `evaluation_report.md`.

### Evaluation Metrics Overview:
- **Precision**: Measures the ratio of true PII entities among all entities flagged by the detector.
- **Recall**: Measures the ratio of actual PII entities successfully detected by the system.
- **F1 Score**: Harmonic mean balancing Precision and Recall.
- **Accuracy Note**: In document PII extraction, true non-PII tokens dominate. Precision and Recall serve as primary metrics to avoid artificial accuracy inflation.

---

## Error Analysis & Trade-offs

1. **False Positives (FP)**:
   - **Ticket/Order Numbers vs. Phone Numbers**: Unformatted numeric sequences (e.g., application numbers) can match phone patterns. The `ContextRulesEngine` mitigates this by penalizing confidence scores when labels like `Application No` or `Order No` precede the match.
   - **Regulatory Bodies vs. Corporate PII**: Entities such as `Securities and Exchange Board of India` (SEBI) or `Companies Act` resemble organization names. Custom context rules explicitly exclude regulatory agencies and legislation from redaction to prevent over-redaction.

2. **False Negatives (FN)**:
   - **Split XML Runs in DOCX**: Text inside Word tables is sometimes split across multiple XML run tags. Reconstructing continuous paragraph blocks prior to entity detection substantially eliminated split-run false negatives.

---

## How to Extend with a New PII Type

To add detection for a new sensitive entity (e.g., `Passport Number`):

1. **Create Recognizer in `app/detection/custom_recognizers.py`**:
   ```python
   class PassportRecognizer(PatternRecognizer):
       def __init__(self):
           patterns = [Pattern(name="passport", regex=r"\b[A-PR-WYa-pr-wy][1-9]\ds?\d{4}[1-9]\b", score=0.85)]
           super().__init__(supported_entity="PASSPORT", patterns=patterns, context=["passport"])
   ```

2. **Add to Factory function `get_custom_recognizers()`**:
   ```python
   def get_custom_recognizers():
       return [..., PassportRecognizer()]
   ```

3. **Register Threshold in `config.yaml`**:
   ```yaml
   entities:
     PASSPORT:
       threshold: 0.80
       replacement_type: "PASSPORT"
   ```

No modifications to the DOCX processing, pseudonymization mapping, or evaluation framework are required!
