"""Statistical tests on empirical and simulated data, summarizing the
support for each sub-hypothesis.

H1 (paper-level): I(θ;A) and tail capture decrease with N (analytical).
H2 (consumption): consumption strategies diverge as N grows (simulation).
H3 (researcher-level): ρ(α, count) decreases with N under fixed K.
H4 (empirical): ICLR rating dispersion increases with N; Δ̂ decreases.

Outputs results/statistical_tests.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr, linregress, mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def mann_kendall(x, y):
    """Two-sided Kendall tau test on monotone trend of y in x."""
    tau, p = kendalltau(x, y)
    return float(tau), float(p)


def main():
    out = {}

    # H1: analytical trends (these are deterministic; we report directional)
    df = pd.read_csv(RESULTS / "analytical_sweep_fixed_capacity.csv")
    h1 = {}
    for dist in df["quality_dist"].unique():
        for sigma in df["sigma"].unique():
            sub = df[(df["quality_dist"] == dist) & (df["sigma"] == sigma)].sort_values("N")
            if len(sub) < 3:
                continue
            tau_mi, p_mi = mann_kendall(sub["N"], sub["mutual_information_bits"])
            tau_tail, p_tail = mann_kendall(sub["N"], sub["tail_capture_top1pct"])
            slope_mi = linregress(np.log(sub["N"]), sub["mutual_information_bits"]).slope
            h1.setdefault(dist, {})[f"sigma={sigma}"] = {
                "MI_kendall_tau": tau_mi, "MI_p": p_mi,
                "tail_kendall_tau": tau_tail, "tail_p": p_tail,
                "MI_slope_in_logN": float(slope_mi),
            }
    out["H1_analytical"] = h1

    # H3: bean-counting trends across population sizes
    df = pd.read_csv(RESULTS / "bean_counting_sweep.csv")
    h3 = {}
    for regime in df["regime"].unique():
        sub = df[df["regime"] == regime]
        agg = sub.groupby("M_researchers").agg(
            mean_rho=("spearman_alpha_count", "mean"),
            mean_recall=("top10_recall", "mean"),
        ).reset_index()
        tau_rho, p_rho = mann_kendall(agg["M_researchers"], agg["mean_rho"])
        tau_rec, p_rec = mann_kendall(agg["M_researchers"], agg["mean_recall"])
        # Compare smallest vs largest M with Mann-Whitney
        m_min = agg["M_researchers"].min()
        m_max = agg["M_researchers"].max()
        rho_min = sub.loc[sub["M_researchers"] == m_min, "spearman_alpha_count"].values
        rho_max = sub.loc[sub["M_researchers"] == m_max, "spearman_alpha_count"].values
        if len(rho_min) > 1 and len(rho_max) > 1:
            mw_u, mw_p = mannwhitneyu(rho_min, rho_max, alternative="greater")
        else:
            mw_u, mw_p = None, None
        h3[regime] = {
            "kendall_tau_rho_vs_M": tau_rho, "p_rho": p_rho,
            "kendall_tau_recall_vs_M": tau_rec, "p_recall": p_rec,
            "mannwhitney_rho_smallM_vs_largeM": {
                "U": float(mw_u) if mw_u is not None else None,
                "p_one_sided": float(mw_p) if mw_p is not None else None,
                "rho_smallM_mean": float(np.mean(rho_min)),
                "rho_largeM_mean": float(np.mean(rho_max)),
            },
        }
    out["H3_bean_counting"] = h3

    # H4: empirical ICLR
    df = pd.read_csv(RESULTS / "empirical_iclr.csv")
    df_full = df.dropna(subset=["mean_rating_std", "delta_accept_reject"])
    n_ratings_years = len(df_full)
    if n_ratings_years >= 4:
        # Mann-Kendall test on dispersion vs year (and dispersion vs N)
        tau_disp_year, p_disp_year = mann_kendall(df_full["year"], df_full["mean_rating_std"])
        tau_disp_n, p_disp_n = mann_kendall(df_full["n_total"], df_full["mean_rating_std"])
        tau_delta_year, p_delta_year = mann_kendall(df_full["year"], df_full["delta_accept_reject"])
        tau_delta_n, p_delta_n = mann_kendall(df_full["n_total"], df_full["delta_accept_reject"])
        # Linear regression of normalized delta on log N
        log_n = np.log(df_full["n_total"])
        emp_delta_norm = df_full["delta_accept_reject"] / df_full["mean_rating_std"]
        lr = linregress(log_n, emp_delta_norm)
        out["H4_empirical_iclr"] = {
            "n_years_with_ratings": n_ratings_years,
            "rating_SD_kendall_tau_vs_year": tau_disp_year,
            "rating_SD_p_vs_year": p_disp_year,
            "rating_SD_kendall_tau_vs_N": tau_disp_n,
            "rating_SD_p_vs_N": p_disp_n,
            "delta_kendall_tau_vs_year": tau_delta_year,
            "delta_p_vs_year": p_delta_year,
            "delta_kendall_tau_vs_N": tau_delta_n,
            "delta_p_vs_N": p_delta_n,
            "delta_normalized_slope_in_logN": float(lr.slope),
            "delta_normalized_slope_p": float(lr.pvalue),
            "delta_normalized_R2": float(lr.rvalue ** 2),
            "first_year_summary": {
                "year": int(df_full["year"].iloc[0]),
                "N": int(df_full["n_total"].iloc[0]),
                "rating_SD": float(df_full["mean_rating_std"].iloc[0]),
                "delta_normalized": float(emp_delta_norm.iloc[0]),
            },
            "last_year_summary": {
                "year": int(df_full["year"].iloc[-1]),
                "N": int(df_full["n_total"].iloc[-1]),
                "rating_SD": float(df_full["mean_rating_std"].iloc[-1]),
                "delta_normalized": float(emp_delta_norm.iloc[-1]),
            },
        }

    # H2: consumption sweep — test whether (under fixed K) the gap between
    # accepted-strategy and all-strategy quality stays constant in N (i.e.,
    # absolute label remains useful) but (under linear K) the gap closes
    # because variance of the accepted pool grows.
    df = pd.read_csv(RESULTS / "consumption_sweep.csv")
    # Within each experiment, regress (accepted_quality - all_quality) on N
    h2 = {}
    for exp in df["experiment"].unique():
        sub = df[df["experiment"] == exp].sort_values("N")
        acc = sub[sub["strategy"] == "accepted_no_feedback"][["N", "mean_quality_consumed"]].rename(
            columns={"mean_quality_consumed": "Q_acc"})
        allp = sub[sub["strategy"] == "all_no_feedback"][["N", "mean_quality_consumed"]].rename(
            columns={"mean_quality_consumed": "Q_all"})
        merged = acc.merge(allp, on="N")
        merged["gap"] = merged["Q_acc"] - merged["Q_all"]
        if len(merged) > 2:
            lr = linregress(np.log(merged["N"]), merged["gap"])
            h2[exp] = {
                "gap_slope_in_logN": float(lr.slope),
                "gap_slope_p": float(lr.pvalue),
                "gap_first_N": float(merged["gap"].iloc[0]),
                "gap_last_N": float(merged["gap"].iloc[-1]),
            }
    out["H2_consumption"] = h2

    with open(RESULTS / "statistical_tests.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
