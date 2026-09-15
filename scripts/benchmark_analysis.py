import time
import io
import chess.pgn
from chess_intelligence_engine.pgn_parser import pgn_to_board_positions
from chess_intelligence_engine.engine_analysis import analyze_positions
from pathlib import Path

engine_path = "/opt/homebrew/bin/stockfish"
node_limit = 10000
pgn = Path("benchmarks/games/baseline.pgn").read_text(encoding="utf-8")
positions = pgn_to_board_positions(pgn)

game = chess.pgn.read_game(io.StringIO(pgn))
if game is None:
    raise ValueError("PGN not able to parse.")
link = game.headers["Link"]


for i in range(3):
    start = time.perf_counter()
    scores = analyze_positions(positions, engine_path, node_limit)
    end = time.perf_counter()

    number_of_positions = len(scores)
    elapsed = end - start
    throughput = number_of_positions / elapsed

    print(f"Positions analyzed: {number_of_positions}")
    print(f"Node limit per position: {node_limit}")
    print(f"Elapsed seconds: {elapsed}")
    print(f"Positions per second: {throughput}")
    print(f"Game PGN link is: {link}")