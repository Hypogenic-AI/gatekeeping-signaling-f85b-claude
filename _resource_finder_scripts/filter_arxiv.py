"""Filter arXiv results for relevance to gatekeeping/signaling/publication system."""
import json
import re

with open("arxiv_search_raw.json") as f:
    papers = json.load(f)

# Keywords that indicate relevance to our hypothesis
core_kw = [
    "gatekeep", "signal", "peer review", "publication", "journal", "publish",
    "scientific", "researcher", "academic", "citation", "bibliometric",
    "predatory", "growth of science", "career", "evaluation",
    "reviewer", "acceptance", "rejection", "scientometric",
]
# Strong negative indicators (clearly off-topic)
neg = [
    "helmholtz", "fem", "finite element", "market clearing", "turkish",
    "speech-to-text", "object tracking", "amm", "automated market maker",
    "code generation", "wavenumber", "particle", "boundary integral",
    "logic encryption", "tabular data", "manufacturing",
    "speech recognition", "image", "vision", "visual",
    "speech-to-speech", "language model translation",
]

scored = []
for p in papers:
    text = (p["title"] + " " + p["summary"]).lower()
    score = sum(2 if kw in p["title"].lower() else 1 for kw in core_kw if kw in text)
    if any(n in text for n in neg):
        score -= 5
    p["_score"] = score
    if score >= 3:
        scored.append(p)

scored.sort(key=lambda x: -x["_score"])

print(f"Total relevant papers: {len(scored)}\n")
for i, p in enumerate(scored[:40]):
    print(f"[{p['_score']:>2}] {p['title']}")
    print(f"     {p['entry_id']}")
    print(f"     {p['published'][:10]} | cats: {','.join(p['categories'][:3])}")
    print()

# Save filtered
with open("arxiv_filtered.json", "w") as f:
    json.dump(scored[:50], f, indent=2)
