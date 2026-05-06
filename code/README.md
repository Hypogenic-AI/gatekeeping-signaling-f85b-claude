# Cloned Code Repositories

These repositories provide tooling and data for the gatekeeping-signaling research project.

---

## 1. AgentReview — `code/AgentReview/`

LLM-agent simulation of peer review dynamics.

- **URL**: https://github.com/Ahren09/AgentReview
- **Paper**: Jin et al., *AgentReview: Exploring Peer Review Dynamics with LLM Agents* (EMNLP 2024). Local PDF: `papers/2406_12708_agentreview_llm_dynamics.pdf`.
- **What it provides**:
  - Multi-agent simulation of the full review pipeline (authors, reviewers, area chairs, program chairs).
  - Configurable reviewer count, reviewer "quality"/biases, paper "true quality".
  - Eight-stage review process (initial reviews, rebuttals, discussion, AC decision, etc.).
  - Templates for reviewer personas (responsible/irresponsible, biased, knowledgeable/unknowledgeable).
- **Why useful for our research**: This is the closest existing implementation of a *simulator* for peer-review-as-signal. We can extend it to vary submission volume N and observe how the signal-to-noise of acceptance changes — directly testing our hypothesis.
- **Entry points**:
  - `run_paper_review_cli.py` — review a single paper.
  - `run_paper_decision_cli.py` — make decision for a set of reviews.
  - `agentreview/` — core library (agent definitions, environment).
  - `notebooks/` — example analyses.
- **Setup**:
  ```bash
  cd code/AgentReview
  pip install -e .
  # requires OpenAI API key for LLM calls
  ```
- **Limitations**: Defaults to GPT-4 calls, which would be expensive at scale. For our experiments we may swap in a cheaper local LLM or replace LLM reviewer with a simpler stochastic model that captures the same noise structure.

---

## 2. openreview-py — `code/openreview-py/`

Official Python client for the OpenReview API.

- **URL**: https://github.com/openreview/openreview-py
- **What it provides**: Programmatic access to OpenReview submissions, reviews, decisions for ICLR, NeurIPS, COLM, AISTATS, UAI, etc.
- **Why useful**: Lets us pull live data from current/past reviewing cycles to validate / extend the static Paper Copilot snapshots.
- **Entry points**: `openreview.api.OpenReviewClient` (v2) and `openreview.Client` (v1).
- **Setup**: `uv add openreview-py` (already on PyPI).

---

## 3. pyalex — `code/pyalex/`

Python client for the OpenAlex bibliometric database.

- **URL**: https://github.com/J535D165/pyalex
- **What it provides**: Free, open access to ~250M scholarly works with citation, author, institution, and journal metadata. Replacement for Microsoft Academic Graph.
- **Why useful**: Enables us to compute publication-volume time series for any journal/conference, citation distributions, and journal proliferation — the empirical anchors for our signaling model.
- **Setup**: `uv add pyalex`. Set `pyalex.config.email = "..."` to use the polite pool (faster, no rate-limit issues).

---

## 4. paperlists (Paper Copilot data) — `code/paperlists/`

Standardized JSON dumps of submissions/reviews for AI/ML/CS conferences.

- **URL**: https://github.com/papercopilot/paperlists
- **Paper**: Yang, Wei & Pei, *Paper Copilot: Tracking the Evolution of Peer Review in AI Conferences* (arXiv:2510.13201). Local PDF: `papers/2510_13201_paper_copilot_ai_conferences_evolution.pdf`.
- **What it provides**: Per-conference, per-year JSON files in `iclr/`, `nips/`, `icml/`, etc. Each file lists submissions with title, authors, decision, scores (when public), affiliation, primary area.
- **Why useful**: Provides the *empirical growth-of-prestigious-venues* time series that motivates the hypothesis. ICLR alone shows ~1000× line-count growth from 2013 to 2026. This is *the* primary empirical dataset.
- **Size**: ~570 MB unpacked. The data is included in this clone (it lives in the repo).

---

## Suggested integration plan for the experiment runner

The experiment runner should:

1. Use `code/paperlists/` to compute empirical growth curves N(t) for ICLR / NeurIPS / ICML and compute observed acceptance-rate trajectories.
2. Optionally use `pyalex` to enrich with journal data (e.g., Nature/Science volume vs. T5 economics journals), to test cross-domain generality.
3. Build a signaling model (Akerlof–Spence-style with capacity constraint and reviewer noise) implemented as either:
   - Closed-form: derive how the posterior P(θ | accept) depends on N, capacity C, and noise σ²(N).
   - Agent-based: extend `AgentReview` or a lightweight simulator to vary N and measure realized signal quality.
4. Calibrate parameters to the empirical N(t) and acceptance-rate trajectories from steps 1–2.
5. Report: how the *information content* of acceptance — measured by mutual information I(quality; accept) or the gap E[θ | accept] − E[θ | reject] — degrades as N grows.

## Repos considered but not cloned

- `peerread` (NLP peer review dataset) — superseded by Paper Copilot for our purposes.
- `csrankings/conference-acceptance-rates` — small but Paper Copilot already provides equivalent info.
- ASReview — for systematic reviews of literature, not directly applicable to our model.
