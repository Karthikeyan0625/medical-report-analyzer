"""
Disease Info Lookup
----------------------
Central place for the "2-line description + who to consult" text shown
in the dashboard for every possible model output. Keeping this separate
from the model-serving code means updating wording later doesn't touch
any inference logic.
"""

DISEASE_INFO = {
    # ---- X-ray ----
    "pneumonia": {
        "description": (
            "The X-ray shows patterns (cloudy/white patches in the lung fields) "
            "commonly associated with pneumonia, a lung infection that inflames "
            "the air sacs."
        ),
        "consult": "Pulmonologist or General Physician",
    },

    # ---- CT Scan ----
    "covid": {
        "description": (
            "The CT scan shows lung patterns (ground-glass opacities) that are "
            "commonly seen in COVID-19 related lung involvement."
        ),
        "consult": "Physician / Infectious Disease Specialist",
    },

    # ---- MRI (Brain Tumor, 4-class) ----
    "glioma": {
        "description": (
            "The MRI shows a mass pattern consistent with a glioma, a tumor that "
            "arises from the brain's glial (supportive) cells."
        ),
        "consult": "Neurologist / Neuro-oncologist",
    },
    "meningioma": {
        "description": (
            "The MRI shows a mass pattern consistent with a meningioma, a tumor "
            "arising from the membranes surrounding the brain and spinal cord."
        ),
        "consult": "Neurologist / Neurosurgeon",
    },
    "pituitary": {
        "description": (
            "The MRI shows a mass pattern consistent with a pituitary tumor, "
            "located in the gland that regulates several of the body's hormones."
        ),
        "consult": "Endocrinologist / Neurosurgeon",
    },

    # ---- Lab markers (blood report) ----
    "glucose_high": {
        "description": "Blood glucose is above the typical fasting range, which can be an early sign of prediabetes or diabetes.",
        "consult": "Endocrinologist / General Physician",
    },
    "glucose_low": {
        "description": "Blood glucose is below the typical range, which can cause dizziness, fatigue, or fainting if untreated.",
        "consult": "General Physician",
    },
    "cholesterol_high": {
        "description": "Total cholesterol is above the recommended range, which can raise the risk of heart disease over time.",
        "consult": "Cardiologist / General Physician",
    },
    "hemoglobin_low": {
        "description": "Hemoglobin is below the typical range, which can indicate anemia and may cause fatigue or weakness.",
        "consult": "General Physician / Hematologist",
    },
    "hemoglobin_high": {
        "description": "Hemoglobin is above the typical range, which can sometimes relate to dehydration or other underlying conditions.",
        "consult": "General Physician",
    },
    "wbc_high": {
        "description": "White blood cell count is elevated, which often points to an infection or inflammation in the body.",
        "consult": "General Physician",
    },
    "wbc_low": {
        "description": "White blood cell count is below the typical range, which can affect the body's ability to fight infection.",
        "consult": "General Physician / Hematologist",
    },
    "ldl_high": {
        "description": "LDL ('bad' cholesterol) is above the recommended range, a known risk factor for heart disease.",
        "consult": "Cardiologist",
    },
    "triglycerides_high": {
        "description": "Triglycerides are above the recommended range, which is linked to increased cardiovascular risk.",
        "consult": "Cardiologist / General Physician",
    },
}


NO_FINDING_INFO = {
    "description": "No abnormal patterns were detected in this report based on the current model.",
    "consult": None,
}


def get_disease_info(key: str) -> dict:
    """Looks up description + who-to-consult text for a disease/marker key.
    Falls back to a generic message if the key isn't in the lookup yet
    (keeps the API safe against new model classes before this file is updated)."""
    return DISEASE_INFO.get(key, {
        "description": f"The model flagged a finding ({key}) that needs clinical review.",
        "consult": "General Physician",
    })
