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

**Current phase:** Phase 0 — Local Monolith

**Current milestone:** Given a Chess.com username, retrieve the PGN for one
game and understand the Chess.com API flow before implementing engine
analysis.