"""
OCR Service - Lab / Blood Report Extraction
---------------------------------------------
Pipeline:
  1. Read PDF or image
  2. Run OCR to get raw text
  3. Regex-match known lab markers (glucose, cholesterol, hemoglobin, ...)
  4. Return a structured dict of {marker: value}

Install:
    pip install easyocr pdfplumber pillow
"""

import re
from typing import Dict

import pdfplumber
import easyocr

# Lazy-loaded so the app starts fast; EasyOCR loads model weights on first use
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


# Marker name -> regex pattern that captures the numeric value after it.
# Extend this dict as you encounter more report formats.
LAB_MARKER_PATTERNS = {
    "glucose": r"glucose[^\d]{0,15}(\d+\.?\d*)",
    "cholesterol": r"(?:total\s+)?cholesterol[^\d]{0,15}(\d+\.?\d*)",
    "hemoglobin": r"h(?:a)?emoglobin[^\d]{0,15}(\d+\.?\d*)",
    "wbc": r"(?:wbc|white\s+blood\s+cell)[^\d]{0,15}(\d+\.?\d*)",
    "platelets": r"platelet[^\d]{0,15}(\d+\.?\d*)",
    "hdl": r"hdl[^\d]{0,15}(\d+\.?\d*)",
    "ldl": r"ldl[^\d]{0,15}(\d+\.?\d*)",
    "triglycerides": r"triglyceride[^\d]{0,15}(\d+\.?\d*)",
}

# Reference ranges used to flag whether a value is high / low / normal.
# NOTE: these are simplified, generic adult ranges for demo purposes only,
# not a substitute for lab-provided reference ranges.
NORMAL_RANGES = {
    "glucose": (70, 140),        # mg/dL, fasting
    "cholesterol": (0, 200),     # mg/dL
    "hemoglobin": (13, 17),      # g/dL (generic adult range)
    "wbc": (4000, 11000),        # cells/mcL
    "platelets": (150000, 450000),
    "hdl": (40, 60),
    "ldl": (0, 100),
    "triglycerides": (0, 150),
}


def extract_text_from_pdf(file_path: str) -> str:
    text_chunks = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    return "\n".join(text_chunks)


def extract_text_from_image(file_path: str) -> str:
    reader = _get_reader()
    results = reader.readtext(file_path, detail=0)  # detail=0 -> just the text strings
    return "\n".join(results)


def extract_raw_text(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    return extract_text_from_image(file_path)


def parse_lab_values(raw_text: str) -> Dict[str, float]:
    text_lower = raw_text.lower()
    values = {}
    for marker, pattern in LAB_MARKER_PATTERNS.items():
        match = re.search(pattern, text_lower)
        if match:
            try:
                values[marker] = float(match.group(1))
            except ValueError:
                continue
    return values


def flag_abnormal_values(values: Dict[str, float]) -> Dict[str, str]:
    flags = {}
    for marker, value in values.items():
        low, high = NORMAL_RANGES.get(marker, (None, None))
        if low is None:
            flags[marker] = "unknown_range"
        elif value < low:
            flags[marker] = "low"
        elif value > high:
            flags[marker] = "high"
        else:
            flags[marker] = "normal"
    return flags


def analyze_lab_report(file_path: str) -> dict:
    from app.services.disease_info import get_disease_info, NO_FINDING_INFO

    raw_text = extract_raw_text(file_path)
    values = parse_lab_values(raw_text)
    flags = flag_abnormal_values(values)

    abnormal = {k: v for k, v in flags.items() if v in ("high", "low")}
    disease_detected = len(abnormal) > 0

    # Build one description/consult per abnormal marker, e.g. "glucose_high"
    findings = []
    for marker, status in abnormal.items():
        info = get_disease_info(f"{marker}_{status}")
        findings.append({
            "marker": marker,
            "status": status,
            "value": values[marker],
            "description": info["description"],
            "consult": info["consult"],
        })

    return {
        "report_type": "lab_report",
        "extracted_values": values,
        "flags": flags,
        "disease_detected": disease_detected,
        "findings": findings,
        "description": (
            f"{len(findings)} value(s) outside the normal range were found."
            if disease_detected else NO_FINDING_INFO["description"]
        ),
        "consult": findings[0]["consult"] if findings else None,
        "disclaimer": (
            "This is an AI-assisted screening tool and NOT a medical diagnosis. "
            "Please consult a licensed doctor for interpretation and treatment."
        ),
    }
