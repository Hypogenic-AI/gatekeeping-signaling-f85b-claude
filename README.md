# Signaling Effect of Gate-keeping in the Publication System

A mathematical model — closed-form Bayesian signaling + agent simulation +
empirical calibration on AI-conference data — for how the signaling
effect of gate-keeping in scientific publishing diminishes as
submission volume grows.

## Key findings

- **Empirical (ICLR 2017–2026):** The standardized posterior contrast
  `Δ̂ / σ̂_rating` between accepted and rejected papers fell from 2.55
  (N = 490) to 1.08 (N = 19,814). OLS slope on `log N`:
  `−0.32`, `R² = 0.85`, `p = 1.1 × 10⁻³`. Mean per-paper reviewer SD
  rose from 0.86 to 1.53 (Kendall `τ = +0.64`, `p = 0.031`).
- **Paper level (analytical):** Under fixed venue capacity `K` and
  reviewer noise `σ`, mutual information `I(θ; A)` and tail recall
  `Pr(top-1% accepted)` both fall monotonically in `N` for Gaussian,
  log-normal, and Pareto quality distributions (Kendall `τ ≤ −0.95`,
  `p < 10⁻⁶`).
- **Researcher level:** Under fixed capacity, `Spearman ρ(α, count)`
  drops from 0.78 (M = 200) to 0.26 (M = 20,000). 95.5% of researchers
  end up with zero publications. Mann–Whitney U `p = 0.004`.
  Capacity expansion (`K = 0.30·N`) restores `ρ ≈ 0.77`.
- **Reader level:** A finite reading budget `B` makes the venue label
  *necessary but not sufficient* — under linear-`K` policy, `B/K → 0`.

## Reproduce

```bash
source .venv/bin/activate
python src/empirical_extraction.py        # extract N(t), accept rate, Δ̂
python src/analytical_signaling.py        # closed-form sweep
python src/consumption_model.py           # reader simulation
python src/researcher_bean_counting.py    # researcher simulation
python src/make_figures.py                # generate Figs 1–8
python src/statistical_tests.py           # trend/comparison tests
```

Total runtime `< 60 s` on CPU. Random seeds explicit; deps pinned in
`pyproject.toml` / `uv.lock`.

## Files

| Path | Purpose |
|---|---|
| `REPORT.md` | Full research report — read this for the complete write-up. |
| `planning.md` | Phase-0/1 motivation, novelty, and detailed plan. |
| `literature_review.md` | Pre-gathered literature synthesis. |
| `resources.md` | Catalogue of papers, datasets, code in this workspace. |
| `src/` | All experiment scripts. |
| `figures/` | 8 generated PNGs referenced from `REPORT.md`. |
| `results/` | CSV/JSON outputs of every experiment. |
| `code/paperlists/` | Paper Copilot data (in-repo). |
| `papers/` | 45 PDFs. |

See `REPORT.md` § 8 for full reproducibility details.
