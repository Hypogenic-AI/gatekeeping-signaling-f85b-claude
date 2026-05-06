"""Generate figures for the report."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGS = ROOT / "figures"
FIGS.mkdir(exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 130,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 10,
})


def fig1_empirical_growth():
    """Submission counts and acceptance rates over time across venues."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    venues_to_plot = [("iclr", "ICLR"), ("nips", "NeurIPS"),
                      ("icml", "ICML"), ("cvpr", "CVPR")]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for (venue, label), color in zip(venues_to_plot, colors):
        path = RESULTS / f"empirical_{venue}.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        # Drop years with fewer than 50 submissions (likely incomplete data)
        df = df[df["n_total"] >= 50]
        axes[0].plot(df["year"], df["n_total"], "o-", label=label, color=color, lw=1.5)
        axes[1].plot(df["year"], df["accept_rate"] * 100, "o-",
                     label=label, color=color, lw=1.5)

    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Submissions N")
    axes[0].set_yscale("log")
    axes[0].set_title("(a) Submission volume N(t)")
    axes[0].legend(frameon=False)
    axes[0].grid(alpha=0.3)

    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Acceptance rate (%)")
    axes[1].set_title("(b) Acceptance rate")
    axes[1].set_ylim(0, 100)
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(FIGS / "fig1_empirical_growth.png")
    plt.close(fig)


def fig2_empirical_dispersion():
    """Reviewer rating dispersion and posterior contrast Δ over time (ICLR)."""
    df = pd.read_csv(RESULTS / "empirical_iclr.csv")
    df = df.dropna(subset=["mean_rating_std", "delta_accept_reject"])
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    ax1 = axes[0]
    ax2 = ax1.twinx()
    ax1.plot(df["year"], df["mean_rating_std"], "o-", color="#d62728",
             lw=2, label="Reviewer rating SD")
    ax2.plot(df["year"], df["n_total"], "s--", color="#1f77b4",
             lw=1.5, alpha=0.7, label="Submissions N")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Mean per-paper reviewer SD", color="#d62728")
    ax2.set_ylabel("Submissions N (log)", color="#1f77b4")
    ax2.set_yscale("log")
    ax1.set_title("(a) ICLR reviewer disagreement vs. volume")
    ax1.tick_params(axis="y", labelcolor="#d62728")
    ax2.tick_params(axis="y", labelcolor="#1f77b4")

    axes[1].plot(df["year"], df["delta_accept_reject"], "o-",
                 color="#2ca02c", lw=2)
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Δ̂ = mean(rating | accept) − mean(rating | reject)")
    axes[1].set_title("(b) ICLR posterior contrast Δ̂(t)")
    axes[1].grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(FIGS / "fig2_empirical_dispersion.png")
    plt.close(fig)


def fig3_analytical_signaling():
    """I(θ; A), tail capture, posterior contrast Δ vs N for fixed K."""
    df = pd.read_csv(RESULTS / "analytical_sweep_fixed_capacity.csv")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    sigmas = sorted(df["sigma"].unique())
    cmap = plt.get_cmap("viridis")

    sub = df[df["quality_dist"] == "gaussian"]
    for i, sigma in enumerate(sigmas):
        ss = sub[sub["sigma"] == sigma].sort_values("N")
        c = cmap(i / max(len(sigmas) - 1, 1))
        axes[0].plot(ss["N"], ss["mutual_information_bits"],
                     "o-", color=c, label=f"σ={sigma}")
        axes[1].plot(ss["N"], ss["tail_capture_top1pct"],
                     "o-", color=c, label=f"σ={sigma}")
        axes[2].plot(ss["N"], ss["posterior_contrast"],
                     "o-", color=c, label=f"σ={sigma}")
    for a in axes:
        a.set_xscale("log")
        a.set_xlabel("Submissions N (log)")
        a.grid(alpha=0.3)
    axes[0].set_ylabel("I(θ; A) [bits]")
    axes[0].set_title("(a) Mutual information")
    axes[1].set_ylabel("Pr(top-1% paper accepted)")
    axes[1].set_title("(b) Tail capture (recall)")
    axes[1].set_ylim(0, 1.05)
    axes[2].set_ylabel("Δ = E[θ|A=1] − E[θ|A=0]")
    axes[2].set_title("(c) Posterior contrast")
    axes[0].legend(frameon=False, fontsize=8)

    fig.suptitle("Closed-form Bayesian signaling, fixed K=200, Gaussian θ",
                 y=1.02, fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGS / "fig3_analytical_signaling.png", bbox_inches="tight")
    plt.close(fig)


