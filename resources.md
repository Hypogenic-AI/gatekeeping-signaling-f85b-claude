# Resources Catalog

Comprehensive catalog of resources gathered for the **Signaling effect of Gate-keeping in the Publication System** project.

## Summary

| Resource type | Count | Location |
|---|---|---|
| Papers (PDFs) | 45 | `papers/` |
| Datasets (catalogued) | 7 | `datasets/README.md` |
| Code repositories | 4 | `code/` |
| Search-result manifests | 4 | `paper_search_results/` |

---

## Papers

40 PDFs are catalogued by relevance bucket in `papers/README.md`. The most directly relevant are:

| Title | Authors | Year | File | Why central |
|---|---|---|---|---|
| Publishing and Promotion in Economics: The Tyranny of the Top Five | Heckman & Moktan | 2019 | `papers/heckman_moktan_top_five_economics.pdf` | Empirical T5-as-screen baseline |
| Top performers and top journals: Persistent concentration in scientific publishing | Kwiek & Roszka | 2026 | `papers/2603_00069_top_performers_top_journals_concentration.pdf` | Persistent gatekeeping mechanism, 144K scientists |
| The Market for Lemons and the Regulator's Signaling Problem | Long | 2023 | `papers/2312_10896_market_lemons_regulator_signaling.pdf` | Closed-form theoretical template |
| Growth rates of modern science: A bibliometric analysis | Bornmann & Mutz | 2015 | `papers/1402_4578_growth_rates_modern_science_bibliometric.pdf` | Quantifies the volume time series N(t) |
| Disproportion Between Scientific Productivity and Knowledge Amount | Fu et al. | 2021 | `papers/2106_02989_disproportion_productivity_knowledge.pdf` | Information per paper drops with volume |
| Peer Review and the Diffusion of Ideas | Wang, Ma, Wang & Uzzi | 2025 | `papers/2507_11825_peer_review_diffusion_of_ideas.pdf` | 100M reviewer-hours/year scale |
| Paper Copilot: Tracking the Evolution of Peer Review in AI Conferences | Yang, Wei & Pei | 2025 | `papers/2510_13201_paper_copilot_ai_conferences_evolution.pdf` | AI-conference 10K+ submissions empirical anchor |
| AgentReview | Jin et al. | 2024 | `papers/2406_12708_agentreview_llm_dynamics.pdf` | Existing peer-review simulator |
| The AI Review Lottery | Latona et al. | 2024 | `papers/2405_02150_ai_review_lottery.pdf` | Quantifies LLM-induced score inflation |
| AI Conference Peer Review Crisis | (multiple) | 2025 | `papers/2505_04966_ai_conference_peer_review_crisis.pdf` | Independent confirmation of system stress |

See `papers/README.md` for the complete categorized list (sections A–H).

## Datasets

| Name | Source | Coverage | Location | Notes |
|---|---|---|---|---|
| Paper Copilot paperlists | github.com/papercopilot/paperlists | ICLR 2013–2026; NeurIPS 1987+; ICML, AAAI, etc. | `code/paperlists/` | Cloned; ~570 MB, in-repo |
| OpenReview API | api.openreview.net (v1, v2) | ICLR/NeurIPS/COLM/UAI/AISTATS reviews | via `code/openreview-py` | API access; requires account |
| OpenAlex | openalex.org | ~250M works, all journals, 1980–present | via `code/pyalex` | Free, polite-pool email recommended |
| WoS / Bornmann growth data | Web of Science | 38.5M publications 1980–2012 | tables in `papers/1402_4578…pdf` | Aggregate counts; no individual records needed |
| Heckman & Moktan online appendix | nber.org/data-appendix/w25093 | Tenure-track histories, 2000–2010 citations, 30 econ journals | manual download | Online appendix from NBER WP 25093 |
| NeurIPS 2014 reproducibility | inverseprobability.com (Lawrence) | 10% double-reviewed papers | manual download | Famous noise-floor anchor |
| Synthetic data plan | (generated) | Configurable θ, capacity, noise | (will live in `experiments/`) | Drives the theoretical/simulation work |

Detailed download instructions in `datasets/README.md`.

## Code Repositories

| Name | URL | Purpose | Location | Status |
|---|---|---|---|---|
| AgentReview | github.com/Ahren09/AgentReview | LLM-agent peer-review simulator | `code/AgentReview/` | Cloned, not yet run (needs LLM API key) |
| openreview-py | github.com/openreview/openreview-py | Official OpenReview API client | `code/openreview-py/` | Cloned, ready to install |
| pyalex | github.com/J535D165/pyalex | OpenAlex Python client | `code/pyalex/` | Cloned, ready to install |
| paperlists (Paper Copilot data) | github.com/papercopilot/paperlists | Conference submission JSON dumps | `code/paperlists/` | Cloned with full data (~570 MB) |

