"""Search arXiv for papers relevant to gatekeeping signaling in publication system."""
import arxiv
import json
import os

queries = [
    "peer review signaling academic publishing",
    "gatekeeping scientific publication quality",
    "journal acceptance signal researcher quality",
    "publication system signaling theory science",
    "growth of science peer review crisis",
    "predatory publishing journal quality signaling",
    "scientific publishing market signaling Spence",
    "career incentives academic publishing peer review",
    "evaluation of researchers publication metrics",
    "noise in peer review reviewer disagreement",
]

results = []
seen_ids = set()

for q in queries:
    print(f"\n=== Query: {q} ===")
    search = arxiv.Search(
        query=q,
        max_results=15,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    try:
        for paper in search.results():
            if paper.entry_id in seen_ids:
                continue
            seen_ids.add(paper.entry_id)
            entry = {
                "title": paper.title,
                "authors": [a.name for a in paper.authors],
                "summary": paper.summary,
                "published": str(paper.published),
                "entry_id": paper.entry_id,
                "pdf_url": paper.pdf_url,
                "categories": paper.categories,
                "query": q,
            }
            results.append(entry)
            print(f"  - {paper.title[:90]}")
    except Exception as e:
        print(f"  Error: {e}")

with open("arxiv_search_raw.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\n\nTotal unique papers found: {len(results)}")
