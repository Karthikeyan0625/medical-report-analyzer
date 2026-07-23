# Vitals — Universal Medical Report Analyzer

Upload any medical report — blood test (PDF), X-ray, CT scan, or MRI scan —
and the system detects what kind of report it is, routes it to the right
model, and returns a plain-language result with a disease flag or a
current-health summary.

**Status: Week 1 scaffold.** Router, API contract, and UI are wired end-to-end.
The imaging models (X-ray/CT/MRI) run on untrained weights until you train
and drop `.pt` files into `backend/app/models/weights/` — see Roadmap below.

## Stack
- **Backend**: FastAPI, EasyOCR + pdfplumber (lab reports), PyTorch/ResNet18 (imaging), pydicom (CT/MRI DICOM handling)
- **Frontend**: React + Vite
- **Database**: Firebase Firestore (report history) + Firebase Storage (optional file retention)

## Project structure
```
medreport-analyzer/
├── backend/
│   └── app/
│       ├── main.py                  # FastAPI entrypoint
│       ├── routers/upload.py        # POST /api/analyze-report
│       ├── services/
│       │   ├── type_detector.py     # decides lab / xray / ct / mri
│       │   ├── ocr_service.py       # blood report OCR + parsing
│       │   ├── imaging_service.py   # CNN inference for scans
│       │   └── firebase_service.py  # save/read report history
│       ├── utils/dicom_utils.py     # DICOM -> PNG conversion
│       └── models/weights/          # trained .pt files go here
└── frontend/
    └── src/
        ├── App.jsx                  # upload -> analyzing -> result flow
        ├── components/
        │   ├── UploadZone.jsx
        │   ├── ResultPanel.jsx
        │   └── PulseLine.jsx        # signature animated trace
        └── api.js                   # calls the backend
```

## Running locally

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Open http://localhost:5173 — uploads go to the backend at http://localhost:8000.

### Firebase (optional for Week 1, needed once you want history)
1. Create a project at https://console.firebase.google.com
2. Project Settings → Service Accounts → Generate new private key
3. Save the JSON as `backend/app/firebase_credentials.json` (already gitignored)

## API contract
`POST /api/analyze-report` — multipart form, field name `file`

Response (unified shape regardless of report type):
```json
{
  "report_type": "xray",
  "disease_detected": true,
  "disease_name": "pneumonia",
  "confidence": 0.91,
  "key_findings": "Model detected signs consistent with pneumonia (confidence 91.0%)",
  "disclaimer": "This is an AI-assisted screening tool and NOT a medical diagnosis..."
}
```
Lab reports return `extracted_values` and `flags` instead of `confidence`.

## Roadmap
- **Week 2**: Train/validate the lab-report marker parser against real sample report formats
- **Week 3**: Train X-ray CNN (Kaggle Chest X-Ray Pneumonia) → drop weights at `models/weights/xray_resnet18.pt`
- **Week 4-5**: Train CT CNN (Kaggle Lung CT Scan / COVID-19 CT) → `ct_resnet18.pt`
- **Week 6**: Train MRI CNN (Kaggle Brain MRI Tumor) → `mri_resnet18.pt`
- **Week 7**: Replace the rule-based image-type detector with a trained 4-class classifier
- **Week 8**: Firebase history panel + trend view on the frontend
- **Week 9-10**: Deploy backend (Render/Railway) + frontend (Vercel), polish, demo video

## Disclaimer
This project is a decision-support/educational screening tool, not a diagnostic
device. It is not a substitute for professional medical advice.
