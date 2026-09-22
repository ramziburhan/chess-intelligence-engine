# Holds the FastAPI application, request model, and endpoint
# FastAPI will define the endpoint and validate requests

from fastapi import FastAPI
from pydantic import BaseModel, Field
from pathlib import Path
from chess_intelligence_engine.game_analysis import analysis_report
from chess_intelligence_engine.exceptions import InvalidPGNError
from fastapi import HTTPException

app = FastAPI()

class AnalysisRequest(BaseModel):
    pgn: str = Field(min_length=1)

@app.post("/analyses")
def creates_analysis(request: AnalysisRequest):
    try:
        analysis = analysis_report(request.pgn, "/opt/homebrew/bin/stockfish", 10000)
        return analysis
    except InvalidPGNError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