Detailed setup notes in `code/README.md`.

## Search-Result Manifests

`paper_search_results/` contains JSONL outputs from the paper-finder service:

- `signaling_theory_peer_review_gatekeeping_academic_publishing_diminishing_signal_20260506_200215.jsonl` — 42 papers; included the highly-relevant *Signaling the trustworthiness of science* (PNAS 2019, paywalled).
- `publication_volume_growth_peer_review_quality_signal_information_theory_20260506_200413.jsonl` — included Grimaldo et al. *Reputation or peer review?* (Scientometrics, paywalled).

Raw arXiv search dumps:

- `arxiv_search_raw.json` — 112 papers from 10 broad queries.
- `arxiv_search_more.json` — 98 papers from 15 follow-up queries.
- `arxiv_targeted.json` — 53 papers from 20 targeted title-based queries.
- `arxiv_filtered.json` — 50 highest-scoring relevant papers.

These can be re-mined later if specific additional citations are needed.

---

## Resource Gathering Notes

### Search Strategy

Three complementary search streams:

1. **Paper-finder service** (localhost:8000, when available) — returned high-precision relevance-ranked results. Two queries succeeded; the second (and additional ones I attempted) were rate-limited by the upstream Semantic Scholar.
2. **arXiv API** via the `arxiv` Python package — bulk retrieval of ~150 candidate papers across 35 queries spanning theory (Spence, Akerlof, signaling, lemons, mechanism design), bibliometrics (growth, citations), and contemporary AI-conference issues.
3. **Direct arXiv ID downloads** — once the right IDs were identified via Paper Copilot or arXiv search, PDFs were pulled directly from `arxiv.org/pdf/{id}.pdf`.

### Selection Criteria

Papers were prioritized by:

- Direct relevance to the *signal/gatekeeping/volume* triad in the hypothesis.
- Theoretical clarity (closed-form models > thought pieces).
- Empirical anchors with explicit time-series of submissions, acceptances, or citation distributions.
- Recency for the modern AI-conference context (2024–2026).
- Citation counts ≥ 10 for foundational items, less strict for very recent (2025–2026) work.

### Challenges Encountered

- **Semantic Scholar rate limiting** prevented bulk downloads of papers identified by the paper-finder. Worked around by direct arXiv lookups.
- **Several initially guessed arXiv IDs were wrong** (the same numeric pattern matched unrelated astronomy/ML papers). Cleaned up wrong PDFs and re-downloaded from verified IDs returned by targeted arXiv search.
- **Paywalled core references** — *Signaling the trustworthiness of science* (PNAS 2019) and Grimaldo et al. *Reputation or peer review?* (Scientometrics) could not be downloaded. Their abstracts are preserved in the search-results JSONL files, and we can cite them from there if needed.
- **OpenReview/Semantic Scholar S2 API rate limits** intermittent throughout the session.

### Gaps and Workarounds

- *Spence (1973)* and *Akerlof (1970)* are pre-arXiv classics. Their content is ubiquitous in textbooks; we cite them from the Long (2023) lemons paper (`2312_10896…`) which covers both.
- *Cortes & Lawrence (NeurIPS experiment 2014/2021)* not in arXiv as separate paper, but its summary statistics are documented in Paper Copilot (`2510_13201…`) and other peer-review crisis papers.
- *Grimaldo, Paolucci & Sabater-Mir (2018) reputation-vs-peer-review agent-based model* — paywalled at Scientometrics. We have the abstract and the architecture description from the search results; the AgentReview code (`code/AgentReview/`) covers similar simulation territory.

## Recommendations for Experiment Design

Based on the gathered resources:

1. **Primary dataset(s)**:
   - `code/paperlists/` for empirical N(t) and acceptance trajectories, especially ICLR / NeurIPS / ICML.
   - `pyalex` queries for cross-domain validation (Nature / Science / journal panel).
2. **Baseline methods**:
   - Spence/Akerlof closed-form (no capacity constraint).
   - Heckman & Moktan empirical filter quality (T5 vs non-T5 citation distributions).
   - Pure-noise reviewer model calibrated to Cortes & Lawrence ~50% disagreement number.
3. **Evaluation metrics**:
   - Mutual information I(θ; A) as a function of submission volume N.
   - Posterior contrast E[θ|A=1] − E[θ|A=0].
   - Tail-capture probability Pr(top-1% paper accepted).
   - Calibration curve Pr(accept | θ) for varying N.
4. **Code to adapt/reuse**:
   - `code/AgentReview` — fork to swap LLM reviewers for stochastic noisy reviewers, varying load N.
   - `code/pyalex` — to compute empirical journal-volume time series.
   - Custom analytical model in NumPy/SciPy for the closed-form derivation.
