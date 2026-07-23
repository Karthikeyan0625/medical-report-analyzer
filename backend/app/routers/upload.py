"""
Upload + History Router
--------------------------
POST /api/analyze-report  -> analyze one uploaded report (auth required)
GET  /api/history         -> the logged-in user's past reports (auth required)

Both routes require a Firebase ID token: Authorization: Bearer <token>.
The frontend attaches this automatically once the user is signed in.
"""

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.services.type_detector import detect_report_type, ReportType
from app.services.ocr_service import analyze_lab_report
from app.services.imaging_service import analyze_scan
from app.utils.dicom_utils import dicom_to_file
from app.services import firebase_service
from app.services.auth import get_current_user_id

router = APIRouter()

UPLOAD_DIR = Path("app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/analyze-report")
async def analyze_report(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id)):
    file_ext = Path(file.filename).suffix.lower()
    temp_filename = f"{uuid.uuid4().hex}{file_ext}"
    temp_path = UPLOAD_DIR / temp_filename

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        report_type = detect_report_type(str(temp_path))

        if report_type == ReportType.UNKNOWN:
            raise HTTPException(
                status_code=422,
                detail="Could not determine report type. Please upload a blood test "
                       "(PDF), or an X-ray/CT/MRI scan image.",
            )

        if report_type == ReportType.LAB_REPORT:
            result = analyze_lab_report(str(temp_path))

        elif report_type in (ReportType.CT_SCAN, ReportType.MRI_SCAN) and file_ext == ".dcm":
            converted_path = UPLOAD_DIR / f"{temp_filename}_converted.png"
            dicom_to_file(str(temp_path), str(converted_path))
            result = analyze_scan(str(converted_path), report_type.value)

        else:
            result = analyze_scan(str(temp_path), report_type.value)

        try:
            firebase_service.save_report_result(
                filename=file.filename,
                report_type=report_type.value,
                result=result,
                user_id=user_id,
            )
        except Exception as e:
            print(f"[warn] Failed to save report to Firebase: {e}")

        return result

    finally:
        temp_path.unlink(missing_ok=True)


@router.get("/history")
async def get_history(user_id: str = Depends(get_current_user_id)):
    """Returns the signed-in user's past analyzed reports, most recent first."""
    try:
        records = firebase_service.get_report_history(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load history: {e}")
    return {"reports": records}
