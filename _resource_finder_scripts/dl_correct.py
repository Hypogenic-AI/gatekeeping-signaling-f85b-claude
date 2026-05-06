"""Download papers with verified arxiv IDs from targeted search."""
import urllib.request
import os
import time

UA = {"User-Agent": "Mozilla/5.0"}

papers = [
    ("2106.02989", "disproportion_productivity_knowledge"),
    ("2303.09020", "system_level_conference_peer_review"),
    ("2109.00923", "auctions_peer_prediction"),
    ("2108.05521", "measurement_integrity_peer_prediction"),
    ("2311.14619", "eliciting_honest_authors_sequential"),
    ("2505.04966", "ai_conference_peer_review_crisis"),
    ("2510.13201", "paper_copilot_ai_conferences_evolution"),
    ("2210.15350", "questionable_journals_less_impactful"),
    ("2204.05390", "alma_distributed_peer_review"),
    ("2511.04820", "drain_of_scientific_publishing"),
    ("1910.05723", "seasonal_entropy_diversity_inequality"),
    ("2006.14830", "metrics_peer_review_agreement"),
    ("2511.01439", "preregistration_grant_peer_review"),
    ("2501.05653", "co_authored_papers_tenure_decisions"),
    ("2511.22965", "diamond_open_access_science_policy"),
    ("2406.12708", "agentreview_llm_dynamics_v2"),  # already have
    # Reputation outliers paper - not on arxiv, on Springer (Grimaldo et al)
]

for aid, name in papers:
    out = f"papers/{aid.replace('.', '_')}_{name}.pdf"
    if os.path.exists(out) and os.path.getsize(out) > 50000:
        print(f"Already: {out}")
        continue
    url = f"https://arxiv.org/pdf/{aid}.pdf"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        if data[:4] != b"%PDF":
            print(f"NOT PDF: {aid}")
            continue
        with open(out, "wb") as f:
            f.write(data)
        print(f"OK: {out} ({len(data)//1024}KB)")
        time.sleep(2)
    except Exception as e:
        print(f"FAIL {aid}: {e}")
        time.sleep(2)
