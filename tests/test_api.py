from fastapi.testclient import TestClient
from chess_intelligence_engine.api import app
import chess_intelligence_engine.api as api_module
import pytest
from threading import BoundedSemaphore

def test_empty_pgn_returns_422(monkeypatch):
    monkeypatch.setenv("STOCKFISH_PATH", "/test/stockfish")
    with TestClient(app) as client:
        response = client.post("/analyses", json={"pgn": ""})
        assert response.status_code == 422
        assert any(
            error["loc"] == ["body", "pgn"]
            and error["type"] == "string_too_short"
            for error in response.json()["detail"]
        )

def test_whitespace_pgn_returns_422(monkeypatch):
    monkeypatch.setenv("STOCKFISH_PATH", "/test/stockfish")
    with TestClient(app) as client:
        response = client.post("/analyses", json={"pgn": "  "})
        assert response.status_code == 422
        decoded_response = response.json()
        error_message = decoded_response["detail"]
        assert error_message == "PGN not able to parse."

def test_illegal_move_returns_422(monkeypatch):
    monkeypatch.setenv("STOCKFISH_PATH", "/test/stockfish")
    with TestClient(app) as client:
        response = client.post("/analyses", json={"pgn": "1. e4 e5 2. Bh6 *"})
        assert response.status_code == 422
        decoded_response = response.json()
        error_message = decoded_response["detail"]
        assert error_message == "PGN contains parsing errors."

def test_valid_pgn_returns_report(monkeypatch):
    monkeypatch.setenv("STOCKFISH_PATH", "/test/stockfish")
    with TestClient(app) as client:
        fake_report = {"pgn": "1. e4 e5"}
        def fake_analysis_report(pgn, engine_path, node_limit):
            assert pgn == "1. e4 e5"
            assert engine_path == "/test/stockfish"
            assert node_limit == 10000

            return fake_report
        monkeypatch.setattr(api_module, "analysis_report", fake_analysis_report)
        response = client.post("/analyses", json={"pgn": "1. e4 e5"})
        assert response.status_code == 200
        assert response.json() == fake_report

def test_analysis_failure_returns_500(monkeypatch):
    monkeypatch.setenv("STOCKFISH_PATH", "/test/stockfish")
    with TestClient(app, raise_server_exceptions=False) as client:
        def fake_analysis_report(pgn, engine_path, node_limit):
            raise RuntimeError("Internal engine failure.")
        monkeypatch.setattr(api_module, "analysis_report", fake_analysis_report)
        response = client.post("/analyses", json={"pgn": "1. e4 e5"})
        assert response.status_code == 500
        assert "Internal engine failure." not in response.text

def test_missing_stockfish_path_prevents_startup(monkeypatch):
    monkeypatch.delenv("STOCKFISH_PATH", raising=False)
    with pytest.raises(RuntimeError, match="STOCKFISH_PATH is not set"):
        with TestClient(app):
            pass

@pytest.mark.parametrize("path", ["", "   ", "\t\n"])
def test_blank_stockfish_path_prevents_startup(monkeypatch, path):
    monkeypatch.setenv("STOCKFISH_PATH", path)
    with pytest.raises(RuntimeError, match="STOCKFISH_PATH must not be empty or whitespace."):
        with TestClient(app):
            pass 

def test_analysis_failure_release_slot(monkeypatch):
    monkeypatch.setenv("STOCKFISH_PATH", "/test/stockfish")
    with TestClient(app, raise_server_exceptions=False) as client:
        app.state.analysis_slots = BoundedSemaphore(1)
        def fake_analysis_report(pgn, engine_path, node_limit):
            raise RuntimeError("Internal engine failure.")
        monkeypatch.setattr(api_module, "analysis_report", fake_analysis_report)
        response = client.post("/analyses", json={"pgn": "1. e4 e5"})
        assert response.status_code == 500
        acquired = app.state.analysis_slots.acquire(blocking=False)
        assert acquired is True
        app.state.analysis_slots.release()