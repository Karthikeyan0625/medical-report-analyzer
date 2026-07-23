"""
Imaging Service - X-ray / CT / MRI Classification
----------------------------------------------------
Each modality gets its own fine-tuned model (same base architecture,
different training data). This file loads whichever model matches the
detected report type and runs inference.

Install:
    pip install torch torchvision pillow
"""

from pathlib import Path
from typing import Dict

from PIL import Image
import torch
from torchvision import transforms, models

from app.services.disease_info import get_disease_info, NO_FINDING_INFO

# Map report type -> weights file, class labels (order MUST match training),
# and which label(s) mean "nothing abnormal found".
MODEL_CONFIG = {
    "xray": {
        "weights_path": "app/models/weights/xray_resnet18.pt",
        "labels": ["normal", "pneumonia"],
        "normal_labels": {"normal"},
    },
    "ct_scan": {
        "weights_path": "app/models/weights/ct_resnet18.pt",
        "labels": ["covid", "normal"],
        "normal_labels": {"normal"},
    },
    "mri_scan": {
        "weights_path": "app/models/weights/mri_resnet18.pt",
        "labels": ["glioma", "meningioma", "notumor", "pituitary"],
        "normal_labels": {"notumor"},
    },
}

IMAGE_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

_loaded_models: Dict[str, torch.nn.Module] = {}


def _load_model(report_type: str) -> torch.nn.Module:
    if report_type in _loaded_models:
        return _loaded_models[report_type]

    config = MODEL_CONFIG[report_type]
    num_classes = len(config["labels"])

    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)

    weights_path = Path(config["weights_path"])
    if weights_path.exists():
        model.load_state_dict(torch.load(weights_path, map_location="cpu"))
    else:
        print(f"[warn] No trained weights found at {weights_path}, using untrained model.")

    model.eval()
    _loaded_models[report_type] = model
    return model


def analyze_scan(file_path: str, report_type: str) -> dict:
    config = MODEL_CONFIG[report_type]
    model = _load_model(report_type)

    image = Image.open(file_path).convert("RGB")
    input_tensor = IMAGE_TRANSFORM(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
        top_idx = int(torch.argmax(probabilities))
        confidence = float(probabilities[top_idx])

    predicted_label = config["labels"][top_idx]
    disease_detected = predicted_label not in config["normal_labels"]

    info = get_disease_info(predicted_label) if disease_detected else NO_FINDING_INFO

    return {
        "report_type": report_type,
        "disease_detected": disease_detected,
        "disease_name": predicted_label if disease_detected else None,
        "confidence": round(confidence, 4),
        "description": info["description"],
        "consult": info["consult"],
        "disclaimer": (
            "This is an AI-assisted screening tool and NOT a medical diagnosis. "
            "Please consult a licensed doctor for interpretation and treatment."
        ),
    }
