# AI-Based Fake Identity & Document Screening System (SIH26188)

A modular, explainable security screening system designed to detect fraudulent, expired, blacklisted, and structurally invalid identity and travel documents.

---

## 🏛️ System Architecture

The overall system is divided into independent, decoupled pipeline modules:

```
[Document Image]
       │
       ▼
┌──────────────┐
│   Module 1   │  OCR Extraction & Document Classification
│ (ocr_module) │  Extracts raw text, detects MRZ zones, outputs canonical fields
└──────┬───────┘
       │ Structured OCR JSON
       ▼
┌─────────────────────┐
│      Module 2       │  Document Validation Engine
│(document_validation)│  Deterministic format, date logic, ICAO MRZ checksums,
└──────┬──────────────┘  blacklist/watchlist lookups, and duplicate detection
       │
       ▼ Validation Report (Flags, Status, Explanations)
┌─────────────────────┐
│  Risk Scoring Engine│  Combines Module 2 validation with Module 3 tampering
│   (Downstream)      │  and Module 4 face verification for holistic risk assessment
└─────────────────────┘
```

---

## 🚀 Module 2: Document Validation Engine

Module 2 provides rule-based, deterministic, explainable document screening with **zero external dependencies**.

### Key Capabilities
- **Format Validation**: Enforces official country-specific patterns (e.g., Indian Passport `^[A-Z][0-9]{7}$`), allowed character sets, and flags suspicious placeholder numbers (`00000000`, `12345678`).
- **Date Logic Verification**: Chronological validation (`DOB` $\le$ `Issue Date` $<$ `Expiry Date`), realistic human lifespan checks (0–130 years), leap year calendar handling (`2024-02-29`), and visa stay duration analysis.
- **ICAO Doc 9303 Checksum Engine**: Calculates mathematical modulus-10 7-3-1 weight check digits for TD3 passports (Document Number, DOB, Expiry, and Composite check digits), and cross-verifies MRZ data against OCR text.
- **Mock Border Security Database**: Local SQLite repository seeded with synthetic records for blacklisted documents (`X9988776`), watchlist identities (`VIKRAM SINGH`), and duplicate identity detection (`ELENA ROSTOVA`).
- **Privacy & PII Protection**: Automatically masks sensitive identifiers (`M8*****4`), redacts names in audit logs, and computes SHA-256 identity tokens.

---

## 🧪 Testing & Verification

### Run Automated Unit Tests (30 Tests)
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Run Accuracy & Precision Evaluation Report
```bash
python tests/run_test_report.py
```

### Run Built-in Live Demonstration
```bash
python -m document_validation.cli --demo
```

### Validate a Document via CLI
```bash
# Valid Passport
python -m document_validation.cli --input docs/contract_examples/valid_passport.json

# Blacklisted Passport
python -m document_validation.cli --input docs/contract_examples/blacklisted_document.json

# Expired Document
python -m document_validation.cli --input docs/contract_examples/expired_document.json
```

---

## 📁 Repository Structure

```
├── .gitignore
├── README.md
├── app.py                             # Optional Flask API demonstration
├── document_validator.py              # Backward-compatibility adapter
├── test_validator.py                  # Adapter test script
├── ocr_module/                        # Module 1: OCR Extraction & Classification
│   └── pipeline.py
├── document_validation/               # Module 2: Document Validation Engine
│   ├── cli.py                         # Standalone command-line interface
│   ├── config.py                      # Validation configuration manager
│   ├── engine.py                      # Core orchestration engine
│   ├── core/                          # Normalizer, rule registry, privacy utils
│   ├── models/                        # Input contract, result model, flags
│   ├── validators/                    # Format, date, MRZ, expiry, standards, duplicates
│   └── database/                      # SQLite repository, seeder, mock_border.db
├── tests/                             # Comprehensive automated test suite
│   ├── test_validation_suite.py
│   └── run_test_report.py
└── docs/                              # Detailed specifications & contract examples
    ├── MODULE_2_SPECIFICATION.md
    └── contract_examples/
```

---

## 📜 Documentation
For detailed input/output contracts, JSON schemas, flag definitions, and integration guides, see:
- [docs/MODULE_2_SPECIFICATION.md](docs/MODULE_2_SPECIFICATION.md)
