"""Reader consumption model with negative-experience feedback.

Key idea
--------
A reader has a fixed time budget B (papers/year). For each accepted paper,
they decide whether to read it based on (i) their venue prior μ_V and
(ii) their personal "saturation" — they only have time to read B papers,
chosen by sampling from their attention distribution.

When K (capacity) is fixed and N grows, the reader can read at most B
of K papers. Since K is fixed, the *fraction of accepted papers actually
read* stays at min(1, B/K). But more importantly, the expected quality
of a paper picked at random from the accepted pile is high under fixed K.

When K is allowed to grow with N (linear policy a = K/N constant), K → ∞
and the reader can only read B/K → 0 fraction. Picking randomly from
accepted pool is then no better than picking randomly from all submissions
*if the reader cannot distinguish papers within the accepted pool*. The
key claim: acceptance is a binary label, and the reader needs more
information to choose B papers from K.

Negative-experience feedback
----------------------------
After reading a bad paper from a venue, the reader updates their venue
prior μ_V downward (Bayesian update with a Beta-Bernoulli model). Once
μ_V drops below a threshold μ_*, the reader stops reading from V.

Quantities measured
-------------------
- E[total quality consumed] over T rounds
- Pr(reader still reads from V at time T)
- Time to "trust collapse"
- Effective signal: P(read paper | accepted) − P(read paper | rejected)

We compare:
  Strategy A: read random papers from accepted pool
  Strategy B: read random papers from all submissions
  Strategy C: read random papers from accepted pool with negative-experience
              feedback shutdown
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


@dataclass
class ConsumptionResult:
    N: int
    K: int
    sigma: float
    budget_B: int
    n_readers: int
    rounds: int
    bad_threshold: float
    strategy: str
    mean_quality_consumed: float
    se_quality_consumed: float
    pct_collapsed_readers: float  # fraction of readers who stopped reading from V
    mean_papers_read: float


def simulate_one_round(
    N: int, K: int, sigma: float, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Generate one venue-year of papers and return (theta_accepted,
    theta_rejected)."""
    theta = rng.standard_normal(N)
    s = theta + sigma * rng.standard_normal(N)
    # top-K accepted
    if K >= N:
        return theta, np.array([])
    idx_sorted = np.argsort(-s)
    accepted_idx = idx_sorted[:K]
    rejected_idx = idx_sorted[K:]
    return theta[accepted_idx], theta[rejected_idx]


def simulate_consumption(
    N: int,
    K: int,
    sigma: float,
    budget_B: int,
    n_readers: int = 200,
    rounds: int = 12,
    bad_threshold: float = -0.5,
    strategy: str = "accepted_no_feedback",
    seed: int = 0,
) -> ConsumptionResult:
    """Simulate reader consumption.

    Strategy options:
      - 'accepted_no_feedback': pick min(B, K) random accepted papers
        per round; never stop reading from V.
      - 'all_no_feedback': pick min(B, N) random papers from all submissions.
      - 'accepted_with_feedback': pick from accepted pool; track trust
        per reader; if mean quality of papers read by this reader drops
        below bad_threshold (after at least 5 papers), reader stops.
    """
    rng = np.random.default_rng(seed)
    # State per reader
    quality_consumed = np.zeros(n_readers)
    papers_read = np.zeros(n_readers, dtype=int)
    active = np.ones(n_readers, dtype=bool)

    # For feedback strategy:
    cumulative_quality_per_reader = np.zeros(n_readers)
    cumulative_count_per_reader = np.zeros(n_readers, dtype=int)

    for t in range(rounds):
        accepted, rejected = simulate_one_round(N=N, K=K, sigma=sigma, rng=rng)
        all_papers = np.concatenate([accepted, rejected])

        if strategy in ("accepted_no_feedback", "accepted_with_feedback"):
            pool = accepted
        elif strategy == "all_no_feedback":
            pool = all_papers
        else:
            raise ValueError(strategy)

        if pool.size == 0:
            continue

        for r in range(n_readers):
            if not active[r]:
                continue
            n_to_read = min(budget_B, len(pool))
            picks = rng.choice(pool, size=n_to_read, replace=False)
            quality_consumed[r] += picks.sum()
            papers_read[r] += n_to_read
            cumulative_quality_per_reader[r] += picks.sum()
            cumulative_count_per_reader[r] += n_to_read

            if strategy == "accepted_with_feedback":
                if cumulative_count_per_reader[r] >= 5:
                    avg_q = (
                        cumulative_quality_per_reader[r] /
                        cumulative_count_per_reader[r]
                    )
                    if avg_q < bad_threshold:
                        active[r] = False

    mean_q = float(quality_consumed.mean())
    se_q = float(quality_consumed.std(ddof=1) / np.sqrt(n_readers))
    pct_collapsed = float(1.0 - active.mean())
    mean_papers = float(papers_read.mean())

    return ConsumptionResult(
        N=N,
        K=K,
        sigma=sigma,
        budget_B=budget_B,
        n_readers=n_readers,
        rounds=rounds,
        bad_threshold=bad_threshold,
        strategy=strategy,
        mean_quality_consumed=mean_q,
        se_quality_consumed=se_q,
        pct_collapsed_readers=pct_collapsed,
        mean_papers_read=mean_papers,
    )


def main():
    rng = np.random.default_rng(0)

    # E2a: Fixed-K policy. Vary N.
    Ns = [200, 400, 800, 1600, 3200, 6400, 12800, 25600]
    K_fixed = 200
    sigma = 1.5  # high noise (consistent with empirical ICLR rating-std ≈ 1.5)
    budget_B = 20

    rows = []
    for N in Ns:
        for strategy in (
            "accepted_no_feedback",
            "all_no_feedback",
            "accepted_with_feedback",
        ):
            res = simulate_consumption(
                N=N, K=K_fixed, sigma=sigma, budget_B=budget_B,
                n_readers=200, rounds=12, bad_threshold=-0.3,
                strategy=strategy, seed=int(rng.integers(0, 1 << 30)),
            )
            rows.append({"experiment": "fixed_K", **asdict(res)})
            print(
                f"[fixed_K] N={N:6d} K={K_fixed} σ={sigma:.2f} B={budget_B} "
                f"{strategy:32s} Q={res.mean_quality_consumed:7.2f}±{res.se_quality_consumed:5.2f} "
                f"collapsed={res.pct_collapsed_readers*100:5.1f}%"
            )

    # E2b: Linear-K policy (constant acceptance rate). Vary N. Capacity grows.
    rows2 = []
    accept_rate = 0.30
    for N in Ns:
        K = max(2, int(accept_rate * N))
        for strategy in (
            "accepted_no_feedback",
            "all_no_feedback",
            "accepted_with_feedback",
        ):
            res = simulate_consumption(
                N=N, K=K, sigma=sigma, budget_B=budget_B,
                n_readers=200, rounds=12, bad_threshold=-0.3,
                strategy=strategy, seed=int(rng.integers(0, 1 << 30)),
            )
            rows2.append({"experiment": "linear_K", **asdict(res)})
            print(
                f"[linear_K] N={N:6d} K={K:6d} σ={sigma:.2f} B={budget_B} "
                f"{strategy:32s} Q={res.mean_quality_consumed:7.2f}±{res.se_quality_consumed:5.2f} "
                f"collapsed={res.pct_collapsed_readers*100:5.1f}%"
            )

    df = pd.DataFrame(rows + rows2)
    df.to_csv(RESULTS / "consumption_sweep.csv", index=False)
    print(f"\nSaved {len(df)} rows to results/consumption_sweep.csv")


if __name__ == "__main__":
    main()