def fig4_distribution_robustness():
    """Same metrics across Gaussian, log-normal, Pareto."""
    df = pd.read_csv(RESULTS / "analytical_sweep_fixed_capacity.csv")
    df = df[df["sigma"] == 1.0]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    dist_color = {"gaussian": "#1f77b4", "lognormal": "#ff7f0e", "pareto": "#2ca02c"}
    for dist, color in dist_color.items():
        ss = df[df["quality_dist"] == dist].sort_values("N")
        axes[0].plot(ss["N"], ss["mutual_information_bits"],
                     "o-", color=color, label=dist)
        axes[1].plot(ss["N"], ss["tail_capture_top1pct"],
                     "o-", color=color, label=dist)
    for a in axes:
        a.set_xscale("log")
        a.set_xlabel("Submissions N (log)")
        a.grid(alpha=0.3)
    axes[0].set_ylabel("I(θ; A) [bits]")
    axes[1].set_ylabel("Pr(top-1% paper accepted)")
    axes[0].legend(frameon=False)
    axes[1].set_ylim(0, 1.05)
    fig.suptitle("Robustness to quality distribution (σ=1.0, K=200)",
                 y=1.02, fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGS / "fig4_distribution_robustness.png", bbox_inches="tight")
    plt.close(fig)


def fig5_capacity_policies():
    """E5: Compare capacity policies — does expanding capacity rescue signal?"""
    df = pd.read_csv(RESULTS / "analytical_capacity_policies.csv")
    df = df[df["sigma"] == 1.5]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    pol_color = {"constant_K": "#d62728", "sublinear_sqrt": "#ff7f0e",
                 "linear_a30pct": "#2ca02c"}
    pol_label = {"constant_K": "Constant K=200", "sublinear_sqrt": "K = 20·√N",
                 "linear_a30pct": "K = 0.30·N (constant accept rate)"}
    for pol, c in pol_color.items():
        ss = df[df["policy"] == pol].sort_values("N")
        axes[0].plot(ss["N"], ss["mutual_information_bits"], "o-",
                     color=c, label=pol_label[pol])
        axes[1].plot(ss["N"], ss["tail_capture_top1pct"], "o-",
                     color=c, label=pol_label[pol])
        axes[2].plot(ss["N"], ss["accept_rate"] * 100, "o-",
                     color=c, label=pol_label[pol])
    for a in axes:
        a.set_xscale("log")
        a.set_xlabel("Submissions N (log)")
        a.grid(alpha=0.3)
    axes[0].set_ylabel("I(θ; A) [bits]")
    axes[0].set_title("(a) Mutual information")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].set_ylabel("Pr(top-1% accepted)")
    axes[1].set_title("(b) Tail capture")
    axes[1].set_ylim(0, 1.05)
    axes[2].set_ylabel("Acceptance rate (%)")
    axes[2].set_title("(c) Acceptance rate")
    axes[2].set_yscale("log")
    fig.suptitle("E5: Capacity policy comparison (σ=1.5, Gaussian θ)",
                 y=1.02, fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGS / "fig5_capacity_policies.png", bbox_inches="tight")
    plt.close(fig)


