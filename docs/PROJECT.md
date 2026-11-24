# Chess Intelligence Engine

## Objective

Build a system that analyzes a player's public Chess.com game history using
Stockfish and produces an evolving player intelligence profile.

The project is also a vehicle for learning backend engineering, cloud
infrastructure, distributed systems, data engineering, observability, and
practical machine learning.

The architecture should evolve in response to measured limitations rather
than introducing distributed infrastructure prematurely.

## MVP

The initial product answers three questions:

1. Where does the player lose the most win probability: opening, middlegame,
   or endgame?
2. Which openings does the player underperform in when there is sufficient
   data?
3. Does the player's error rate increase as their clock decreases?

Additional analysis features are backlog unless required by the current phase.

## Development Phases

### Phase 0 — Local Monolith

Goal: establish the complete analysis path locally and obtain baseline
performance measurements.

- Fetch public Chess.com game history.
- Parse PGNs.
- Analyze one game locally with Stockfish.
- Produce structured analysis output.
- Measure positions analyzed per second per core.

### Phase 1 — Local Service Decomposition

Goal: introduce service boundaries and persistence after understanding the
local workload.

- FastAPI API service.
- Stockfish worker process.
- Postgres persistence.
- Docker Compose.
- Local queue stand-in.
- Idempotent game processing.

### Phase 2 — AWS Deployment

Goal: distribute the expensive analysis workload and learn production cloud
infrastructure.

Planned components:

- Application Load Balancer → Fargate API.
- RDS Postgres.
- S3.
- SQS with a dead-letter queue.
- Fargate Spot ARM64 Stockfish workers.
- Queue-depth-based autoscaling.
- Worker scale-to-zero.
- Terraform.
- GitHub Actions CI/CD.

Avoid a NAT Gateway unless measurements or requirements justify its cost.

### Phase 3 — Performance and Observability

- Position evaluation cache.
- Performance benchmarks.
- Structured logging.
- Correlation IDs.
- CloudWatch metrics.
- Distributed tracing where useful.
- Deliberate failure testing.

### Phase 4 — Statistical Player Profile

- Aggregate player performance.
- Minimum sample-size thresholds.
- Confidence intervals where appropriate.
- Account for multiple comparisons when evaluating many openings or groups.

### Phase 5 — Blunder Prediction

Predict:

> P(next move loses at least 20 percentage points of win probability)

Candidate pre-move features include:

- Top-3 MultiPV evaluation spread.
- Legal move count.
- Clock remaining.
- Move number.
- Game phase.
- Rating differential.
- Historical blunder rate.

Avoid target leakage:

- Do not use post-move evaluation as an input feature.
- Historical features must use information available before the prediction.
- Do not randomly split individual moves from the same games across train
  and test sets.

Evaluate against explicit baselines using metrics appropriate for an
imbalanced probability prediction problem, including PR-AUC and calibration.

### Phase 6 — LLM Explanation Layer

Use an LLM to explain already-computed evidence rather than invent chess
analysis.

Retrieved evidence should come from our own aggregates and analysis results.

Claims should be traceable to supporting games, including game URL and ply
where applicable.

## Important Technical Decisions

### Stockfish Work Limit

Use node-limited analysis rather than depth-limited analysis.

This provides a more deterministic amount of engine work and makes throughput
measurements and cache identity easier to reason about.

### Position Evaluation

Analyze each position once.

For move `i`, derive evaluation loss from the change between consecutive
position evaluations, normalized to the perspective of the player who made
the move.

### Error Metric

Use loss in win probability as the primary player-facing error metric rather
than raw centipawn loss.

### Distributed Job Granularity

When distributed processing is introduced, the planned unit of queue work is
one game per message.

This decision can be revisited if measurements show that game-level jobs are
too coarse or too fine.

### Position Cache

A future position-evaluation cache must distinguish evaluations by at least:

- Position.
- Stockfish/engine version.
- Node limit.

