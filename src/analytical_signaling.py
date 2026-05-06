"""Closed-form Bayesian signaling model with capacity-constrained
gatekeeper.

Model
-----
- N papers submitted; each has latent quality θ_i ~ F.
- Reviewer observes noisy score s_i = θ_i + ε_i, ε_i ~ N(0, σ²).
- Gatekeeper accepts the top-K papers by score, where K = capacity.
- Acceptance rate a = K / N. As N grows for fixed K, a → 0.
  (And as N grows with K = a*N for fixed a, K grows but the *cutoff
  in standardized units* is fixed; signal does not collapse — see E5.)

Quantities we compute
---------------------
- Calibration: Pr(A=1 | θ) = Pr(s > τ | θ) = Φ((θ − τ) / σ),
  where τ is the score threshold solving Pr(s > τ) = a.
- Posterior contrast Δ(N, K, σ²):
    Δ = E[θ | A=1] − E[θ | A=0]
  for Gaussian θ ~ N(0,1), this can be expressed in closed form in terms
  of the standard normal hazard rate.
- Mutual information I(θ; A) (binary A): computed numerically.
- Tail capture: Pr(θ in top 1% | A=1) and Pr(top 1% paper accepted).

Derivation note (Gaussian case)
-------------------------------
Let θ ~ N(0,1) and ε ~ N(0,σ²) independent. Then s = θ + ε ~ N(0, 1+σ²).
The score threshold for accepting top fraction a is τ = z_{1-a} √(1+σ²),
where z_{1-a} is the standard-normal (1-a)-quantile.
Conditional on θ, s|θ ~ N(θ, σ²), so
    p_acc(θ) := Pr(A=1|θ) = Φ((θ - τ)/σ).
The marginal acceptance rate is a (by construction).
Then
    E[θ | A=1] = E[θ p_acc(θ)] / a,
    E[θ | A=0] = E[θ (1 - p_acc(θ))] / (1-a).
Both integrals are tractable as standard-normal hazard-style integrals.

We compute everything by numerical integration to avoid hand-derivation
errors and to support arbitrary θ distributions.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
from scipy.stats import norm, lognorm, pareto

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


@dataclass
class SignalingResult:
    N: int
    K: int
    sigma: float
    accept_rate: float
    threshold: float
    mean_quality_accepted: float
    mean_quality_rejected: float
    posterior_contrast: float
    mutual_information_bits: float
    tail_capture_top1pct: float  # Pr(top-1% paper is accepted)
    precision_top1pct: float     # Pr(accepted paper is in top 1% of θ)
    quality_dist: str


def _quality_pdf_cdf_grid(dist: str, n_grid: int = 4001):
    """Return (theta_grid, pdf, cdf) for a unit-variance quality dist."""
    if dist == "gaussian":
        theta = np.linspace(-6.0, 6.0, n_grid)
        pdf = norm.pdf(theta)
        cdf = norm.cdf(theta)
        return theta, pdf, cdf
    if dist == "lognormal":
        # Standardize to mean 0 var 1 by subtracting mean and dividing by std.
        s = 0.7  # shape
        # Compute mean and var of lognormal(0,s) directly:
        m = np.exp(s * s / 2)
        v = (np.exp(s * s) - 1) * np.exp(s * s)
        sd = np.sqrt(v)
        theta = np.linspace(-3.0, 12.0, n_grid)
        # transform: y = (X - m)/sd where X ~ lognormal
        x = theta * sd + m
        # Only x > 0 is supported
        pdf = np.where(x > 0, lognorm.pdf(x, s) * sd, 0.0)
        cdf = np.where(x > 0, lognorm.cdf(x, s), 0.0)
        return theta, pdf, cdf
    if dist == "pareto":
        # Pareto with shape b=2.5 (finite mean and variance for b>2)
        b = 2.5
        x_min = 1.0
        m = b * x_min / (b - 1)
        v = (b * x_min ** 2) / ((b - 1) ** 2 * (b - 2))
        sd = np.sqrt(v)
        theta = np.linspace(-2.0, 15.0, n_grid)
        x = theta * sd + m
        pdf = np.where(x >= x_min, pareto.pdf(x, b) * sd, 0.0)
        cdf = np.where(x >= x_min, pareto.cdf(x, b), 0.0)
        return theta, pdf, cdf
    raise ValueError(f"Unknown distribution {dist!r}")


def compute_signaling(
    N: int, K: int, sigma: float, dist: str = "gaussian"
) -> SignalingResult:
    """Compute all signaling quantities for given (N, K, sigma) and quality
    distribution. Capacity-constrained: top K of N are accepted."""
    a = K / N
    a = max(min(a, 1.0 - 1e-9), 1e-9)

    theta, p_theta, _ = _quality_pdf_cdf_grid(dist)
    # Normalize numerically
    p_theta = p_theta / np.trapezoid(p_theta, theta)

    # The score s = theta + epsilon. The marginal of s under the true theta
    # distribution is the convolution. We solve for tau such that
    # Pr(s > tau) = a.
    # Pr(s > tau) = ∫ p_theta(θ) Φ((θ - tau)/sigma) dθ ... wait that's
    # Pr(s > tau | theta) integrated. Actually:
    #   Pr(s > tau) = ∫ p_theta(θ) [1 - Φ((tau - θ)/sigma)] dθ
    #              = ∫ p_theta(θ) Φ((θ - tau)/sigma) dθ
    def acc_rate(tau: float) -> float:
        return float(np.trapezoid(p_theta * norm.cdf((theta - tau) / sigma), theta))

    # Bisection over tau.
    lo, hi = float(theta[0]) - 5 * sigma, float(theta[-1]) + 5 * sigma
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if acc_rate(mid) > a:
            lo = mid
        else:
            hi = mid
    tau = 0.5 * (lo + hi)

    p_acc_theta = norm.cdf((theta - tau) / sigma)  # Pr(A=1 | theta)
    realized_a = float(np.trapezoid(p_theta * p_acc_theta, theta))

    e_theta_acc_num = float(np.trapezoid(theta * p_theta * p_acc_theta, theta))
    e_theta_rej_num = float(np.trapezoid(theta * p_theta * (1 - p_acc_theta), theta))
    mean_acc = e_theta_acc_num / max(realized_a, 1e-12)
    mean_rej = e_theta_rej_num / max(1 - realized_a, 1e-12)
    delta = mean_acc - mean_rej

    # Mutual information I(theta; A). theta is continuous, A is binary.
    # I = H(A) - H(A | theta).
    # H(A) = -a log a - (1-a) log(1-a)
    # H(A | theta) = -∫ p(θ) [p_a(θ) log p_a(θ) + (1-p_a(θ)) log(1-p_a(θ))] dθ
    eps = 1e-12
    p1 = np.clip(p_acc_theta, eps, 1 - eps)
    h_a = -realized_a * np.log2(realized_a) - (1 - realized_a) * np.log2(1 - realized_a)
    cond_entropy = -np.trapezoid(
        p_theta * (p1 * np.log2(p1) + (1 - p1) * np.log2(1 - p1)), theta
    )
    mi_bits = float(h_a - cond_entropy)

    # Tail capture: top-1% threshold of theta distribution.
    cdf_grid = np.cumsum(p_theta) * (theta[1] - theta[0])
    cdf_grid /= cdf_grid[-1]
    top1_idx = np.searchsorted(cdf_grid, 0.99)
    theta_top1 = theta[min(top1_idx, len(theta) - 1)]
    # Pr(top-1% paper accepted) = Pr(A=1 | θ > theta_top1)
    mask = theta >= theta_top1
    if mask.sum() > 1:
        num = np.trapezoid((p_theta * p_acc_theta)[mask], theta[mask])
        den = np.trapezoid(p_theta[mask], theta[mask])
        tail_cap = float(num / max(den, 1e-12))
    else:
        tail_cap = float("nan")

    # Precision top-1%: Pr(θ > theta_top1 | A=1)
    num2 = np.trapezoid((p_theta * p_acc_theta)[mask], theta[mask])
    prec_top1 = float(num2 / max(realized_a, 1e-12))

    return SignalingResult(
        N=N,
        K=K,
        sigma=sigma,
        accept_rate=realized_a,
        threshold=float(tau),
        mean_quality_accepted=mean_acc,
        mean_quality_rejected=mean_rej,
        posterior_contrast=float(delta),
        mutual_information_bits=mi_bits,
        tail_capture_top1pct=tail_cap,
        precision_top1pct=prec_top1,
        quality_dist=dist,
    )


def main():
    # Sweep over N, fixed capacity K. Capacity here measures absolute
    # accepts (e.g., top conference issues a fixed number of slots).
    Ks = [200]  # fixed-capacity policy: top venue accepts ~200 papers/year
    Ns = [200, 400, 800, 1600, 3200, 6400, 12800, 25600, 51200, 102400]
    sigmas = [0.3, 0.7, 1.0, 1.5, 2.0]
    dists = ["gaussian", "lognormal", "pareto"]

    rows = []
    for K in Ks:
        for sigma in sigmas:
            for dist in dists:
                for N in Ns:
                    if N < K:
                        continue
                    res = compute_signaling(N=N, K=K, sigma=sigma, dist=dist)
                    rows.append(asdict(res))
                    print(
                        f"K={K} σ={sigma:.2f} {dist:10s} "
                        f"N={N:6d} a={res.accept_rate:.4f} "
                        f"Δ={res.posterior_contrast:.3f} "
                        f"I={res.mutual_information_bits:.3f} "
                        f"tail={res.tail_capture_top1pct:.3f}"
                    )

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "analytical_sweep_fixed_capacity.csv", index=False)
    print(f"\nSaved {len(df)} rows to results/analytical_sweep_fixed_capacity.csv")

    # Also: capacity-policy sweep (E5). For each policy, vary N and pick K.
    policies = {
        "constant_K": lambda N: 200,
        "sublinear_sqrt": lambda N: int(20 * np.sqrt(N)),
        "linear_a30pct": lambda N: max(1, int(0.30 * N)),
    }
    rows2 = []
    for policy, k_of_n in policies.items():
        for sigma in [0.7, 1.5]:
            for N in Ns:
                K = k_of_n(N)
                K = min(K, N - 1)
                if K < 2:
                    continue
                res = compute_signaling(N=N, K=K, sigma=sigma, dist="gaussian")
                d = asdict(res)
                d["policy"] = policy
                rows2.append(d)
    df2 = pd.DataFrame(rows2)
    df2.to_csv(RESULTS / "analytical_capacity_policies.csv", index=False)
    print(f"Saved {len(df2)} rows to results/analytical_capacity_policies.csv")


if __name__ == "__main__":
    main()
