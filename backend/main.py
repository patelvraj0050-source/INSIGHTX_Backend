from __future__ import annotations

import io
import os
import sys
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ai_business_analyst import answer_question  # noqa: E402

app = FastAPI(
    title="INSIGHTX API",
    version="0.6.0",
    description="Production-oriented API layer for the INSIGHTX analytics platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.getenv("INSIGHTX_ALLOWED_ORIGINS", "*").split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_dataset: Optional[pd.DataFrame] = None
_dataset_name: Optional[str] = None


class QuestionRequest(BaseModel):
    question: str


def _require_dataset() -> pd.DataFrame:
    if _dataset is None or _dataset.empty:
        raise HTTPException(status_code=400, detail="Upload a non-empty CSV dataset first.")
    return _dataset


@app.get("/health")
def health():
    return {"status": "ok", "service": "insightx-api", "version": "0.6.0"}


@app.get("/dataset")
def dataset_info():
    df = _require_dataset()
    return {
        "name": _dataset_name,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": [str(c) for c in df.columns],
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }


@app.post("/dataset/upload")
async def upload_dataset(file: UploadFile = File(...)):
    global _dataset, _dataset_name

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        loaded = pd.read_csv(io.BytesIO(raw))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {exc}") from exc

    if loaded.empty:
        raise HTTPException(status_code=400, detail="The CSV contains no data rows.")

    _dataset = loaded
    _dataset_name = file.filename

    return {
        "message": "Dataset uploaded successfully.",
        "name": _dataset_name,
        "rows": int(len(loaded)),
        "columns": int(len(loaded.columns)),
    }


@app.post("/analyst/ask")
def ask_business_analyst(payload: QuestionRequest):
    df = _require_dataset()
    question = payload.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = answer_question(df, question)
    return {
        "intent": result.intent,
        "confidence": result.confidence,
        "answer": result.answer,
        "evidence": result.evidence,
    }
