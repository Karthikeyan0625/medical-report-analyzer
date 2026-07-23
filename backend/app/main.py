"""
Universal Medical Report Analyzer - Backend Entry Point
---------------------------------------------------------
Run with: uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload

app = FastAPI(
    title="Universal Medical Report Analyzer",
    description="Upload any medical report (blood test, X-ray, CT, MRI) and get an AI-assisted health analysis.",
    version="0.1.0",
)

# Allow the React dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000","https://medical-report-analyzer-ebon.vercel.app","https://medical-report-analyzer-git-main-karthikeyan6.vercel.app","https://medical-report-analyzer-mjlss7o53-karthikeyan6.vercel.app/"],  # Vite / CRA dev ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["reports"])


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Medical Report Analyzer API is running"}
