import io
import chess.pgn
from chess_intelligence_engine.pgn_parser import pgn_to_board_positions
from chess_intelligence_engine.engine_analysis import analyze_positions
from chess_intelligence_engine.exceptions import InvalidPGNError

def analysis_report(pgn: str, engine_path: str, node_limit: int):
    game = chess.pgn.read_game(io.StringIO(pgn))
    if game is None:
        raise InvalidPGNError("PGN not able to parse.")

    link = game.headers.get("Link")
    white_player = game.headers["White"]
    black_player = game.headers["Black"]
    result = game.headers["Result"]
    positions = pgn_to_board_positions(pgn)
    engine_analysis = analyze_positions(positions, engine_path, node_limit)
    scores = engine_analysis["scores"]
    analysis_settings = engine_analysis["analysis_settings"]
    if len(positions) != len(scores):
        raise ValueError("Length of positions and scores don't match.")
    
    analysis = {"URL": link, "White player": white_player, "Black player": black_player, "Result": result}
    position_records = []
    for i in range(len(positions)):
        record = {
            "position_index": i,
            "fen": positions[i],
            "evaluation": scores[i]
        }
        position_records.append(record)
    analysis["Positions"] = position_records
    analysis["Analysis settings"] = analysis_settings
    return analysis