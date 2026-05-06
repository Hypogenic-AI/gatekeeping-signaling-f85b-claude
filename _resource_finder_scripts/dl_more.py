"""Download highly relevant papers found in arxiv_search_more.json."""
import urllib.request
import os
import time

UA = {"User-Agent": "Mozilla/5.0"}

papers = [
    ("2312.10896", "market_lemons_regulator_signaling"),  # CORE THEORY
    ("2105.03166", "bayesian_info_cascade"),
    ("1303.7274", "reputation_impact_academic_careers"),
    ("1912.06231", "wos_publications_china_tenure"),
    ("2405.02150", "ai_review_lottery"),
    ("2601.19778", "reimagining_peer_review_multi_agent"),
    ("2411.10575", "tenure_research_trajectories"),
    ("2102.00176", "automate_scientific_reviewing"),
    ("2601.17035", "deferred_acceptance_peer_review"),
    ("1910.05723", "seasonal_entropy_papers"),
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
