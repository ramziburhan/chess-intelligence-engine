import os

def get_stockfish_path():

    stockfish_path = os.environ.get("STOCKFISH_PATH")
    if stockfish_path is None:
        raise RuntimeError("STOCKFISH_PATH is not set.")
    if stockfish_path.strip() == "":
        raise RuntimeError("STOCKFISH_PATH must not be empty or whitespace.")
    return stockfish_path

def get_max_concurrent_analyses() -> int:
    raw_limit = os.environ.get("MAX_CONCURRENT_ANALYSES", "16")
    try:
        limit = int(raw_limit)
    except ValueError:
        raise RuntimeError("MAX_CONCURRENT_ANALYSES must be a positive integer.")
    if limit <= 0:
        raise RuntimeError(f"Expected positive num from MAX_CONCURRENT_ANALYSES, but got {limit}.")
    return limit