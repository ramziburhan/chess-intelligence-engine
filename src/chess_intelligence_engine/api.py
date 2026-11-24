# Holds the FastAPI application, request model, and endpoint
# FastAPI will define the endpoint and validate requests

from fastapi import FastAPI
from pydantic import BaseModel, Field
from chess_intelligence_engine.game_analysis import analysis_report
from chess_intelligence_engine.exceptions import InvalidPGNError
from fastapi import HTTPException
from contextlib import asynccontextmanager
from chess_intelligence_engine.config import get_stockfish_path
from threading import BoundedSemaphore
from chess_intelligence_engine.config import get_max_concurrent_analyses

@asynccontextmanager
async def lifespan(app: FastAPI):
    limit = get_max_concurrent_analyses()
    app.state.stockfish_path = get_stockfish_path()
    app.state.analysis_slots = BoundedSemaphore(limit)
    yield

app = FastAPI(lifespan=lifespan)

class AnalysisRequest(BaseModel):
    pgn: str = Field(min_length=1)

@app.post("/analyses")
def creates_analysis(request: AnalysisRequest):
    try:
        with app.state.analysis_slots:
            analysis = analysis_report(request.pgn, app.state.stockfish_path, 10000)
        return analysis
    except InvalidPGNError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
