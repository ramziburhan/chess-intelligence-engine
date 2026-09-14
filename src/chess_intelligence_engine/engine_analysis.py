import chess
import chess.engine

def analyze_position(fen: str, engine: chess.engine.SimpleEngine, node_limit: int):
    if not isinstance(fen, str) or not fen.strip():
        raise ValueError("FEN must be a nonempty string.")
    if not isinstance(node_limit, int) or node_limit < 1 or isinstance(node_limit, bool):
        raise ValueError("Node limit must be a positive integer.")

    board = chess.Board(fen)
    if not board.is_valid():
        raise ValueError("Board position failed validity check.")

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

def analyze_positions(positions: list[str], engine_path: str, node_limit: int):
    if not isinstance(positions, list) or not positions:
        raise TypeError("Positions must be a nonempty list of strings.")
    for index, position in enumerate(positions):
        if not isinstance(position, str) or not position.strip():
            raise ValueError(f"Position {index} in positions must be a nonempty string.")
    if not isinstance(engine_path, str) or not engine_path.strip():
        raise ValueError("Engine path must be a nonempty string.")
    if not isinstance(node_limit, int) or node_limit < 1 or isinstance(node_limit, bool):
        raise ValueError("Node limit must be a positive integer.")

    scores = []
    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
        for position in positions:
            score = analyze_position(position, engine, node_limit)
            scores.append(score)
    return scores