Position identity should be based on the first four FEN fields so that
irrelevant move counters do not fragment the cache.

### Implementation Language

Use Python throughout the system unless a measured limitation provides a
reason to reconsider.

## Development Principle

Build the simplest version that allows us to learn something or measure
something.

Then:

1. Measure it.
2. Identify the bottleneck or limitation.
3. Introduce the architecture that solves it.
4. Measure again.

The project should tell a story of measured engineering evolution rather than
predetermined complexity.

## Current Status

**Current status:** Phase 0 local prototype complete within the scope and
limitations below. Phase 1 is underway: the synchronous analysis API and its
tests are implemented, and concurrency experiments are informing the next step.

**Completed milestones:**

- Retrieve the latest available archived game PGN for a Chess.com username.
- Parse a PGN into ordered FEN positions, including the starting position.
- Analyze positions with one shared Stockfish process and a per-position node
  budget.
- Return structured centipawn or mate scores from White's perspective,
  preserving upper/lower bounds and reversing their direction when needed.
- Measure local analysis throughput with one search thread.
- Assemble game reports containing game metadata, indexed FEN positions,
  evaluations, and the running engine's name, configured thread count, and
  per-position node budget.
- Identify already-checkmated positions and their winners explicitly,
  distinguishing them from positions with a future forced mate.
- Export reports to JSON, create missing output directories, and verify that
  reading the JSON back reproduces the original report dictionary.
- Save a fixed benchmark PGN and document setup and script usage in the README.

### Phase 0 Completion Review

| Original goal | Evidence and scope |
| --- | --- |
| Fetch public Chess.com game history | Retrieve one latest available archived game through the archive API; bulk history ingestion is not implemented. |
| Parse PGNs | Reconstruct ordered positions, including the starting position, from one game's main line. |
| Analyze one game locally | Reuse one Stockfish process across all positions with a fixed node budget per position. |
| Produce structured output | Export game metadata, position evaluations, checkmate information, and engine settings as JSON. |
| Measure throughput per core | Establish a single-search-thread baseline; CPU affinity and strict per-core throughput were not measured. |

Validation so far includes developer-run successful retrieval and parsing,
invalid-input checks, live centipawn and mate examples, full-game reports,
repeated benchmarks, and JSON round-trip checks. These are not an exhaustive
automated regression suite or a clean-machine setup verification.

**Next step:** Compare server-side analysis concurrency limits of eight and
sixteen against the existing unrestricted 32-request batch. The Phase 1
experiments below show diminishing throughput gains and evidence of CPU
saturation on the local Mac. Win-probability loss and player-profile reports
remain future work, not additional Phase 0 completion requirements.

### Known Limitations

- Each position is reconstructed from a standalone FEN, so Stockfish does not
  receive the played move history needed for repetition-aware analysis.
- Position-level `winner` identifies checkmate winners only. `None` does not
  establish a draw or an ongoing game. Resignation and other game results are
  represented separately by the PGN result; draw reasons are not classified.
- Evaluation quality at 10,000 nodes per position has not been validated.
  Centipawn scores are not win probabilities, and retained search bounds must
  not be treated as exact estimates when deriving move-level changes.
- Reports allow a missing Chess.com-style `Link` header. The local
  scripts read a fixed PGN and use a manually configured Stockfish path; they
  do not expose a username-based command-line interface.
- The prototype targets standard chess; variant-aware analysis has not been
  implemented or validated.

## Initial Phase 0 Performance Baseline

Measured locally on September 14, 2026; results recorded from the developer's
benchmark runs.

| Setting | Value |
| --- | --- |
| Benchmark script | `scripts/benchmark_analysis.py` |
| Game | https://www.chess.com/game/live/174488590032 |
| Engine | Stockfish 19 |
| Search threads | 1, explicitly configured |
| Positions per run | 57, including the starting position |
| Node budget | 10,000 per position |
| Runs | 3, using the same positions fetched and parsed once |

