# Research Plan — Signaling Effect of Gate-keeping in the Publication System

## Motivation & Novelty Assessment

### Why This Research Matters
Modern science relies on a few prestigious venues to certify quality. If
volume growth degrades that signal — empirically observed in AI conferences
(>10K submissions/year at NeurIPS, ICLR) — the system silently loses its
ability to allocate attention and recognize talent. Quantifying *how fast*
the signal degrades, and *what feature of consumption* drives it, has direct
implications for venue policy (capacity expansion, structured review,
researcher-level vs. paper-level evaluation) and for individual scholars
trying to allocate reading time.

### Gap in Existing Work
From `literature_review.md`:
- Akerlof, Spence, Long (2023) give static signaling models that do **not**
  vary submission volume `N` as the explanatory variable.
- Heckman & Moktan (2019) and Kwiek & Roszka (2026) describe gatekeeping
  empirically at single snapshots, not as a function of `N`.
- Bornmann & Mutz (2015) and Fu et al. (2021) describe the volume growth and
  the per-paper information drop, but not via a signaling mechanism.
- AgentReview (2024) and Grimaldo et al. (2018) simulate review pipelines
  but do not vary load `N` and do not include a *reader* consumption model
  with negative-experience feedback.

**No prior work** combines (i) capacity-constrained Bayesian signaling with
explicit `N`, (ii) a reader-side consumption model where bad-paper exposure
erodes the venue prior, and (iii) a researcher-level "bean counting"
identifiability analysis.

### Our Novel Contribution
1. **Closed-form Bayesian signaling model** parameterised by `N` (volume)
   and `C` (capacity). We derive the mutual information `I(θ; A)` and the
   posterior contrast `Δ = E[θ|A=1] − E[θ|A=0]` analytically and show
   `Δ → 0` as `N → ∞` for fixed `C` (and any reviewer noise σ² > 0).
2. **Reader consumption model with negative-experience feedback.** Each
   reader has a fixed time budget; their decision to read a paper from
   venue `V` follows a Bayesian update using both the venue prior and
   their own past sampling history. Negative experiences shift the prior
   downward and create an absorbing "stop reading from V" state. We show
   the venue's effective signal collapses faster than the raw
   `I(θ; A)` because of feedback.
3. **Researcher-level bean-counting identifiability theorem.** Treating
   each researcher as having latent ability `α`, we show that when papers
   become near-uninformative as a quality signal, the order statistic
   "publication count in venue V" becomes asymptotically uninformative
   about `α` for fixed observation horizon — i.e., gatekeeping ceases to
   identify good researchers.
4. **Empirical calibration.** We extract submission-count time series and
   reviewer-rating distributions from `code/paperlists/` (ICLR 2013–2026,
   NeurIPS 2018–2024) and show our model's predicted signal degradation
   tracks the empirical reviewer-disagreement growth.

### Experiment Justification

| # | Experiment | Why needed |
|---|---|---|
| E1 | Closed-form derivation + numerical sweep of `I(θ; A)` and `Δ(N)` for Gaussian and heavy-tailed quality distributions | Establishes core theorem and shows it does not depend on the Gaussian assumption |
| E2 | Reader consumption simulation with negative-experience feedback | Shows the *effective* signal (probability a researcher reads accepted papers) collapses faster than `I(θ;A)` alone |
| E3 | Researcher-level bean-counting Monte Carlo | Quantifies how many true high-`α` researchers are misranked at high `N` and tests the identifiability claim |
| E4 | Empirical calibration on ICLR/NeurIPS Paper Copilot data | Tests whether predicted degradation rates match observed reviewer disagreement and inflation in submission volume |
| E5 | Robustness sweep: vary capacity policy `C(N)` (constant vs. linear in `N` vs. sublinear) | Tests whether expanding capacity restores the signal — informs policy |

---

## Research Question
*As the number of papers in prestigious venues grows, how rapidly does the
signaling effect of gate-keeping diminish, and through what mechanisms
(paper-level Bayesian decay, reader-feedback collapse, researcher-level
bean-counting) does it diminish?*

Decomposed sub-hypotheses:
- **H1 (paper-level):** For fixed capacity `C` and reviewer noise σ² > 0,
  the mutual information `I(θ; A)` and posterior contrast `Δ` strictly
  decrease in `N` and tend to zero.
- **H2 (consumption):** When a reader's reading decision incorporates
  negative-experience feedback, the *effective* venue signal collapses
  for the reader before `I(θ; A)` itself collapses.
- **H3 (researcher-level):** The publication-count rank of researchers
  becomes asymptotically uninformative about ability `α` as the per-paper
  signal vanishes ("bean counting fails").
- **H4 (empirical):** Reviewer-rating dispersion and rejection rates in
  ICLR/NeurIPS over 2013–2026 follow patterns consistent with the model
  (specifically: reviewer disagreement σ̂² and acceptance-rate-conditioned
  posterior contrast trend in the predicted direction).

## Background and Motivation
See `literature_review.md`. Top-line: the volume of submissions to
prestigious venues has grown 1000× in some AI conferences over a decade
(`code/paperlists/iclr/iclr2013.json` vs `iclr2024.json`), capacity has
not kept pace, and reviewer noise is empirically high (Cortes & Lawrence
~50% disagreement). Our model is the first to tie all three to a
single signal-degradation prediction.

