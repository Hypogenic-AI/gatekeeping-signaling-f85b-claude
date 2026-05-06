"""Researcher-level bean-counting identifiability simulation.

Model
-----
M researchers have latent ability α_i ~ N(0, σ_α²).
Each researcher submits S papers per year for T years.
Paper quality θ_{i,j} = α_i + ν_{i,j}, ν_{i,j} ~ N(0, σ_ν²).
(So between-researcher variance σ_α² accounts for some fraction of total
quality variance.)

Each paper is reviewed: s = θ + ε, ε ~ N(0, σ²_review). Top-K of all
N = M*S submissions per year are accepted.

We measure researcher i's "publication count" c_i = #{accepted papers of i
across T years}.

Question: how well does c_i rank α_i?

We compute Spearman ρ(α, c) and Pr(α_i in top 10% | c_i in top 10%) as a
function of N (varied by varying M, the population size).

Hypothesis: as M (and hence N) grows for fixed K, ρ → 0 because:
  (a) Each researcher's c_i becomes a sparse Bernoulli-with-tiny-p count,
  (b) The variance of c_i is dominated by review noise, not ability,
  (c) Tied counts proliferate at the bottom (most researchers have c_i = 0).

We also compare to the *infeasible* oracle ranker that ranks researchers
by E[θ_i] = α_i + (sample mean of true qualities).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, kendalltau

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


@dataclass
class BeanCountResult:
    M_researchers: int
    S_per_year: int
    T_years: int
    N_per_year: int
    K_per_year: int
    sigma_alpha: float
    sigma_nu: float
    sigma_review: float
    accept_rate: float
    spearman_alpha_count: float
    spearman_alpha_count_p: float
    spearman_alpha_truequality: float
    top10_recall: float       # Pr(α top-10% | count top-10%)
    top10_precision: float    # Pr(count top-10% | α top-10%) — these are equal here
    pct_zero_publications: float
    n_unique_counts: int


def simulate(
    M: int,
    S: int,
    T: int,
    K_per_year: int,
    sigma_alpha: float = 1.0,
    sigma_nu: float = 1.0,
    sigma_review: float = 1.5,
    seed: int = 0,
) -> BeanCountResult:
    rng = np.random.default_rng(seed)
    alpha = rng.normal(0, sigma_alpha, size=M)

    counts = np.zeros(M, dtype=int)
    sum_true_quality = np.zeros(M)
    n_per_year = M * S

    for t in range(T):
        # Generate papers
        author_id = np.repeat(np.arange(M), S)
        nu = rng.normal(0, sigma_nu, size=n_per_year)
        theta = alpha[author_id] + nu
        eps = rng.normal(0, sigma_review, size=n_per_year)
        s = theta + eps

        sum_true_quality += np.bincount(author_id, weights=theta, minlength=M)

        # Top K accepted
        K = min(K_per_year, n_per_year)
        if K <= 0:
            continue
        idx_sorted = np.argsort(-s)
        accepted = idx_sorted[:K]
        author_acc = author_id[accepted]
        counts += np.bincount(author_acc, minlength=M)

    avg_true_q = sum_true_quality / (S * T)
    accept_rate = float(counts.sum() / (n_per_year * T))

    rho_count, rho_p = spearmanr(alpha, counts)
    rho_true, _ = spearmanr(alpha, avg_true_q)

    # top-10% recall: of researchers in top decile by counts, what fraction
    # are in top decile by alpha?
    n_top = max(1, M // 10)
    top_count_idx = set(np.argsort(-counts)[:n_top])
    top_alpha_idx = set(np.argsort(-alpha)[:n_top])
    overlap = len(top_count_idx & top_alpha_idx)
    top10_recall = overlap / n_top
    # By symmetry of percentile thresholds, precision and recall are equal
    # under matched-percentile selection. Compute both for clarity.
    top10_precision = overlap / n_top

    pct_zero = float((counts == 0).mean())
    n_unique = int(len(np.unique(counts)))

    return BeanCountResult(
        M_researchers=M,
        S_per_year=S,
        T_years=T,
        N_per_year=n_per_year,
        K_per_year=K_per_year,
        sigma_alpha=sigma_alpha,
        sigma_nu=sigma_nu,
        sigma_review=sigma_review,
        accept_rate=accept_rate,
        spearman_alpha_count=float(rho_count),
        spearman_alpha_count_p=float(rho_p),
        spearman_alpha_truequality=float(rho_true),
        top10_recall=float(top10_recall),
        top10_precision=float(top10_precision),
        pct_zero_publications=pct_zero,
        n_unique_counts=n_unique,
    )


def main():
    rng = np.random.default_rng(42)

    # Vary population size M with fixed K (capacity).
    # S=2 papers/year, T=5 years (typical pre-tenure window).
    Ms = [200, 500, 1000, 2000, 5000, 10000, 20000]
    K_year = 200
    S = 2
    T = 5

    rows = []
    n_trials = 5
    for M in Ms:
        for trial in range(n_trials):
            res = simulate(
                M=M, S=S, T=T, K_per_year=K_year,
                sigma_alpha=1.0, sigma_nu=1.0, sigma_review=1.5,
                seed=int(rng.integers(0, 1 << 30)),
            )
            d = asdict(res)
            d["trial"] = trial
            d["regime"] = "fixed_K"
            rows.append(d)
        # Aggregate print
        sub = [r for r in rows if r["regime"] == "fixed_K" and r["M_researchers"] == M]
        rho_mean = np.mean([r["spearman_alpha_count"] for r in sub])
        rho_se = np.std([r["spearman_alpha_count"] for r in sub], ddof=1) / np.sqrt(n_trials)
        recall_mean = np.mean([r["top10_recall"] for r in sub])
        zero_mean = np.mean([r["pct_zero_publications"] for r in sub])
        print(
            f"[fixed_K] M={M:6d} N={M*S:6d} K={K_year} "
            f"ρ(α,count)={rho_mean:.3f}±{rho_se:.3f}  "
            f"top10_recall={recall_mean:.3f}  zero%={zero_mean*100:5.1f}"
        )

    # Also: linear-K policy (constant accept rate). Capacity grows with N.
    accept_rate = 0.30
    for M in Ms:
        K_year2 = max(2, int(accept_rate * M * S))
        for trial in range(n_trials):
            res = simulate(
                M=M, S=S, T=T, K_per_year=K_year2,
                sigma_alpha=1.0, sigma_nu=1.0, sigma_review=1.5,
                seed=int(rng.integers(0, 1 << 30)),
            )
            d = asdict(res)
            d["trial"] = trial
            d["regime"] = "linear_K"
            rows.append(d)
        sub = [r for r in rows if r["regime"] == "linear_K" and r["M_researchers"] == M]
        rho_mean = np.mean([r["spearman_alpha_count"] for r in sub])
        rho_se = np.std([r["spearman_alpha_count"] for r in sub], ddof=1) / np.sqrt(n_trials)
        recall_mean = np.mean([r["top10_recall"] for r in sub])
        zero_mean = np.mean([r["pct_zero_publications"] for r in sub])
        print(
            f"[linear_K] M={M:6d} N={M*S:6d} K={K_year2:6d} "
            f"ρ(α,count)={rho_mean:.3f}±{rho_se:.3f}  "
            f"top10_recall={recall_mean:.3f}  zero%={zero_mean*100:5.1f}"
        )

    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "bean_counting_sweep.csv", index=False)
    print(f"\nSaved {len(df)} rows to results/bean_counting_sweep.csv")


if __name__ == "__main__":
    main()