| Run | Elapsed seconds | Positions per second |
| --- | ---: | ---: |
| 1 | 1.272595 | 44.790352 |
| 2 | 1.054902 | 54.033432 |
| 3 | 1.061401 | 53.702589 |

**Median throughput: 53.70 positions per second.** Throughput is the number
of returned evaluations divided by elapsed seconds, measured with
`time.perf_counter()` around `analyze_positions(...)`.

Each run starts one Stockfish process, reuses it for all positions, and closes
it. Timing includes engine startup, analysis, and shutdown; it excludes API
retrieval, PGN parsing, metadata extraction, and printing.

This is a single-search-thread measurement, not a CPU-affinity-controlled
per-core benchmark. It measures completed position evaluations, not
Stockfish's internal search nodes per second. The first run was slower, but
the cause has not been established. These results characterize this game and
search budget; they do not establish evaluation quality or general throughput.
Hardware details beyond the local Mac environment were not recorded.

For comparisons, reuse this game's PGN rather than fetching whatever game is
latest at the time, and record the engine version, thread count, node budget,
and timing scope alongside each result.

### Fixed-File Benchmark Follow-up

The game above is saved at `benchmarks/games/baseline.pgn`. The benchmark now
loads that file once before its three runs, so subsequent account activity
does not change the input. The export script uses the same fixture.

The developer reported the following runs after switching to the saved file,
with the same 57 positions, one search thread, and 10,000-node budget:

| Run | Elapsed seconds | Positions per second |
| --- | ---: | ---: |
| 1 | 1.288224 | 44.246959 |
| 2 | 1.048623 | 54.357004 |
| 3 | 1.063612 | 53.590956 |

**Median throughput: 53.59 positions per second.** This preserves the initial
53.70 baseline above as a separate measurement rather than replacing its
recorded results. Neither batch explains the slower first run or establishes
an application bottleneck.

## Phase 1 Experiment: Concurrent API Requests

Measured locally on October 11, 2026; results supplied by the developer from
`scripts/benchmark_api.py`.

**Question:** Does processing two analysis requests concurrently improve
throughput, and how does it affect individual request latency?

### Setup and Method

- Client and API server run on the same Mac, communicating over localhost.
- One Uvicorn server process, without development reload.
- Each request submits `benchmarks/games/baseline.pgn`: game
  https://www.chess.com/game/live/174488590032, containing 57 positions.
- Stockfish 19, one search thread per analysis, 10,000 nodes per position.
- Each request starts and closes its own Stockfish process.
- Three concurrent pairs are followed by three sequential pairs. Concurrent
  pairs submit both requests before waiting; sequential pairs wait for the
  first response before submitting the second.
- Every response is checked for HTTP 200 and 57 returned position records.

Individual request latency is measured around the HTTP POST, including
receipt of the response body. Batch elapsed time runs from immediately before
the first submission until both results have been retrieved and validated.
Batch throughput is two completed requests divided by batch elapsed seconds.
PGN file reading and printing occur outside these timers.

### Results

| Mode | Pair | Request 1 seconds | Request 2 seconds | Requests per second |
| --- | ---: | ---: | ---: | ---: |
| Concurrent | 1 | 1.135125 | 1.134713 | 1.761667 |
| Concurrent | 2 | 1.152717 | 1.152156 | 1.734759 |
| Concurrent | 3 | 1.157006 | 1.156290 | 1.728380 |
| Sequential | 1 | 1.093349 | 1.102232 | 0.910828 |
| Sequential | 2 | 1.090539 | 1.126912 | 0.901846 |
| Sequential | 3 | 1.096918 | 1.095806 | 0.912016 |

Median batch throughput was **1.735 requests/second concurrent** versus
**0.911 sequential**, approximately **1.90 times higher**. Average individual
request latency was approximately **1.148 seconds concurrent** versus
**1.101 seconds sequential**, about **4.3% longer** (roughly 5%). All 12
requests succeeded and returned 57 positions.

