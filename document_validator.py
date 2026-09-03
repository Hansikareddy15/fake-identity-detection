"""
Compatibility Adapter for Document Validation Module.
Provides backward-compatible interface `validate_document(document)` for legacy callers
while routing all validation logic through the production `DocumentValidationEngine`.
"""
import os
from typing import Any, Dict

from document_validation.config import ValidationConfig
from document_validation.engine import DocumentValidationEngine
from document_validation.models.result_model import ValidationStatus

_SHARED_ENGINE = None


def get_shared_engine() -> DocumentValidationEngine:
    global _SHARED_ENGINE
    if _SHARED_ENGINE is None:
        _SHARED_ENGINE = DocumentValidationEngine()
    return _SHARED_ENGINE


def validate_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backward-compatible entrypoint.
    Executes DocumentValidationEngine and returns both legacy format and modern report.
    """
    doc_copy = dict(document)
    if "document_type" not in doc_copy:
        if "passport_number" in doc_copy:
            doc_copy["document_type"] = "passport"
        elif "visa_number" in doc_copy:
            doc_copy["document_type"] = "visa"
        elif "national_id_number" in doc_copy:
            doc_copy["document_type"] = "national_id"

    engine = get_shared_engine()
    report = engine.validate(doc_copy)

    # Map ValidationStatus to legacy status string
    status_map = {
        ValidationStatus.PASS: "VALID",
        ValidationStatus.FAIL: "INVALID",
        ValidationStatus.WARN: "SUSPICIOUS",
        ValidationStatus.INCOMPLETE: "INCOMPLETE"
    }
    legacy_status = status_map.get(report.overall_status, "INVALID")

    # Estimate representative score for legacy callers
    if report.overall_status == ValidationStatus.PASS:
        legacy_score = int(report.overall_confidence * 100)
    elif report.overall_status == ValidationStatus.WARN:
        legacy_score = 65
    elif report.overall_status == ValidationStatus.INCOMPLETE:
        legacy_score = 30
    else:
        legacy_score = 15

    # Determine tampering level
    tampering_flags = {
        "MRZ_CHECKSUM_INVALID",
        "MRZ_DOCUMENT_NUMBER_MISMATCH",
        "MRZ_DATE_OF_BIRTH_MISMATCH",
        "COUNTRY_FORMAT_MISMATCH",
        "SUSPICIOUS_PLACEHOLDER_NUMBER",
        "EXPIRY_BEFORE_ISSUE"
    }
    flag_set = set(report.flags)
    tamper_intersection = flag_set.intersection(tampering_flags)
    if len(tamper_intersection) >= 2 or "MRZ_CHECKSUM_INVALID" in flag_set:
        tampering_level = "HIGH"
    elif len(tamper_intersection) >= 1:
        tampering_level = "MEDIUM"
    else:
        tampering_level = "LOW"

    return {
        "status": legacy_status,
        "score": legacy_score,
        "issues": report.explanations,
        "tampering_level": tampering_level,
        "flags": report.flags,
        "report": report.to_dict()
    }