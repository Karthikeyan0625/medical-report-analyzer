"""
DICOM Utilities
-----------------
Converts a .dcm (DICOM) file into a normal image array/file that a
standard CNN (trained on jpg/png datasets) can consume.

Why this is needed:
  Real hospital scans (CT/MRI) are usually exported as DICOM, not jpg/png.
  Kaggle training datasets are pre-converted to jpg/png for convenience,
  but a production-realistic project should still handle raw DICOM input
  gracefully -- this is a strong interview talking point.

Install:
    pip install pydicom numpy pillow
"""

import numpy as np
import pydicom
from PIL import Image


def dicom_to_pil_image(dicom_path: str) -> Image.Image:
    ds = pydicom.dcmread(dicom_path)
    pixel_array = ds.pixel_array.astype(float)

    # Normalize to 0-255 range (DICOM pixel intensities can vary widely
    # depending on the scanner and windowing settings)
    pixel_min = pixel_array.min()
    pixel_max = pixel_array.max()
    if pixel_max - pixel_min == 0:
        normalized = np.zeros_like(pixel_array)
    else:
        normalized = (pixel_array - pixel_min) / (pixel_max - pixel_min)

    image_8bit = (normalized * 255).astype(np.uint8)
    return Image.fromarray(image_8bit)


def dicom_to_file(dicom_path: str, output_path: str) -> str:
    """Convert and save as .png so the standard CNN preprocessing pipeline
    (same one used for X-ray) can be reused without modification."""
    img = dicom_to_pil_image(dicom_path)
    img = img.convert("L")  # ensure grayscale, consistent with most scan CNNs
    img.save(output_path)
    return output_path


def get_dicom_modality(dicom_path: str) -> str:
    """Reads just the header (fast) to know if it's a CT or MRI scan."""
    ds = pydicom.dcmread(dicom_path, stop_before_pixels=True)
    return getattr(ds, "Modality", "UNKNOWN")  # e.g. "CT", "MR"
