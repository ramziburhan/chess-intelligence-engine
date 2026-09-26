import os

def get_stockfish_path():

    stockfish_path = os.environ.get("STOCKFISH_PATH")
    if stockfish_path is None:
        raise RuntimeError("STOCKFISH_PATH is not set.")
    if stockfish_path.strip() == "":
        raise RuntimeError("STOCKFISH_PATH must not be empty or whitespace.")
    
    return stockfish_path