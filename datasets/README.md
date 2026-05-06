# Datasets for Gatekeeping Signaling Research

This directory documents datasets relevant to the hypothesis: *as the number of papers increases in prestigious journals/conferences, the signaling effect of gate-keeping diminishes*.

Data files themselves are excluded from git (see `.gitignore`); follow the download instructions below to populate.

## 1. Paper Copilot AI Conference Data (PRIMARY)

Already cloned at `code/paperlists/`. Provides per-conference paper lists with submission/acceptance metadata for the major AI/ML/CS venues.

- **Coverage**:
  - ICLR: 2013–2026 (12 years)
  - NeurIPS (nips/): 1987–present (~38 years)
  - ICML, AAAI, IJCAI, AISTATS, COLT, UAI, KDD, CVPR, ICCV, ECCV, WACV, ACL, NAACL, EMNLP, COLING, etc.
- **Format**: One JSON file per conference-year. Each entry contains paper id, title, authors, decision, scores (when available from OpenReview), affiliation, primary area.
- **Why central to this research**: Directly captures the explosive growth of submissions to "prestigious" AI venues. Line counts of the ICLR JSONs alone show ~1000× growth from iclr2013 to iclr2026, providing a natural experiment for the hypothesis.

### Loading
```python
import json
with open("code/paperlists/iclr/iclr2024.json") as f:
    iclr24 = json.load(f)
print(len(iclr24), "submissions")
print(iclr24[0].keys())
```

### Suggested derived series
- Submissions per year (panels: ICLR, NeurIPS, ICML, …).
- Acceptance rate per year.
- Score distribution per year (where reviews are open).
- Affiliation concentration (Gini, HHI).

---

## 2. OpenReview API Data (ICLR/NeurIPS reviews)

Open peer reviews and scores for venues that publish them. Already covered by Paper Copilot snapshots, but the live API is needed for fresh pulls.

- **Source**: https://api.openreview.net (v2 at https://api2.openreview.net)
- **Python client**: `code/openreview-py/` (cloned)
- **Coverage**: ICLR 2017–present; NeurIPS 2021+ (datasets/benchmarks track 2021+, main from 2024); UAI, COLM, AISTATS some years.

### Download
```python
import openreview
client = openreview.api.OpenReviewClient(baseurl="https://api2.openreview.net")
notes = client.get_notes(invitation="ICLR.cc/2024/Conference/-/Submission", limit=1000)
```

For bulk archived dumps, use the Paper Copilot data above and avoid hitting the API.

---

## 3. OpenAlex (Comprehensive bibliometric database)

Open replacement for Microsoft Academic Graph (MAG). Free; covers ~250M works, ~100k journals, ~120k institutions.

- **Source**: https://docs.openalex.org/
- **Python client**: `code/pyalex/` (cloned)
- **Snapshot**: monthly full snapshot, ~330 GB compressed (S3 `s3://openalex/data/`)

### Download (selective query, recommended)
```python
import pyalex
pyalex.config.email = "your@email"  # for polite pool
from pyalex import Works, Sources
# Yearly publication counts in Nature
nature = Sources().filter(display_name="Nature").get()
# All works in 2024 from Nature
works = Works().filter(primary_location={"source": {"id": nature[0]['id']}}, publication_year=2024).get()
```

### Suggested series
- Annual paper counts per top-tier journal (Nature, Science, Cell, NEJM, JAMA, AER, QJE, …) over 1980–2024.
- Citation distribution per year per journal (compare top-decile journals vs. rest).
- Number of distinct journals indexed per year (proliferation indicator).

---

## 4. Web of Science / Scopus growth data (Bornmann & Mutz)

Used by *Bornmann & Mutz (2015) — Growth rates of modern science* (paper in `papers/`). Aggregate publication counts 1980–2012 by year and discipline.

- **Source**: Web of Science API (subscription) or Scopus.
- **Free alternative**: Bornmann's reproducibility data on GitHub: search "bornmann growth rates" or use the publicly aggregated tables in the paper PDF (Table 2 onward).
- **What we need**: yearly publication counts, ideally split into natural sciences / social sciences / humanities. The paper documents three growth regimes (<1% pre-1750, 2–3% interwar, 8–9% post-WWII).

### Manual extraction
The growth rates table is small enough to be transcribed directly from the paper PDF if the API is unavailable.

---

## 5. Heckman & Moktan (2019) Top-5 Economics Journals dataset

The NBER WP 25093 paper (in `papers/`) ships an online appendix with the data on tenure-track careers and T5 publications.

- **Source**: http://www.nber.org/data-appendix/w25093 (NBER online appendix)
- **Coverage**: 30 economics journals, articles 2000–2010, citation counts through 2018; tenure histories of tenure-track economists at top-35 US departments.
- **Use for our research**: Lets us measure the *signal-to-noise* of T5 publications as a quality predictor and how the share of top-1% influential papers appearing in T5 has shifted as overall publication volume grew.

### Download
```bash
mkdir -p datasets/heckman_moktan_w25093
# follow link in paper to NBER appendix; manual download may be required
```

---

## 6. NeurIPS 2014 Reproducibility Experiment (Cortes & Lawrence)

Famous experiment on NeurIPS reviewing inconsistency: 10% of papers were reviewed twice; ~50% of accepted papers would have been rejected by the second committee.

- **Source**: blog posts and follow-ups; the raw data was released by Lawrence at https://inverseprobability.com/2014/12/16/the-nips-experiment
- **Direct relevance**: empirical evidence of high noise in peer-review screening at scale — exactly the signaling-degradation phenomenon we want to model.

---

## 7. Synthetic data plan (theory experiments)

For the theoretical core of this project, we will primarily generate **synthetic data** from agent-based / signaling models calibrated to the empirical series above. Specifically:

- Researcher quality distribution θ ~ F (e.g., Beta or truncated Normal).
- Submission process to top-K journals/conferences with capacity C(t) growing slower than submissions N(t).
- Reviewer noise model (Gaussian with variance σ²(N) increasing in submission load).
- Acceptance rule (rank-based selection given limited capacity).
- Outcome: posterior P(quality | acceptance) — measure how it degrades as N/C grows and σ grows.

No external download required for this; the empirical datasets above will calibrate the parameters.

---

## Sample data snapshot (small, in-repo)

For documentation purposes only, a tiny ICLR sample is available at `code/paperlists/iclr/iclr2013.json` (~2K lines, comfortably git-tracked through the paperlists repo).

## Notes / limitations

- Many publishers (Elsevier, Springer) restrict bulk download. Use OpenAlex as the open alternative.
- Conference acceptance rates pre-2010 are sometimes unavailable for top venues; use community-maintained pages (e.g., openresearch.community, csrankings/conference-acceptance-rates) as fallback.
- For modeling we primarily need *time series of submissions and acceptances*, which is easier to obtain than per-paper review text.
