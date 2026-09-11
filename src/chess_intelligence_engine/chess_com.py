import requests

#This function fetches the latest game PGN from chess.com for a given username.
def fetch_latest_game_pgn(username: str) -> str:

    headers = {"User-Agent": "ChessIntelligenceEngine/0.1 (learning project)"}
    
    username = username.strip()

    if not username:
        raise ValueError("Username invalid.")

    response = requests.get(f"https://api.chess.com/pub/player/{username}/games/archives", headers=headers, timeout=10)
    response.raise_for_status()
    
    data = response.json()

    archive_list = data["archives"]

    if not archive_list:
        raise ValueError("No archives in user history!")

    latest_archive_url = archive_list[-1]

    second_response = requests.get(latest_archive_url, headers=headers, timeout=10)
    second_response.raise_for_status()

    archive_data = second_response.json()

    games = archive_data["games"]

    if not games:
        raise ValueError("No games in archive history.")

    latest_game = games[-1]

    pgn = latest_game["pgn"]

    if not isinstance(pgn, str) or not pgn.strip():
        raise ValueError("No PGN in latest game.")

    return pgn