The observed tradeoff is higher aggregate throughput with slightly longer
individual waits. Overlapping requests allows multiple Stockfish processes
to make progress at once. The measurements do not identify the cause of the
small latency increase; resource contention and CPU scheduling or frequency
changes are possible explanations, not established findings.

### Limits and Next Experiment

This experiment covers only three pairs per mode, one game, and one node
budget. Concurrent runs always occurred first, so order effects were not
controlled. Client and server share the same machine; CPU and memory usage
were not measured. These results neither establish maximum capacity nor
justify a specific concurrency limit or queue design.

Next, compare batches of 1, 2, and 4 concurrent requests using the same input
and settings. Record individual latencies, total batch duration, successful
request throughput, and failures. Repeat measurements and vary mode order to
reduce order bias. Look for where additional concurrency gives diminishing
throughput gains while latency rises; no plateau has been demonstrated yet.

### Follow-up: Increasing Concurrent Requests

Subsequent developer-run measurements used the same fixture, engine, node
budget, and localhost setup. The benchmark submits all requests before
collecting their results. It records failures separately and computes
successful throughput as validated responses divided by total batch time.
A stopped-server check recorded connection failures and zero successful
throughput while allowing collection to finish.

The latest repeated comparison rotated batch order: 8/16/4, 16/4/8, then
4/8/16. A single exploratory 32-request batch followed.

| Concurrent requests | Batch throughput, requests/sec (each run) | Median throughput | Individual request range, seconds |
| --- | --- | ---: | --- |
| 4 | 3.173227, 3.166136, 3.141165 | 3.166136 | 1.253–1.273 |
| 8 | 4.784595, 4.855767, 4.811659 | 4.811659 | 1.589–1.671 |
| 16 | 5.261024, 5.453562, 5.253237 | 5.261024 | 2.827–3.042 |
| 32 | 4.713165 (one run) | Not established | 6.313–6.780 |

All 84 requests in the repeated comparison and all 32 requests in the
exploratory batch returned HTTP 200 and 57 positions. The 32-request batch
took 6.789493 seconds.

Doubling concurrency from eight to sixteen increased median throughput by
only about 9%, while individual request times rose from roughly 1.6 to
3 seconds. The single 32-request run had about 10% lower throughput than
the sixteen-request median, with request times exceeding 6 seconds.

During a sixteen-request batch, the developer observed overall CPU idle
drop to 0% in Activity Monitor. This supports CPU saturation as a contributor
to the slowdown. Per-process CPU percentages are distinct from overall
machine utilization. These observations do not isolate scheduling overhead,
memory pressure, or other possible contributors.

These are short batches, not sustained-load capacity measurements. Client
and server share the Mac, resource usage was observed manually rather than
logged, memory pressure was not systematically measured, and the 32-request
result has not been repeated. Eight has not been established as the optimal
concurrency limit; sixteen achieved higher measured throughput.

### Next Experiment: Limit Active Analyses

Keep the client workload fixed at 32 concurrent requests and compare:

1. No added server-side analysis limit (repeat the baseline).
2. At most eight active analyses, with other requests waiting for a slot.
3. At most sixteen active analyses, with other requests waiting for a slot.

Repeat each condition and rotate condition order. Keep one Uvicorn process,
the PGN, engine settings, and client timeout unchanged. Record successful
throughput, batch duration, individual end-to-end request latency, and
failures. End-to-end latency must include waiting for an analysis slot;
separate server-side waiting and analysis timings can help explain results.

The limit belongs on the server so all requests share it. Limiting client
threads would change the offered workload instead. The initial experiment
uses an in-process limit, not a durable job queue; pending requests still
hold open their HTTP connections. A per-process limit would not provide a
global cap across multiple Uvicorn processes. The hypothesis is that bounded
analysis concurrency can improve behavior under load; the comparison must
establish whether eight or sixteen offers a better tradeoff.