## Proposed Methodology

### Approach
Two-layer construction (per `literature_review.md` §8):
- **Layer 1 (analytical):** Spence-Akerlof-style Bayesian signaling with
  capacity-constrained gatekeeper. Gaussian-quality and reviewer-noise
  setup admits closed forms; we then verify the qualitative result for
  Pareto/log-normal quality.
- **Layer 2 (simulation):** Stochastic agent simulation. Authors draw
  quality, reviewers produce noisy scores, top-K accepted, readers
  consume with bounded budget and update their venue prior from
  experience. Researcher-level analysis takes the resulting publication
  records.

### Experimental Steps
1. **E1 — Closed-form & numerical signaling.** Derive `Δ(N, C, σ²)` and
   `I(θ; A)` for Gaussian. Numerically compute for Pareto and log-normal
   quality. Plot vs. `N` for several capacity policies.
2. **E2 — Reader consumption with feedback.** Simulate `M` readers with
   time budget `B`. Each round: a reader picks a venue based on prior,
   reads a paper from that venue (drawn from the venue's accepted pool),
   updates prior using observed quality. Measure: probability of reading,
   total quality consumed, time-to-prior-collapse.
3. **E3 — Researcher-level bean counting.** Sample researchers with latent
   `α`, generate paper qualities `θ ∼ p(·|α)`, run them through the
   gatekeeper, and rank by acceptance count. Compute Spearman ρ between
   true `α` rank and acceptance-count rank as a function of `N`.
4. **E4 — Empirical calibration.** Extract ICLR/NeurIPS submission counts
   per year and (where available) reviewer-rating dispersion. Fit the
   model's `σ²` and capacity policy and compare predicted vs. empirical
   trajectories.
5. **E5 — Capacity policy sweep.** Repeat E1–E3 under three capacity
   policies (constant, sublinear, linear in `N`) to test whether
   expanding capacity rescues the signal.

### Baselines
- **Pure Spence (no capacity):** `I(θ; A)` is flat in `N`.
- **No-capacity-constraint Bayesian:** acceptance probability follows
  the calibration curve set by σ² alone.
- **Heckman & Moktan empirical reference:** target T5 vs non-T5
  citation overlap (top-5 captures only ~50% of top-1% papers).
- **Cortes & Lawrence noise floor:** reviewer disagreement ~50% at
  NeurIPS 2014 — used to anchor σ².

### Evaluation Metrics
- `I(θ; A)`: mutual information between true quality and acceptance.
- `Δ = E[θ|A=1] − E[θ|A=0]`: posterior contrast.
- `Pr(top-1% accepted)`: tail capture.
- `Spearman ρ(true α, acceptance-count)`: researcher-level identifiability.
- `Pr(reader reads accepted paper at time t)`: effective signal under
  reader feedback.
- Calibration curve `Pr(A=1 | θ)`.

### Statistical Analysis Plan
- All Monte Carlo: 1000 trials per (N, C, σ²) cell, report mean ± 95% CI
  via bootstrap (10K resamples).
- Hypothesis tests: two-sided test on slope of `Δ(N)`, Mann-Kendall
  trend test for monotonicity. α = 0.05.
- Empirical calibration: report predicted vs. observed correlation and
  RMSE.

## Expected Outcomes
- **Supports H1**: closed form yields `Δ(N) = O(1/√N)` for fixed `C` and
  Gaussian `θ`.
- **Supports H2**: reader-feedback simulations show effective signal
  collapses at a *threshold* `N` rather than smoothly.
- **Supports H3**: Spearman ρ between α and publication count drops
  below 0.5 well before `Δ` does, because rank statistics amplify
  per-paper noise.
- **H4 partially testable**: ICLR rating-dispersion data only covers
  2017–2026 with structured reviews; we expect dispersion increases.

## Timeline and Milestones
| Step | Time |
|---|---|
| Plan + setup (this file + env) | 30 min |
| Empirical N(t) extraction | 30 min |
| E1 closed-form + plotting | 45 min |
| E2 reader simulation | 45 min |
| E3 researcher-level Monte Carlo | 30 min |
| E4 empirical calibration | 45 min |
| E5 capacity sweep | 30 min |
| Analysis + REPORT.md | 60 min |

## Potential Challenges
- *Heavy-tailed quality* may break Gaussian closed form — addressed by
  numerical computation.
- *ICLR rating data structure* varies by year — early years (2013–2016)
  lack rating fields. Addressed by graceful degradation: use submission
  counts and acceptance rates only for those years.
- *Capacity policy* is empirically not constant; some venues do expand.
  We document the empirical capacity trajectory and use it as the
  calibration target rather than assuming constancy.

## Success Criteria
- Closed-form derivation complete and `Δ(N) → 0` shown rigorously.
- Three simulation experiments (E2, E3, E5) execute without error and
  produce monotone-trend results.
- Empirical extraction (E4) yields a consistent ICLR/NeurIPS time
  series and a calibration plot.
- REPORT.md contains all results with figures and statistical tests.
