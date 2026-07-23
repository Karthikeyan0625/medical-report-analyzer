"""
Firebase Service
------------------
Stores each analyzed report's result in Firestore so the dashboard
can show history / trends over time. Uploaded files themselves (if you
want to keep them) go to Firebase Storage.

Setup steps:
  1. Go to https://console.firebase.google.com -> create a project
  2. Project settings -> Service accounts -> "Generate new private key"
     Save the downloaded JSON as backend/app/firebase_credentials.json
     (add this file to .gitignore -- never commit it)
  3. pip install firebase-admin
"""

from datetime import datetime, timezone
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

_db = None

CREDENTIALS_PATH = Path(__file__).resolve().parents[1] / "firebase_credentials.json"


def _get_db():
    global _db
    if _db is None:
        if not CREDENTIALS_PATH.exists():
            raise RuntimeError(
                f"Firebase credentials not found at {CREDENTIALS_PATH}. "
                "Download it from Firebase Console -> Project Settings -> Service Accounts."
            )
        cred = credentials.Certificate(str(CREDENTIALS_PATH))
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db


def save_report_result(filename: str, report_type: str, result: dict, user_id: str = "demo_user") -> str:
    """Saves one analyzed report to the `reports` collection. Returns the doc ID."""
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


def get_report_history(user_id: str, limit: int = 20):
    """Fetches the most recent reports for the dashboard's history tab."""
    db = _get_db()
    query = (
        db.collection("reports")
        .where("user_id", "==", user_id)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
    )
    records = []
    for doc in query.stream():
        record = doc.to_dict()
        record["id"] = doc.id
        records.append(record)
    return records
