"""Search Semantic Scholar for relevant papers."""
import httpx
import json
import time

queries = [
    "signaling theory peer review academic publishing",
    "gatekeeping scientific publication quality signal",
    "growth academic publishing peer review crisis",
    "journal prestige signal researcher quality",
    "Spence signaling academic career publication",
    "noise reviewer disagreement peer review",
    "publication system efficiency information",
    "predatory journals quality assessment",
    "evaluation researchers publication metrics bibliometrics",
    "career concerns academic publishing",
]

S2_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

results = []
seen_ids = set()

with httpx.Client(timeout=60.0) as client:
    for q in queries:
        print(f"\n=== Query: {q} ===")
        try:
            r = client.get(S2_URL, params={
                "query": q,
                "limit": 20,
                "fields": "title,abstract,authors,year,citationCount,url,openAccessPdf,venue,externalIds",
            })
            if r.status_code == 429:
                time.sleep(10)
                r = client.get(S2_URL, params={
                    "query": q,
                    "limit": 20,
                    "fields": "title,abstract,authors,year,citationCount,url,openAccessPdf,venue,externalIds",
                })
            r.raise_for_status()
            data = r.json()
            for paper in data.get("data", []):
                pid = paper.get("paperId")
                if not pid or pid in seen_ids:
                    continue
                seen_ids.add(pid)
                paper["query"] = q
                results.append(paper)
                title = paper.get("title", "")
                cits = paper.get("citationCount", 0)
                print(f"  - [{cits} cit] {title[:90]}")
            time.sleep(2)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(5)

with open("s2_search_raw.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nTotal unique papers from S2: {len(results)}")
