import chess
import chess.engine

def analyze_position(fen: str, engine_path: str, node_limit: int):
    if not isinstance(fen, str) or not fen.strip():
        raise ValueError("FEN must be a nonempty string.")
    if not isinstance(engine_path, str) or not engine_path.strip():
        raise ValueError("Engine path must be a nonempty string.")
    if not isinstance(node_limit, int) or node_limit < 1 or isinstance(node_limit, bool):
        raise ValueError("Node limit must be a positive integer.")

    board = chess.Board(fen)
    if not board.is_valid():
        raise ValueError("Board position failed validity check.")

    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        limit = chess.engine.Limit(nodes=node_limit)
        info = engine.analyse(board, limit)

    white_score = info["score"].white()
    score = {"perspective": "white"}
    if white_score.is_mate() == True:
        score["mate_value"] = white_score.mate()
    if white_score.is_mate() == False:
        score["cp_value"] = white_score.score()
    upperbound = info.get("upperbound", False)
    lowerbound = info.get("lowerbound", False)
    if info["score"].turn == chess.BLACK:
        upperbound, lowerbound = lowerbound, upperbound

    score["upperbound"] = upperbound
    score["lowerbound"] = lowerbound

    return score