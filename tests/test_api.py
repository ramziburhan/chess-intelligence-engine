from fastapi.testclient import TestClient
from chess_intelligence_engine.api import app
import chess_intelligence_engine.api as api_module

client = TestClient(app)

def test_empty_pgn_returns_422():
    response = client.post("/analyses", json={"pgn": ""})
    assert response.status_code == 422

def test_whitespace_pgn_returns_422():
    response = client.post("/analyses", json={"pgn": "  "})
    assert response.status_code == 422
    decoded_response = response.json()
    error_message = decoded_response["detail"]
    assert error_message == "PGN not able to parse."

def test_illegal_move_returns_422():
    response = client.post("/analyses", json={"pgn": "1. e4 e5 2. Bh6 *"})
    assert response.status_code == 422
    decoded_response = response.json()
    error_message = decoded_response["detail"]
    assert error_message == "PGN contains parsing errors."

def test_valid_pgn_returns_report(monkeypatch):
    fake_report = {"pgn": "1. e4 e5"}
    def fake_analysis_report(pgn, engine_path, node_limit):
        return fake_report
    monkeypatch.setattr(api_module, "analysis_report", fake_analysis_report)
    response = client.post("/analyses", json={"pgn": "1. e4 e5"})
    assert response.status_code == 200
    assert response.json() == fake_report

def test_analysis_failure_returns_500(monkeypatch):
    client = TestClient(app, raise_server_exceptions=False)
    def fake_analysis_report(pgn, engine_path, node_limit):
        raise RuntimeError("Internal engine failure.")
    monkeypatch.setattr(api_module, "analysis_report", fake_analysis_report)
    response = client.post("/analyses", json={"pgn": "1. e4 e5"})
    assert response.status_code == 500
    assert response.text not in "Internal engine failure."