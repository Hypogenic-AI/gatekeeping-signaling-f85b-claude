"""Find specific papers identified by paper-finder via arXiv title search."""
import arxiv
import urllib.request
import json
import time
import os

UA = {"User-Agent": "Mozilla/5.0 (research-bot)"}

# (search query, expected name)
targets = [
    ("Reputation peer review outliers Grimaldo Paolucci agent-based", "reputation_peer_review_outliers"),
    ("Exploring disproportion scientific productivity knowledge amount KQI", "disproportion_productivity_knowledge"),
    ("System-Level Analysis Conference Peer Review Schaerer", "system_level_conference_peer_review"),
    ("Innovation Suppression Clique Evolution Peer-Review Funding", "innovation_suppression_clique"),
    ("Auctions Peer Prediction Academic Peer Review", "auctions_peer_prediction"),
    ("Eliciting Honest Information Authors Sequential Review", "eliciting_honest_information"),
    ("AI Conference Peer Review Crisis Author Feedback Reviewer Reward", "ai_conference_peer_review_crisis"),
    ("Heckman Moktan top-five economics tenure publication", "heckman_moktan_top_five"),
    ("AgentReview Exploring Peer Review Dynamics LLM", "agentreview_llm_dynamics"),
    ("How Frequently Articles Predatory Open Access Journals Cited", "predatory_oa_cited_2"),
    ("Peer review process past present future Tenant", "peer_review_past_present_future"),
    ("Innovation suppression clique peer review funding Lehman", "innovation_suppression_lehman"),
    ("metric-based research evaluation gatekeeping inclusion 2025", "closing_door_metric_evaluation"),
    ("trustworthiness of science signaling 2019", "trustworthiness_signaling"),
    ("information cascade peer review acceptance Klamer", "info_cascade_peer_review"),
    ("Reviewer disagreement large model peer review study", "reviewer_disagreement_study"),
    ("noise peer review reviewer agreement randomness", "noise_peer_review"),
    ("growth scientific publishing volume Lariviere", "growth_publishing_lariviere"),
    ("Bornmann Mutz peer review F1000 quality reliability inter-rater", "bornmann_mutz_peer_review"),
    ("Larivière Sugimoto inflation publishing impact factor oligopoly", "lariviere_oligopoly"),
]

results = []
seen_ids = set()

for q, name in targets:
    print(f"\n=== Query: {q[:50]} → {name} ===")
    search = arxiv.Search(query=q, max_results=4, sort_by=arxiv.SortCriterion.Relevance)
    try:
        for paper in search.results():
            if paper.entry_id in seen_ids:
                continue
            seen_ids.add(paper.entry_id)
            print(f"  - {paper.title[:90]}")
            print(f"    {paper.entry_id}")
            results.append({
                "title": paper.title,
                "authors": [a.name for a in paper.authors],
                "summary": paper.summary[:600],
                "entry_id": paper.entry_id,
                "pdf_url": paper.pdf_url,
                "categories": paper.categories,
                "_target": name,
            })
        time.sleep(1)
    except Exception as e:
        print(f"  Error: {e}")
        time.sleep(2)

with open("arxiv_targeted.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nTotal: {len(results)} papers")
