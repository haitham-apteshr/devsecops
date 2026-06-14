"""
FastAPI AI Security Service — called by Jenkins (like SonarQube), not built during CI.
Run locally:  uvicorn ai_api:app --host 0.0.0.0 --port 8000
"""
import base64
import json
import os
import tempfile
from typing import Optional, Union

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ai_dast import analyze_dast_findings
from ai_parsers import parse_dast_report, parse_sonar_report
from ai_sast import analyze_sast_findings
from ai_utils import create_pdf_report, validate_api_key

app = FastAPI(
    title="DevSecOps AI Security Service",
    description="External AI engine for SAST/DAST analysis. Jenkins posts scan reports here.",
    version="2.0.0",
)


class HealthResponse(BaseModel):
    status: str
    groq: str
    message: str


class AnalyzeResponse(BaseModel):
    scan_type: str
    summary: Optional[str]
    findings: list
    scanner: Optional[str] = None
    pdf_filename: Optional[str] = None
    pdf_base64: Optional[str] = None


@app.get("/health", response_model=HealthResponse)
def health():
    ok, msg = validate_api_key()
    return HealthResponse(
        status="ok" if ok else "degraded",
        groq="connected" if ok else "error",
        message=msg if ok else f"Groq unavailable: {msg}",
    )


@app.get("/")
def root():
    return {
        "service": "DevSecOps AI Security API",
        "health": "/health",
        "docs": "/docs",
        "endpoints": {
            "sast": "POST /api/v1/analyze/sast",
            "dast": "POST /api/v1/analyze/dast",
        },
    }


def _encode_pdf(path: str) -> tuple[str, str]:
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return os.path.basename(path), encoded


def _load_json_upload(raw: bytes) -> Union[dict, list]:
    try:
        return json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON report: {exc}") from exc


@app.post("/api/v1/analyze/sast", response_model=AnalyzeResponse)
async def analyze_sast(
    report: UploadFile = File(..., description="SonarQube JSON report"),
    max_issues: int = Query(10, ge=1, le=20),
    include_summary: bool = Query(True),
    include_pdf: bool = Query(True),
):
    raw = await report.read()
    data = _load_json_upload(raw)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as tmp:
        json.dump(data, tmp)
        tmp_path = tmp.name

    try:
        issues = parse_sonar_report(tmp_path)
    finally:
        os.unlink(tmp_path)

    if not issues:
        raise HTTPException(status_code=400, detail="No SonarQube issues found in report.")

    results, summary = analyze_sast_findings(
        issues, max_issues=max_issues, include_summary=include_summary
    )

    pdf_name = None
    pdf_b64 = None
    if include_pdf and results:
        pdf_name = "ai_sast_report.pdf"
        create_pdf_report(
            "AI-Enhanced SAST Security Analysis Report",
            results,
            pdf_name,
            executive_summary=summary,
        )
        pdf_name, pdf_b64 = _encode_pdf(pdf_name)

    return AnalyzeResponse(
        scan_type="SAST",
        summary=summary,
        findings=results,
        pdf_filename=pdf_name,
        pdf_base64=pdf_b64,
    )


@app.post("/api/v1/analyze/dast", response_model=AnalyzeResponse)
async def analyze_dast(
    report: UploadFile = File(..., description="Nuclei or ZAP JSON report"),
    max_issues: int = Query(10, ge=1, le=20),
    include_summary: bool = Query(True),
    include_pdf: bool = Query(True),
):
    raw = await report.read()
    data = _load_json_upload(raw)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8") as tmp:
        json.dump(data, tmp)
        tmp_path = tmp.name

    try:
        findings, scanner = parse_dast_report(tmp_path)
    finally:
        os.unlink(tmp_path)

    if not findings:
        raise HTTPException(status_code=400, detail="No DAST findings detected (Nuclei/ZAP format).")

    results, summary = analyze_dast_findings(
        findings,
        max_issues=max_issues,
        include_summary=include_summary,
        scanner=scanner.upper(),
    )

    pdf_name = None
    pdf_b64 = None
    if include_pdf and results:
        pdf_name = "ai_dast_report.pdf"
        create_pdf_report(
            f"AI-Enhanced {scanner.upper()} Pentest Report",
            results,
            pdf_name,
            executive_summary=summary,
        )
        pdf_name, pdf_b64 = _encode_pdf(pdf_name)

    return AnalyzeResponse(
        scan_type="DAST",
        summary=summary,
        findings=results,
        scanner=scanner,
        pdf_filename=pdf_name,
        pdf_base64=pdf_b64,
    )
