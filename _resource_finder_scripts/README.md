# Resource-finder helper scripts

These scripts were used during the resource-finding phase to discover and
download papers via arXiv and Semantic Scholar. They are not needed for the
experiment runner phase, but kept for reproducibility.

- `search_arxiv.py`, `search_more.py`, `find_more_arxiv.py` — broad and targeted arXiv queries
- `search_semantic_scholar.py` — Semantic Scholar bulk search (rate-limited)
- `filter_arxiv.py` — score arXiv results by relevance keywords
- `download_papers.py`, `dl_specific.py`, `dl_correct.py`, `dl_more.py` — paper downloaders
- `download_s2.py` — try to download via S2 OpenAccess PDFs

Outputs (in repo root):
- `arxiv_search_raw.json`, `arxiv_search_more.json`, `arxiv_targeted.json`, `arxiv_filtered.json`
- `s2_search_raw.json` (failed: rate-limited)
- `paper_search_results/*.jsonl` (paper-finder results)
