"""
fact_checker.py
===============
Sentinelle Numérique — Groupe 4 : Fact-Checker Automatisé
SUP'PTIC | ITT3-IR | 2025-2026
 
The user types a claim or keyword.
The system searches Wikipedia AND Google News,
then returns a confidence score.
 
Dependencies (install once):
    python -m pip install requests wikipedia-api
"""
 
import requests
import time
 
# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────
 
# Google News API key — get yours free at https://newsapi.org
# Replace the string below with your own key
GOOGLE_NEWS_API_KEY = "YOUR_API_KEY_HERE"
 
 
# ─────────────────────────────────────────────────────────────
# WIKIPEDIA SERVICE
# ─────────────────────────────────────────────────────────────
 
def search_wikipedia(query: str) -> dict:
    """
    Searches Wikipedia for the claim/keyword.
    Uses the free Wikipedia REST API — no key needed.
 
    Returns a dict with:
        found    : bool
        title    : str
        summary  : str (first 300 chars)
        url      : str
        score    : float (0.0 to 1.0)
    """
    print(f"\n  [Wikipedia] Searching for: '{query}'...")
 
    try:
        # Step 1: search for matching articles
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 3,
        }
        response = requests.get(search_url, params=search_params, timeout=5)
        data = response.json()
 
        results = data.get("query", {}).get("search", [])
 
        if not results:
            print("  [Wikipedia] ✗ No results found.")
            return { "found": False, "title": "", "summary": "", "url": "", "score": 0.0 }
 
        # Step 2: get the summary of the top result
        top_title = results[0]["title"]
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{top_title.replace(' ', '_')}"
        summary_response = requests.get(summary_url, timeout=5)
        summary_data = summary_response.json()
 
        summary  = summary_data.get("extract", "No summary available.")[:400]
        page_url = summary_data.get("content_urls", {}).get("desktop", {}).get("page", "")
 
        # Step 3: compute a basic relevance score
        # How many words from the query appear in the summary?
        query_words = set(query.lower().split())
        summary_words = set(summary.lower().split())
        overlap = len(query_words & summary_words)
        score = min(overlap / max(len(query_words), 1), 1.0)
        score = round(0.4 + score * 0.4, 2)   # scale: 0.40 → 0.80
 
        print(f"  [Wikipedia] ✓ Found: '{top_title}'")
        print(f"  [Wikipedia]   Score : {score}")
 
        return {
            "found"  : True,
            "title"  : top_title,
            "summary": summary,
            "url"    : page_url,
            "score"  : score,
        }
 
    except requests.exceptions.ConnectionError:
        print("  [Wikipedia] ✗ No internet connection.")
        return { "found": False, "title": "", "summary": "", "url": "", "score": 0.0 }
    except Exception as e:
        print(f"  [Wikipedia] ✗ Error: {e}")
        return { "found": False, "title": "", "summary": "", "url": "", "score": 0.0 }
 
 
# ─────────────────────────────────────────────────────────────
# GOOGLE NEWS SERVICE
# ─────────────────────────────────────────────────────────────
 
def search_google_news(query: str) -> dict:
    """
    Searches Google News (via NewsAPI) for recent articles
    matching the claim/keyword.
 
    Returns a dict with:
        found    : bool
        articles : list of dicts (title, source, url)
        count    : int
        score    : float (0.0 to 1.0)
    """
    print(f"\n  [Google News] Searching for: '{query}'...")
 
    # If no API key provided, return a demo result
    if GOOGLE_NEWS_API_KEY == "YOUR_API_KEY_HERE":
        print("  [Google News] ⚠ No API key set.")
        print("  [Google News]   Get a free key at https://newsapi.org")
        print("  [Google News]   Then replace YOUR_API_KEY_HERE in the code.")
        return {
            "found"   : False,
            "articles": [],
            "count"   : 0,
            "score"   : 0.0,
        }
 
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q"          : query,
            "language"   : "en",
            "sortBy"     : "relevancy",
            "pageSize"   : 5,
            "apiKey"     : GOOGLE_NEWS_API_KEY,
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
 
        if data.get("status") != "ok":
            print(f"  [Google News] ✗ API error: {data.get('message', 'Unknown')}")
            return { "found": False, "articles": [], "count": 0, "score": 0.0 }
 
        articles = data.get("articles", [])
        count    = len(articles)
 
        if count == 0:
            print("  [Google News] ✗ No articles found.")
            return { "found": False, "articles": [], "count": 0, "score": 0.0 }
 
        # Score based on number of corroborating articles found
        score = min(0.3 + (count / 5) * 0.5, 0.80)
        score = round(score, 2)
 
        clean_articles = []
        for a in articles[:5]:
            clean_articles.append({
                "title" : a.get("title", "No title"),
                "source": a.get("source", {}).get("name", "Unknown"),
                "url"   : a.get("url", ""),
            })
 
        print(f"  [Google News] ✓ Found {count} articles.")
        print(f"  [Google News]   Score : {score}")
 
        return {
            "found"   : True,
            "articles": clean_articles,
            "count"   : count,
            "score"   : score,
        }
 
    except requests.exceptions.ConnectionError:
        print("  [Google News] ✗ No internet connection.")
        return { "found": False, "articles": [], "count": 0, "score": 0.0 }
    except Exception as e:
        print(f"  [Google News] ✗ Error: {e}")
        return { "found": False, "articles": [], "count": 0, "score": 0.0 }
 
 
