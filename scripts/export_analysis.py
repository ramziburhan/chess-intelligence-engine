import json
from chess_intelligence_engine.game_analysis import analysis_report
from pathlib import Path

data = analysis_report(pgn=Path("benchmarks/games/baseline.pgn").read_text(encoding="utf-8"), 
                        engine_path="/opt/homebrew/bin/stockfish", 
                        node_limit=10000)

output_path = Path("outputs/baseline_analysis.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w") as file:
    json.dump(data, file)
with open(output_path, "r") as file:
    file_data = json.load(file)
if data == file_data:
    print (True)