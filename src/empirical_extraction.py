"""Extract empirical N(t), C(t), acceptance rates, and reviewer-rating
dispersion from Paper Copilot paperlists.

Outputs:
    results/empirical_iclr.csv
    results/empirical_nips.csv
    results/empirical_summary.json

Each row: venue, year, n_submissions, n_accepted, accept_rate,
mean_rating, rating_dispersion (mean of per-paper rating std),
reviewer_disagreement (mean of |max-min| per paper).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import statistics

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPERLISTS = ROOT / "code" / "paperlists"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


# Statuses that count as "accepted" (top-tier presentation).
ACCEPTED_STATUSES = {
    "Poster", "Spotlight", "Oral", "Talk", "Top 5%", "Top 25%",
    "Notable Top 25%", "Notable Top 5%", "Highlight", "Best Paper",
    "Award", "Outstanding Paper", "Workshop",  # workshop = soft accept; we exclude later
}
# Strict "main-track accepted":
MAIN_ACCEPTED = {
    "Poster", "Spotlight", "Oral", "Talk", "Top 5%", "Top 25%",
    "Notable Top 25%", "Notable Top 5%", "Highlight", "Best Paper",
    "Award", "Outstanding Paper",
}
REJECTED_STATUSES = {"Reject", "Withdraw", "Desk Reject", "Withdrawn"}


def parse_rating_field(rating_str: str) -> list[float]:
    """Parse a rating string like '6;3;6;5' into a list of floats."""
    if not rating_str:
        return []
    out = []
    for tok in str(rating_str).split(";"):
        tok = tok.strip()
        if not tok:
            continue
        try:
            out.append(float(tok))
        except ValueError:
            continue
    return out


def summarize_year(json_path: Path) -> dict | None:
    try:
        with open(json_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, list) or len(data) == 0:
        return None

    n_total = len(data)
    n_accept = 0
    n_reject = 0
    n_with_rating = 0

    rating_means: list[float] = []
    rating_stds: list[float] = []
    rating_ranges: list[float] = []
    accepted_ratings: list[float] = []
    rejected_ratings: list[float] = []

    for entry in data:
        status = entry.get("status", "")
        # Filter out clearly non-conference items (workshops, withdrawals before review)
        is_accept = status in MAIN_ACCEPTED
        is_reject = status in REJECTED_STATUSES
        if is_accept:
            n_accept += 1
        if is_reject:
            n_reject += 1

        ratings = parse_rating_field(entry.get("rating", ""))
        if len(ratings) >= 2:
            n_with_rating += 1
            rating_means.append(float(np.mean(ratings)))
            rating_stds.append(float(np.std(ratings, ddof=1)))
            rating_ranges.append(float(max(ratings) - min(ratings)))
            if is_accept:
                accepted_ratings.append(float(np.mean(ratings)))
            elif is_reject:
                rejected_ratings.append(float(np.mean(ratings)))

    accept_rate = n_accept / max(n_total, 1)
    return {
        "n_total": n_total,
        "n_accept": n_accept,
        "n_reject": n_reject,
        "accept_rate": accept_rate,
        "n_with_rating": n_with_rating,
        "mean_rating": float(np.mean(rating_means)) if rating_means else None,
        "mean_rating_std": float(np.mean(rating_stds)) if rating_stds else None,
        "mean_rating_range": float(np.mean(rating_ranges)) if rating_ranges else None,
        "delta_accept_reject": (
            float(np.mean(accepted_ratings) - np.mean(rejected_ratings))
            if accepted_ratings and rejected_ratings else None
        ),
        "n_accepted_with_rating": len(accepted_ratings),
        "n_rejected_with_rating": len(rejected_ratings),
    }


def extract_venue(venue_dir: Path) -> pd.DataFrame:
    rows = []
    for p in sorted(venue_dir.glob("*.json")):
        # filename like iclr2024.json or nips1987.json
        stem = p.stem
        # Find trailing 4-digit year
        if len(stem) < 4 or not stem[-4:].isdigit():
            continue
        year = int(stem[-4:])
        venue = stem[:-4]
        summary = summarize_year(p)
        if summary is None:
            continue
        rows.append({"venue": venue, "year": year, **summary})
    return pd.DataFrame(rows)


def main():
    out = {}
    summary_rows = []
    for venue in ("iclr", "nips", "icml", "aaai", "cvpr", "emnlp", "acl"):
        vdir = PAPERLISTS / venue
        if not vdir.is_dir():
            continue
        df = extract_venue(vdir)
        if df.empty:
            continue
        df = df.sort_values("year").reset_index(drop=True)
        path = RESULTS / f"empirical_{venue}.csv"
        df.to_csv(path, index=False)
        out[venue] = {
            "n_years": len(df),
            "year_range": [int(df["year"].min()), int(df["year"].max())],
            "n_submissions_first": int(df["n_total"].iloc[0]),
            "n_submissions_last": int(df["n_total"].iloc[-1]),
            "growth_factor": float(df["n_total"].iloc[-1] / max(df["n_total"].iloc[0], 1)),
        }
        summary_rows.append({
            "venue": venue,
            "n_years": len(df),
            "year_min": int(df["year"].min()),
            "year_max": int(df["year"].max()),
            "n_first": int(df["n_total"].iloc[0]),
            "n_last": int(df["n_total"].iloc[-1]),
        })
        print(
            f"[{venue}] years {df['year'].min()}–{df['year'].max()}: "
            f"submissions {df['n_total'].iloc[0]} → {df['n_total'].iloc[-1]}"
        )

    pd.DataFrame(summary_rows).to_csv(RESULTS / "empirical_summary.csv", index=False)
    with open(RESULTS / "empirical_summary.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nSaved per-venue CSVs and empirical_summary.json to results/")


if __name__ == "__main__":
    main()