# ─────────────────────────────────────────────────────────────
# SCORE ENGINE
# ─────────────────────────────────────────────────────────────
 
def compute_confidence(wiki_score: float, news_score: float) -> tuple:
    """
    Aggregates Wikipedia and Google News scores
    into one final confidence score (0–100%).
 
    Wikipedia has slightly more weight (60%) than News (40%)
    because it is more stable and encyclopedic.
 
    Returns (score_percent, verdict)
    """
    if wiki_score == 0.0 and news_score == 0.0:
        return 0, "UNVERIFIABLE"
 
    # Weighted average
    if wiki_score > 0 and news_score > 0:
        combined = (wiki_score * 0.6) + (news_score * 0.4)
    elif wiki_score > 0:
        combined = wiki_score * 0.7     # only wiki found
    else:
        combined = news_score * 0.7     # only news found
 
    score_percent = round(combined * 100)
 
    if score_percent >= 70:
        verdict = "HIGH — Likely True ✓"
    elif score_percent >= 45:
        verdict = "MEDIUM — Partially Verified ⚠"
    else:
        verdict = "LOW — Likely False or Unverifiable ✗"
 
    return score_percent, verdict
 
 
# ─────────────────────────────────────────────────────────────
# DISPLAY RESULTS
# ─────────────────────────────────────────────────────────────
 
def display_results(claim: str, wiki: dict, news: dict, score: int, verdict: str):
    """Prints the full fact-check report for one claim."""
 
    print("\n")
    print("=" * 60)
    print("  FACT-CHECK REPORT — Sentinelle Numérique · Groupe 4")
    print("=" * 60)
    print(f"\n  Claim : \"{claim}\"")
    print(f"\n  ── Wikipedia ──────────────────────────────────────")
    if wiki["found"]:
        print(f"  Found   : {wiki['title']}")
        print(f"  Summary : {wiki['summary'][:250]}...")
        print(f"  Source  : {wiki['url']}")
        print(f"  Score   : {round(wiki['score'] * 100)}%")
    else:
        print("  No Wikipedia result found.")
 
    print(f"\n  ── Google News ────────────────────────────────────")
    if news["found"]:
        print(f"  Articles found : {news['count']}")
        for i, art in enumerate(news["articles"][:3], 1):
            print(f"  [{i}] {art['title']} — {art['source']}")
            print(f"       {art['url']}")
        print(f"  Score : {round(news['score'] * 100)}%")
    else:
        print("  No Google News results found.")
 
    print(f"\n  ── Final Result ───────────────────────────────────")
    print(f"  Confidence Score : {score}%")
    print(f"  Verdict          : {verdict}")
    print("=" * 60)
 
 
# ─────────────────────────────────────────────────────────────
# MAIN — USER INPUT LOOP
# ─────────────────────────────────────────────────────────────
 
def main():
    print("\n" + "=" * 60)
    print("  Sentinelle Numérique — Fact-Checker Automatisé")
    print("  Groupe 4 · SUP'PTIC · ITT3-IR · 2025-2026")
    print("=" * 60)
    print("  Type a claim or keyword to fact-check.")
    print("  Type 'quit' to exit.\n")
 
    while True:
        # ── Get user input ──────────────────────────────────
        claim = input("  Enter claim or keyword: ").strip()
 
        if claim.lower() in ("quit", "exit", "q"):
            print("\n  Goodbye!\n")
            break
 
        if len(claim) < 3:
            print("  ⚠ Please enter at least 3 characters.\n")
            continue
 
        print(f"\n  Fact-checking: \"{claim}\"")
        print("  Please wait...\n")
 
        # ── Search Wikipedia ────────────────────────────────
        wiki_result = search_wikipedia(claim)
        time.sleep(0.5)   # small pause to be polite to APIs
 
        # ── Search Google News ──────────────────────────────
        news_result = search_google_news(claim)
        time.sleep(0.5)
 
        # ── Compute confidence score ────────────────────────
        score, verdict = compute_confidence(
            wiki_result["score"],
            news_result["score"]
        )
        
        # ── Display full report ─────────────────────────────
        display_results(claim, wiki_result, news_result, score, verdict)
 
        # ── Ask if user wants to check another ─────────────
        print("\n  Check another claim? (press Enter to continue or type 'quit')")
 
 
if __name__ == "__main__":
    main()