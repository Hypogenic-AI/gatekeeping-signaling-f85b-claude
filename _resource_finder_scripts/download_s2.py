"""Try to download papers found via paper-finder using Semantic Scholar IDs."""
import httpx
import os
import time

# Highly relevant papers from paper-finder
papers = [
    # (S2 corpus ID, descriptive name)
    ("202747249", "signaling_trustworthiness_science_2019"),
    ("277490670", "metric_evaluation_gatekeeping_2025"),
    ("258615819", "auctions_peer_prediction_review"),
    ("250660160", "fake_peer_reviews_boundary"),
    ("258413442", "improve_peer_review_four_schools"),
    ("0ce300fc37302e4d76fe2e", "towards_theorizing_peer_review"),
    ("270562353", "agentreview_llm_dynamics"),
    ("261124992", "gender_submission_elite_journals"),
    ("54518478", "peer_review_still_working_2018"),
    ("271537255", "peer_review_gold_standard_2022"),
    ("208131657", "diverse_niches_megajournals"),
    ("6635829", "scientific_utopia_communication"),
]

S2_PAPER_URL = "https://api.semanticscholar.org/graph/v1/paper/CorpusId:{cid}"

os.makedirs("papers", exist_ok=True)

with httpx.Client(timeout=60.0) as client:
    for cid, name in papers:
        try:
            r = client.get(
                S2_PAPER_URL.format(cid=cid),
                params={"fields": "title,authors,year,abstract,openAccessPdf,externalIds,url"},
            )
            if r.status_code == 429:
                time.sleep(15)
                r = client.get(
                    S2_PAPER_URL.format(cid=cid),
                    params={"fields": "title,authors,year,abstract,openAccessPdf,externalIds,url"},
                )
            r.raise_for_status()
            d = r.json()
            print(f"\n{d.get('title', 'NO TITLE')[:80]}")
            pdf = d.get("openAccessPdf")
            if pdf and pdf.get("url"):
                print(f"  PDF: {pdf['url']}")
                # Try to download
                out = f"papers/s2_{cid}_{name}.pdf"
                if not os.path.exists(out) or os.path.getsize(out) < 10000:
                    try:
                        pr = client.get(pdf["url"], follow_redirects=True, timeout=60)
                        if pr.status_code == 200 and len(pr.content) > 10000:
                            with open(out, "wb") as f:
                                f.write(pr.content)
                            print(f"  SAVED ({len(pr.content)//1024} KB)")
                        else:
                            print(f"  PDF unavailable status={pr.status_code}")
                    except Exception as e:
                        print(f"  PDF DL fail: {e}")
            else:
                print("  No open access PDF")
            ext = d.get("externalIds") or {}
            print(f"  IDs: {ext}")
            time.sleep(1.5)
        except Exception as e:
            print(f"FAIL {cid}: {e}")
            time.sleep(3)
