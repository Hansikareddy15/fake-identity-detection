"""End-to-end OCR processing pipeline for identity and travel documents.

Orchestrates:
1. Input decoding (File path, bytes, or NumPy array)
2. Image quality gatekeeper (Blur, brightness, glare, resolution)
3. Document boundary detection and perspective rectification
4. OCR text and MRZ line extraction
5. Multi-feature document classification
6. Field extraction and normalization
7. Confidence scoring and JSON packaging
"""

from datetime import datetime
import os
from pathlib import Path
import time
from typing import Any, Dict, Optional, Union
import cv2
import numpy as np

from .confidence import build_confidence_summary
from .config import (
    DOC_TYPE_PASSPORT,
    DOC_TYPE_UNKNOWN,
    OCRConfig,
    PreprocessingConfig,
    QualityThresholds,
)
from .document_classification import classify_document
from .document_detection import detect_and_align_document
from .exceptions import (
    ImageLoadError,
    ImageQualityError,
    TesseractNotFoundError,
)
from .field_extraction import extract_fields
from .image_quality import assess_image_quality
from .models import BoundingBox, ExtractedField, MRZResult, OCRResult, QualityAssessment
from .mrz_processor import parse_mrz
from .ocr_engine import (
    extract_mrz_text,
    extract_text,
    is_tesseract_available,
)
from .preprocessing import preprocess_for_ocr
from .region_detection import detect_all_regions


class OCRPipeline:
    """Production-grade pipeline for identity document OCR extraction."""

    def __init__(
        self,
        ocr_config: Optional[OCRConfig] = None,
        quality_thresholds: Optional[QualityThresholds] = None,
        preprocessing_config: Optional[PreprocessingConfig] = None,
        strict_quality_gate: bool = False,
    ):
        self.ocr_config = ocr_config or OCRConfig()
        self.quality_thresholds = quality_thresholds or QualityThresholds()
        self.preprocessing_config = preprocessing_config or PreprocessingConfig()
        self.strict_quality_gate = strict_quality_gate

    def load_image(self, image_input: Union[str, Path, bytes, np.ndarray]) -> np.ndarray:
        """Decode image input from file path, raw bytes, or existing NumPy array."""
        if isinstance(image_input, np.ndarray):
            if image_input.size == 0:
                raise ImageLoadError("Supplied NumPy image array is empty.")
            return image_input

        if isinstance(image_input, (bytes, bytearray)):
            nparr = np.frombuffer(image_input, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                raise ImageLoadError("Failed to decode image from byte buffer.")
            return image

        if isinstance(image_input, (str, Path)):
            path_str = str(image_input)
            if not os.path.exists(path_str):
                raise ImageLoadError(f"Image file does not exist: {path_str}")

            # cv2.imread doesn't always support unicode paths on Windows, use imdecode
            with open(path_str, "rb") as f:
                buffer = f.read()
            nparr = np.frombuffer(buffer, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None:
                raise ImageLoadError(f"OpenCV failed to decode image at: {path_str}")
            return image

        raise ImageLoadError(f"Unsupported image input type: {type(image_input)}")

    def process_image(
        self,
        image_input: Union[str, Path, bytes, np.ndarray],
        document_type_hint: Optional[str] = None
    ) -> OCRResult:
        """Execute full OCR extraction pipeline on an input document image.

        Args:
            image_input: File path, bytes, or NumPy image.
            document_type_hint: Optional forced document classification.

        Returns:
            Structured OCRResult containing canonical fields and detailed telemetry.
        """
        start_time = time.time()

        # 1. Load and decode image
        raw_image = self.load_image(image_input)

        # 2. Quality assessment
        quality = assess_image_quality(raw_image, self.quality_thresholds)
        if self.strict_quality_gate and not quality.is_acceptable:
            raise ImageQualityError(
                f"Image failed strict quality checks: {', '.join(quality.warnings)}",
                details=quality.to_dict()
            )

        # 3. Boundary detection and rectification
        aligned_image, _ = detect_and_align_document(raw_image)

        # 4. Preprocessing
        enhanced_gray, binary_img = preprocess_for_ocr(aligned_image, self.preprocessing_config)

        # 5. Region localization
        regions = detect_all_regions(aligned_image)

        # 6. OCR Text & MRZ extraction
        raw_text = ""
        raw_mrz = ""
        mrz_result: Optional[MRZResult] = None

        try:
            # Full text OCR
            raw_text = extract_text(enhanced_gray, psm=self.ocr_config.general_psm, config=self.ocr_config)

            # MRZ region OCR
            if "mrz" in regions:
                _, mrz_crop = regions["mrz"]
                raw_mrz = extract_mrz_text(mrz_crop, config=self.ocr_config)
            else:
                # Search bottom of full text for MRZ lines
                raw_mrz = raw_text

            # 7. MRZ Parsing
            if raw_mrz:
                try:
                    mrz_result = parse_mrz(raw_mrz)
                except Exception:
                    # Fallback: check if MRZ lines are within raw_text
                    try:
                        mrz_result = parse_mrz(raw_text)
                    except Exception:
                        mrz_result = None

        except TesseractNotFoundError:
            raise
        except Exception:
            # If general OCR fails, attempt graceful continuation
            raw_text = raw_text or ""

        # 8. Document Classification
        if document_type_hint:
            doc_type = document_type_hint
            class_conf = 1.0
        else:
            doc_type, class_conf, _ = classify_document(
                raw_text,
                raw_mrz=mrz_result.raw_mrz if mrz_result else None
            )

        # 9. Field Extraction
        fields = extract_fields(doc_type, raw_text, mrz=mrz_result)

        # 10. Confidence Scoring
        conf_summary = build_confidence_summary(fields, quality, mrz_result)

        # 11. Assemble canonical values
        name_val = fields.get("name").value if "name" in fields else ""
        doc_num_val = fields.get("document_number").value if "document_number" in fields else ""
        pass_num_val = fields.get("passport_number").value if "passport_number" in fields else doc_num_val
        nat_val = fields.get("nationality").value if "nationality" in fields else ""
        dob_iso = fields.get("date_of_birth").value if "date_of_birth" in fields else ""
        dob_dmy = fields.get("dob").value if "dob" in fields else ""
        exp_iso = fields.get("date_of_expiry").value if "date_of_expiry" in fields else ""
        exp_dmy = fields.get("expiry").value if "expiry" in fields else ""
        gender_val = fields.get("gender").value if "gender" in fields else "X"
        valid_score = conf_summary.get("valid_score", 0.0)

        elapsed_ms = int((time.time() - start_time) * 1000)

        metadata = {
            "processing_time_ms": elapsed_ms,
            "processed_at": datetime.now().isoformat(),
            "classification_confidence": class_conf,
            "resolution": list(quality.resolution),
            "engine_version": "1.0.0",
        }

        return OCRResult(
            document_type=doc_type,
            name=name_val,
            document_number=doc_num_val,
            passport_number=pass_num_val,
            nationality=nat_val,
            date_of_birth=dob_iso,
            dob=dob_dmy,
            date_of_expiry=exp_iso,
            expiry=exp_dmy,
            gender=gender_val,
            valid_score=valid_score,
            issue_date=fields.get("issue_date").value if "issue_date" in fields else None,
            address=fields.get("address").value if "address" in fields else None,
            fields=fields,
            raw_text=raw_text,
            quality=quality,
            mrz=mrz_result,
            confidence_summary=conf_summary,
            metadata=metadata,
        )
