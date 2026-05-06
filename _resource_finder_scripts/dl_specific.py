"""Download specific known-relevant papers via direct URLs."""
import urllib.request
import os
import time

UA = {"User-Agent": "Mozilla/5.0 (compatible; research-bot)"}

papers = [
    # arXiv IDs
    ("https://arxiv.org/pdf/2406.12708.pdf", "papers/2406_12708_agentreview_llm_dynamics.pdf"),
    # PMC for PNAS Trustworthiness signaling
    ("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6765233/pdf/pnas.201913039.pdf", "papers/PMC6765233_signaling_trustworthiness_science.pdf"),
    # AI Conference Peer Review Crisis - 2025
    ("https://arxiv.org/pdf/2505.01951.pdf", "papers/2505_01951_ai_conf_peer_review_crisis.pdf"),
    # System-level analysis of conference peer review (Schaerer et al)
    ("https://arxiv.org/pdf/2207.13620.pdf", "papers/2207_13620_system_level_conference_peer_review.pdf"),
    # Auctions and peer prediction for academic peer review
    ("https://arxiv.org/pdf/2305.09678.pdf", "papers/2305_09678_auctions_peer_prediction.pdf"),
    # Heckman & Moktan paper on top-five economics journals
    ("https://www.nber.org/system/files/working_papers/w25093/w25093.pdf", "papers/heckman_moktan_top_five_economics.pdf"),
    # Disproportion productivity vs knowledge amount
    ("https://arxiv.org/pdf/2106.10184.pdf", "papers/2106_10184_disproportion_productivity_knowledge.pdf"),
    # A System-Level Analysis of Conference Peer Review (different ID maybe)
    ("https://arxiv.org/pdf/2406.05088.pdf", "papers/2406_05088_what_drives_paper_acceptance.pdf"),
    # NeurIPS 2014 experiment - Cortes & Lawrence reproducibility
    ("https://arxiv.org/pdf/2109.09774.pdf", "papers/2109_09774_neurips_experiment.pdf"),
    # Eliciting honest information from authors
    ("https://arxiv.org/pdf/2311.14619.pdf", "papers/2311_14619_eliciting_honest_authors.pdf"),
]

for url, out in papers:
    if os.path.exists(out) and os.path.getsize(out) > 20000:
        print(f"Already: {out}")
        continue
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        # Verify PDF
        if data[:4] != b"%PDF":
            print(f"NOT PDF: {url} (header={data[:20]!r})")
            continue
        with open(out, "wb") as f:
            f.write(data)
        print(f"OK: {out} ({len(data)//1024}KB)")
        time.sleep(2)
    except Exception as e:
        print(f"FAIL {url}: {e}")
        time.sleep(2)
