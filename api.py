import time
from pathlib import Path
from typing import Dict, List, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from inference import analyze
from interpreter import interpret_poem_mlx


class AnalyzeRequest(BaseModel):
    poem: str = ""
    title: str = ""
    poet: str = ""


class AnalyzeResponse(BaseModel):
    predictions: Dict[str, List[Tuple[str, float]]]
    interpretation: str
    duration_seconds: float
    word_count: int


app = FastAPI(title="VerseLens API")


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_poem(request: AnalyzeRequest) -> AnalyzeResponse:
    poem = request.poem.strip()
    if not poem:
        raise HTTPException(
            status_code=400,
            detail="Poem text is required. Please provide a non-empty poem.",
        )

    started = time.perf_counter()
    predictions = analyze(poem, k=5, threshold=0.3)
    interpretation = interpret_poem_mlx(
        poem,
        request.title,
        request.poet,
        analysis=predictions,
    )

    return AnalyzeResponse(
        predictions=predictions,
        interpretation=interpretation,
        duration_seconds=round(time.perf_counter() - started, 2),
        word_count=len(interpretation.split()),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": f"Analysis failed: {exc}"},
    )


frontend_dir = Path(__file__).parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")