def fig6_bean_counting():
    """E3: ρ(α, count) and top-10% recall vs population size, two regimes."""
    df = pd.read_csv(RESULTS / "bean_counting_sweep.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for regime, color in [("fixed_K", "#d62728"), ("linear_K", "#2ca02c")]:
        sub = df[df["regime"] == regime]
        agg = sub.groupby("M_researchers").agg(
            mean_rho=("spearman_alpha_count", "mean"),
            se_rho=("spearman_alpha_count", lambda x: x.std(ddof=1) / np.sqrt(len(x))),
            mean_recall=("top10_recall", "mean"),
            se_recall=("top10_recall", lambda x: x.std(ddof=1) / np.sqrt(len(x))),
            mean_zero=("pct_zero_publications", "mean"),
        ).reset_index()
        label = "Fixed K=200" if regime == "fixed_K" else "K = 0.30·N"
        axes[0].errorbar(agg["M_researchers"], agg["mean_rho"],
                         yerr=agg["se_rho"], fmt="o-", color=color,
                         label=label, capsize=3)
        axes[1].errorbar(agg["M_researchers"], agg["mean_recall"],
                         yerr=agg["se_recall"], fmt="o-", color=color,
                         label=label, capsize=3)
    for a in axes:
        a.set_xscale("log")
        a.set_xlabel("Researcher population M (log)")
        a.grid(alpha=0.3)
        a.legend(frameon=False)
    axes[0].set_ylabel("Spearman ρ(α, publication count)")
    axes[0].set_title("(a) Researcher-level identifiability")
    axes[0].axhline(0, color="k", lw=0.7, ls="--", alpha=0.4)
    axes[1].set_ylabel("Top-10% recall (researcher level)")
    axes[1].set_title("(b) Top-decile recall by ability")
    axes[1].set_ylim(0, 1)
    fig.suptitle("E3: Bean-counting fails to identify good researchers under fixed capacity",
                 y=1.02, fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGS / "fig6_bean_counting.png", bbox_inches="tight")
    plt.close(fig)


def fig7_consumption():
    """E2: Reader consumption — quality consumed and reader collapse."""
    df = pd.read_csv(RESULTS / "consumption_sweep.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    for (exp, ax_label) in [("fixed_K", "Fixed K=200"), ("linear_K", "K=0.30·N")]:
        sub = df[df["experiment"] == exp]
        for strategy, color, marker in [
            ("accepted_no_feedback", "#1f77b4", "o"),
            ("all_no_feedback", "#7f7f7f", "s"),
            ("accepted_with_feedback", "#d62728", "^"),
        ]:
            ss = sub[sub["strategy"] == strategy].sort_values("N")
            label = f"{ax_label}: {strategy.replace('_', ' ')}"
            ax = axes[0] if exp == "fixed_K" else axes[1]
            ax.errorbar(ss["N"], ss["mean_quality_consumed"],
                        yerr=ss["se_quality_consumed"],
                        fmt=marker + "-", color=color,
                        label=strategy.replace("_", " "), capsize=3)
    for ax, title in zip(axes, ["(a) Fixed K=200 capacity",
                                "(b) Linear K=0.30·N capacity"]):
        ax.set_xscale("log")
        ax.set_xlabel("Submissions N (log)")
        ax.set_ylabel("Total true quality consumed (12 yr × B=20)")
        ax.set_title(title)
        ax.grid(alpha=0.3)
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle("E2: Reader consumption (B=20 papers/yr, σ=1.5, M=200 readers)",
                 y=1.02, fontsize=11)
    fig.tight_layout()
    fig.savefig(FIGS / "fig7_consumption.png", bbox_inches="tight")
    plt.close(fig)


def fig8_calibration_iclr():
    """Calibrate model σ to match empirical ICLR posterior contrast Δ̂."""
    emp = pd.read_csv(RESULTS / "empirical_iclr.csv")
    emp = emp.dropna(subset=["delta_accept_reject", "mean_rating_std"])
    # Compare empirical Δ̂ to model Δ at matching N and accept_rate.
    # Model uses Gaussian theta with unit variance; empirical uses 1-10 rating
    # scale. To compare, normalize empirical Δ̂ by empirical pooled rating SD.
    # Pooled SD: weighted average of mean_rating_std across years.
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # Left: empirical normalized Δ̂ vs model prediction
    from scipy.stats import norm as _norm
    # Quick analytical approximation in Gaussian case:
    # delta_normalized = phi(z_a)/(a(1-a)) approximately, scaled by 1/sqrt(1+sigma^2)
    # We'll compute the model Δ in standardized rating units (theta+ratingSD).

    # We re-use compute_signaling? Just call analytical_sweep here:
    import sys; sys.path.insert(0, str(ROOT / "src"))
    from analytical_signaling import compute_signaling

    rows = []
    for _, row in emp.iterrows():
        N = int(row["n_total"])
        a = float(row["accept_rate"])
        K = max(2, int(a * N))
        emp_delta_norm = row["delta_accept_reject"] / max(row["mean_rating_std"], 1e-6)
        # Try a few sigmas; record predicted normalized delta
        for sigma in [0.5, 1.0, 1.5, 2.0]:
            res = compute_signaling(N=N, K=K, sigma=sigma, dist="gaussian")
            rows.append({
                "year": int(row["year"]),
                "N": N,
                "accept_rate": a,
                "sigma": sigma,
                "predicted_delta": res.posterior_contrast,
                "predicted_mi": res.mutual_information_bits,
                "empirical_delta_normalized": emp_delta_norm,
                "empirical_rating_sd": row["mean_rating_std"],
            })
    cal = pd.DataFrame(rows)
    cal.to_csv(RESULTS / "calibration_iclr.csv", index=False)

    sigmas_to_show = [0.5, 1.0, 1.5, 2.0]
    cmap = plt.get_cmap("viridis")
    for i, sigma in enumerate(sigmas_to_show):
        sub = cal[cal["sigma"] == sigma].sort_values("year")
        axes[0].plot(sub["year"], sub["predicted_delta"], "o-",
                     color=cmap(i / len(sigmas_to_show)),
                     label=f"Model σ={sigma}")
    emp_only = cal[cal["sigma"] == 1.0].sort_values("year")
    axes[0].plot(emp_only["year"], emp_only["empirical_delta_normalized"],
                 "k^--", lw=2, label="Empirical Δ̂/σ̂_rating", markersize=8)
    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Δ (standardized)")
    axes[0].set_title("(a) ICLR — empirical Δ̂ vs model")
    axes[0].legend(frameon=False, fontsize=8)
    axes[0].grid(alpha=0.3)

    # Right: best-fit sigma per year (minimizing |predicted - empirical|)
    best_sigmas = []
    for year in sorted(cal["year"].unique()):
        sub = cal[cal["year"] == year]
        emp_d = sub["empirical_delta_normalized"].iloc[0]
        # Find sigma minimizing |delta - emp_d|
        sub2 = sub.copy()
        sub2["err"] = (sub2["predicted_delta"] - emp_d).abs()
        best = sub2.loc[sub2["err"].idxmin()]
        best_sigmas.append({"year": year, "best_sigma": best["sigma"],
                            "N": best["N"], "emp_d": emp_d,
                            "rating_sd": best["empirical_rating_sd"]})
    bs = pd.DataFrame(best_sigmas)
    bs.to_csv(RESULTS / "calibration_best_sigma.csv", index=False)

    axes[1].plot(bs["year"], bs["best_sigma"], "o-", color="#d62728",
                 lw=2, label="Best-fit σ (model)")
    axes[1].plot(bs["year"], bs["rating_sd"], "s--", color="#1f77b4",
                 lw=2, label="Empirical reviewer SD")
    axes[1].set_xlabel("Year")
    axes[1].set_ylabel("Reviewer noise σ")
    axes[1].set_title("(b) Inferred reviewer noise vs. observed SD")
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(FIGS / "fig8_calibration_iclr.png", bbox_inches="tight")
    plt.close(fig)


def main():
    fig1_empirical_growth(); print("fig1 done")
    fig2_empirical_dispersion(); print("fig2 done")
    fig3_analytical_signaling(); print("fig3 done")
    fig4_distribution_robustness(); print("fig4 done")
    fig5_capacity_policies(); print("fig5 done")
    fig6_bean_counting(); print("fig6 done")
    fig7_consumption(); print("fig7 done")
    fig8_calibration_iclr(); print("fig8 done")
    print("All figures saved to figures/")


if __name__ == "__main__":
    main()
