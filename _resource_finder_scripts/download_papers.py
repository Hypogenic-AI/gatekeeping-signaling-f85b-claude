"""Download top-relevance papers to papers/."""
import json
import os
import re
import urllib.request
import time

os.makedirs("papers", exist_ok=True)

# Hand-curated top papers from filter (arxiv) — focus on theoretical/quantitative
# relevance to the gatekeeping signaling hypothesis
top_papers = [
    # Core: signaling/gatekeeping/quality
    ("2603.00069", "top_performers_top_journals_concentration"),
    ("2605.02128", "liberata_graph_scientometrics_publishing"),
    ("2401.14952", "AI_change_scientific_publishing_market"),
    ("1402.4578", "growth_rates_modern_science_bibliometric"),
    ("2404.05345", "non_scientific_factors_scholarly_impact"),
    ("2212.05419", "higher_impact_higher_quality_articles"),
    ("2212.05417", "international_coauthorship_quality"),
    # Predatory journals (signal failure)
    ("1912.10228", "predatory_oa_citations"),
    ("2003.08283", "prevalence_predatory_publishing_scopus"),
    ("1906.06856", "evolving_ecosystem_predatory_journals"),
    # Peer review noise/disagreement (signal noise)
    ("2310.18685", "reviewer_disagreement_peer_review"),
    ("2507.14741", "disparities_peer_review_tone"),
    ("1404.0359", "inter_rater_reliability_F1000Prime"),
    ("1806.00287", "performance_peer_review_journals"),
    # Diffusion of ideas / publishing systems
    ("2507.11825", "peer_review_diffusion_of_ideas"),
    ("1711.05822", "changing_roles_scientific_publications"),
    # Conference vs journal (CS)
    ("1806.10674", "conference_vs_journal_cs"),
    # Publication pressure / behavior
    ("2109.09375", "publication_pressure_research_quality"),
    ("2111.15532", "reasons_to_publish_astronomy"),
    # Process-centric peer review analysis
    # Find ID for "What Drives Paper Acceptance" - need to check
]

UA = {"User-Agent": "Mozilla/5.0 (research-bot)"}

for arxiv_id, name in top_papers:
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    out = f"papers/{arxiv_id.replace('.', '_')}_{name}.pdf"
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        print(f"Already have: {out}")
        continue
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        with open(out, "wb") as f:
            f.write(data)
        print(f"Downloaded: {out} ({len(data)//1024} KB)")
        time.sleep(2)
    except Exception as e:
        print(f"FAIL {arxiv_id}: {e}")
        time.sleep(2)
