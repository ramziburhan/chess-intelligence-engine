# Chess Intelligence Engine

A Python project for learning backend engineering through chess analysis.
The current local pipeline retrieves a player's latest available archived
Chess.com game, parses its PGN into board positions, and evaluates those
positions with Stockfish.

The included benchmark and JSON export scripts use a saved sample game.
They do not fetch a username's latest game when run.

## Setup on macOS

**Prerequisite:** Homebrew installed on macOS. If you do not have it, follow
the [official Homebrew installation instructions](https://brew.sh/), including
the installer's "Next steps" to configure your shell. Verify installation:

```bash
brew --version
```

The steps below install uv, Stockfish, and the project's Python environment.
The project selects Python 3.12 through `.python-version`.

Install uv and the standalone Stockfish executable:

```bash
brew install uv stockfish
```

From the repository root, install the project and its Python dependencies:

```bash
uv sync
```

Find the Stockfish executable:

```bash
command -v stockfish
```

Set `engine_path` in both `scripts/benchmark_analysis.py` and
`scripts/export_analysis.py` to the returned path. Both scripts currently use
`/opt/homebrew/bin/stockfish`. This is configured in the scripts, not in
Homebrew. The recorded baseline used Stockfish 19; a newer installation may
produce different evaluations and timings.

## Run the benchmark

Run all commands from the repository root so relative file paths resolve
correctly:

```bash
uv run python scripts/benchmark_analysis.py
```

The script reads `benchmarks/games/baseline.pgn` once and performs three
analysis runs. Each run reports:

- Positions analyzed: 57, including the starting position.
- Node limit: 10,000 per position.
- Elapsed seconds and positions analyzed per second.
- The sample game's Chess.com URL.

Each run uses one Stockfish search thread and one engine process shared
across its positions. Timing includes engine startup, analysis, and shutdown;
it excludes PGN loading, parsing, and printing. The initial recorded median
was 53.70 positions per second. Performance depends on the machine, engine
version, workload, and system activity.

## Export an analysis report

```bash
uv run python scripts/export_analysis.py
```

The script analyzes the same saved game and writes
`outputs/baseline_analysis.json`, creating its parent directory if needed.
An existing report at that path is overwritten.

The report includes game metadata, 57 indexed FEN positions with evaluations,
and the engine name, thread count, and node budget. Scores use White's
perspective and distinguish centipawn and mate values, preserve search-bound
flags, and identify positions that are already checkmate.

The script reads the JSON back and prints `True` when it matches the original
report dictionary. Generated reports belong in the ignored `outputs/`
directory; the saved benchmark PGN remains tracked for reproducibility.

## Current scope and limitations

- Username-based retrieval is available through
  `fetch_latest_game_pgn` in `src/chess_intelligence_engine/chess_com.py`;
  the scripts currently operate on the fixed local PGN.
- Evaluation quality at the 10,000-node budget has not been validated.
  Search bounds are retained and must not be treated as exact estimates.
- Standalone FEN positions do not preserve repetition history.
- The evaluation's `winner` field identifies a winner through checkmate
  only. `None` does not establish that a position is a draw or that the game
  is ongoing; the PGN result is recorded separately.
- Win-probability loss and aggregate opening, game-phase, and clock-pressure
  reports are not implemented yet.

See [docs/PROJECT.md](docs/PROJECT.md) for the architecture, development phases,
and recorded performance baseline.
