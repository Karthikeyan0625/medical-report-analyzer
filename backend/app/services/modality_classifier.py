"""
Modality Classifier Service
------------------------------
Loads the trained ResNet18 modality classifier (xray vs ct_scan for now,
mri_scan added once that dataset/training happens) and predicts which
imaging modality an uploaded image belongs to.

This replaces the "always assume xray" stub in type_detector.py with a
real trained model, so any image upload gets routed correctly.
"""

from pathlib import Path
from typing import Optional

import torch
from torchvision import transforms, models
from PIL import Image

WEIGHTS_PATH = Path("app/models/weights/modality_classifier.pt")

# Must match the label order used during training (MODALITY_LABELS dict
# in the training notebook: {"xray": 0, "ct_scan": 1}). Add "mri_scan": 2
# here once the classifier is retrained on 3 classes.
MODALITY_CLASSES = ["xray", "ct_scan"]

IMAGE_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

_model: Optional[torch.nn.Module] = None


def _load_model() -> Optional[torch.nn.Module]:
    global _model
    if _model is not None:
        return _model

    if not WEIGHTS_PATH.exists():
        print(f"[warn] Modality classifier weights not found at {WEIGHTS_PATH}. "
              f"Falling back to 'xray' for all image uploads until trained.")
        return None

    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, len(MODALITY_CLASSES))
    model.load_state_dict(torch.load(WEIGHTS_PATH, map_location="cpu"))
    model.eval()
    _model = model
    return _model


def predict_modality(file_path: str) -> str:
    """Returns one of MODALITY_CLASSES (e.g. 'xray', 'ct_scan'). Defaults to
    'xray' if the classifier isn't trained/available yet, so the API stays
    usable end-to-end even before this model exists."""
    model = _load_model()
    if model is None:
        return "xray"

    image = Image.open(file_path).convert("RGB")
    input_tensor = IMAGE_TRANSFORM(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(input_tensor)
        predicted_idx = int(torch.argmax(outputs, dim=1))

    return MODALITY_CLASSES[predicted_idx]
