"""
Auth Service
--------------
Verifies the Firebase ID token the frontend sends on every request
(Authorization: Bearer <token>), so the backend knows which logged-in
user made the request without trusting anything the client claims.
"""

from fastapi import Header, HTTPException
from firebase_admin import auth as firebase_auth

from app.services.firebase_service import _get_db  # ensures firebase_admin app is initialized


async def get_current_user_id(authorization: str = Header(None)) -> str:
    """FastAPI dependency: reads the Authorization header, verifies the
    Firebase ID token, and returns the user's uid. Raises 401 if missing
    or invalid, so every protected route rejects unauthenticated calls."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")

    _get_db()  # make sure firebase_admin.initialize_app() has run

    id_token = authorization.removeprefix("Bearer ").strip()
    try:
        decoded = firebase_auth.verify_id_token(id_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")

    return decoded["uid"]
