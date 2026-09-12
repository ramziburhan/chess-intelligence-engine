import io
import chess.pgn

#This function takes in a PGN string and outputs a list of FEN strings. 

def pgn_to_board_positions(pgn: str) -> list[str]:
    if not isinstance(pgn, str) or not pgn.strip():
        raise ValueError("PGN must be a nonempty string.")

    game = chess.pgn.read_game(io.StringIO(pgn))

    if game is None:
        raise ValueError("No game found in PGN.")

    if game.errors:
        raise ValueError("PGN contains parsing errors.")

    board = game.board()
    positions = [board.fen()]

    for move in game.mainline_moves():
        board.push(move)
        positions.append(board.fen())

    if len(positions) == 1:
        raise ValueError("Game contains no moves.")
    
    return positions
