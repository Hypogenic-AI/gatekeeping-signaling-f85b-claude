"""Targeted search for theoretical / signaling-economics papers on academic publishing."""
import arxiv
import json
import time

queries = [
    "information cascade scientific peer review",
    "lemons market academic publishing asymmetric information",
    "reputation publishing impact factor",
    "screening selection academia tenure publication",
    "diffusion innovation peer review model",
    "Bayesian model peer review acceptance",
    "competition prestige academic publishing model",
    "agent based model peer review",
    "mechanism design peer review",
    "review fatigue scientific publishing",
    "open access journal proliferation",
    "journal impact factor inflation",
    "paper inflation academic publishing volume",
    "scientific productivity paper count quality",
    "saturation peer review system",
]

results = []
seen_ids = set()

for q in queries:
    print(f"\n=== Query: {q} ===")
    search = arxiv.Search(
        query=q,
        max_results=10,
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
        time.sleep(1)
    except Exception as e:
        print(f"  Error: {e}")
        time.sleep(2)

with open("arxiv_search_more.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nTotal new papers: {len(results)}")
