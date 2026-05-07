"""
Explore EDGAR facts for AXP to find the correct revenue concept name,
then build the final merged quarterly dataset.
"""
import requests, json, pandas as pd

AXP_CIK = "0000004962"
HEADERS = {"User-Agent": "amex-analysis barbiejindal03@gmail.com"}

print("Fetching AXP EDGAR company facts...")
url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{AXP_CIK}.json"
r = requests.get(url, headers=HEADERS, timeout=60)
data = r.json()
us_gaap = data["facts"]["us-gaap"]

# Find all concepts whose name contains 'revenue' or 'Revenue' with USD units
print("\nRevenue-related XBRL concepts in AXP filings:\n")
revenue_concepts = {}
for concept, info in us_gaap.items():
    if "revenue" in concept.lower() or "Revenue" in concept:
        usd_entries = info.get("units", {}).get("USD", [])
        # Only show concepts with 10-Q filings
        quarterly = [e for e in usd_entries if e.get("form") == "10-Q"]
        if quarterly:
            revenue_concepts[concept] = len(quarterly)

for c, n in sorted(revenue_concepts.items(), key=lambda x: -x[1]):
    print(f"  {c:70s}  {n} quarterly filings")
