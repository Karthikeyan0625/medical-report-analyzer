"""
Type Detector Service
----------------------
Decides what kind of medical report was uploaded, so the request
can be routed to the correct downstream pipeline:

    - "lab_report"  -> OCR + classical ML  (blood test, CBC, lipid panel, etc.)
    - "xray"        -> CNN pipeline
    - "ct_scan"     -> CNN pipeline (+ DICOM handling if .dcm)
    - "mri_scan"    -> CNN pipeline

Detection strategy (simple, explainable -- good for a resume project
because you can defend every rule in an interview):

1. File extension check first (cheap, fast).
   - .pdf / .csv / .txt / .docx            -> almost always a lab report
   - .dcm                                  -> CT or MRI (DICOM header tells you which)
   - .jpg / .jpeg / .png                   -> ambiguous, needs image inspection

2. For ambiguous images, run a lightweight pretrained image classifier
   (a small CNN you fine-tune on a 4-class dataset: xray / ct / mri / lab-scan-image)
   OR, as a fast MVP, use image characteristics:
   - Lab reports scanned as images tend to have high text density (OCR confidence high)
   - X-rays/CT/MRI are mostly grayscale, low text density

For the MVP (Week 1), we keep this rule-based + a stub for the ML classifier,
so the API works end-to-end before the real classifier is trained.
"""

from enum import Enum
from pathlib import Path

import pydicom

from app.services.modality_classifier import predict_modality


class ReportType(str, Enum):
    LAB_REPORT = "lab_report"
    XRAY = "xray"
    CT_SCAN = "ct_scan"
    MRI_SCAN = "mri_scan"
    UNKNOWN = "unknown"


TEXT_BASED_EXTENSIONS = {".pdf", ".csv", ".txt", ".docx"}
DICOM_EXTENSIONS = {".dcm"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def detect_from_dicom(file_path: str) -> ReportType:
    """DICOM files carry metadata that tells us the modality directly."""
    try:
        ds = pydicom.dcmread(file_path, stop_before_pixels=True)
        modality = getattr(ds, "Modality", "").upper()
        if modality == "CT":
            return ReportType.CT_SCAN
        if modality == "MR":
            return ReportType.MRI_SCAN
        if modality in ("CR", "DX"):
            return ReportType.XRAY
    except Exception:
        pass
    return ReportType.UNKNOWN


MODALITY_TO_REPORT_TYPE = {
    "xray": ReportType.XRAY,
    "ct_scan": ReportType.CT_SCAN,
    "mri_scan": ReportType.MRI_SCAN,
}


def detect_from_image_content(file_path: str) -> ReportType:
    """
    Uses the trained ResNet18 modality classifier (xray vs ct_scan today;
    mri_scan once that model is trained) to decide what kind of scan this is.
    Falls back to XRAY if the classifier weights aren't available yet, so
    the API keeps working before/while models are being trained.
    """
    predicted_modality = predict_modality(file_path)
    return MODALITY_TO_REPORT_TYPE.get(predicted_modality, ReportType.XRAY)


def detect_report_type(file_path: str) -> ReportType:
    ext = Path(file_path).suffix.lower()

    if ext in TEXT_BASED_EXTENSIONS:
        return ReportType.LAB_REPORT

    if ext in DICOM_EXTENSIONS:
        result = detect_from_dicom(file_path)
        if result != ReportType.UNKNOWN:
            return result
        # Fall back to image content check if DICOM metadata is missing
        return detect_from_image_content(file_path)

    if ext in IMAGE_EXTENSIONS:
        return detect_from_image_content(file_path)

    return ReportType.UNKNOWN
