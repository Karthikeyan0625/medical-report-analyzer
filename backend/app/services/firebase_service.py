"""
Firebase Service
----------------
Stores each analyzed report's result in Firestore.
Uses Render Environment Variable (FIREBASE_CREDENTIALS)
for production deployment.
"""

from datetime import datetime, timezone
import os
import json

import firebase_admin
from firebase_admin import credentials, firestore


_db = None


def _get_db():
    """
    Initialize Firebase once and return Firestore database client.
    """

    global _db

    if _db is None:

        # Initialize Firebase only once
        if not firebase_admin._apps:

            firebase_json = os.getenv("FIREBASE_CREDENTIALS")

            if firebase_json:
                # Render Environment Variable
                cred_dict = json.loads(firebase_json)
                cred = credentials.Certificate(cred_dict)

            else:
                # Local development fallback
                cred = credentials.Certificate(
                    "app/firebase_credentials.json"
                )

            firebase_admin.initialize_app(cred)

        _db = firestore.client()

    return _db


def save_report_result(
    filename: str,
    report_type: str,
    result: dict,
    user_id: str = "demo_user"
) -> str:
    """
    Saves analyzed report result into Firestore.
    """

    db = _get_db()

    doc_ref = db.collection("reports").document()

    doc_ref.set({
        "user_id": user_id,
        "filename": filename,
        "report_type": report_type,
        "result": result,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    return doc_ref.id


def get_report_history(
    user_id: str,
    limit: int = 20
):
    """
    Fetch user's previous analyzed reports.
    """

    db = _get_db()

    query = (
        db.collection("reports")
        .where("user_id", "==", user_id)
        .order_by(
            "created_at",
            direction=firestore.Query.DESCENDING
        )
        .limit(limit)
    )

    records = []

    for doc in query.stream():
        record = doc.to_dict()
        record["id"] = doc.id
        records.append(record)

    return records