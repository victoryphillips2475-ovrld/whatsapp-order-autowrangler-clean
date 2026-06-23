# Deep Web Search Architecture — OVERLORD Empire Standard

## When to Use This Pattern
- Before writing code that uses an unfamiliar API or library
- When verifying current package versions before pinning them
- When researching a technical approach before implementing
- When debugging requires understanding an error pattern

## The 4-Phase Pipeline

### PHASE 1 — Intent Parsing & Query Generation
Never pass raw questions to a search engine. Generate 3-5 parallel sub-queries.

Example:
  Task: "Find the current stable version of httpx"
  Queries:
    - "httpx python package latest stable version 2025"
    - "httpx pypi release history"
    - "site:pypi.org httpx"

### PHASE 2 — Retrieval (Wide Net)
Use Tavily for semantic search (primary):
```python
import httpx, os

async def tavily_search(query: str, max_results: int = 5) -> list[dict]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": os.environ["TAVILY_API_KEY"],
                "query": query,
                "max_results": max_results,
                "include_raw_content": False,
            }
        )
        response.raise_for_status()
        return response.json().get("results", [])
```

Use Firecrawl for full page extraction (when URL is known):
```python
async def firecrawl_fetch(url: str) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {os.environ['FIRECRAWL_API_KEY']}"},
            json={"url": url, "formats": ["markdown"]}
        )
        response.raise_for_status()
        return response.json().get("data", {}).get("markdown", "")
```

SearXNG as fallback:
```python
async def searxng_search(query: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            "http://localhost:8888/search",
            params={"q": query, "format": "json", "categories": "general"}
        )
        return response.json().get("results", [])
```

### PHASE 3 — Extraction & Ranking
- From search results, collect the top 5-10 URLs
- Fetch the most promising 2-3 with Firecrawl
- Extract only the relevant sections (not entire pages)
- Prioritize: official docs > package registry > trusted blogs > forums

### PHASE 4 — Grounding & Use
- State the source for any fact you act on
- For package versions: verify on pypi.org, npmjs.com, or crates.io directly
- For API patterns: verify against official documentation URL
- Never act on a single source for version-critical information

## Quick Pattern for Package Version Check
```python
async def get_latest_pypi_version(package: str) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"https://pypi.org/pypi/{package}/json")
        response.raise_for_status()
        return response.json()["info"]["version"]
```

## RULES
1. Never send raw user prompts to search — decompose first
2. Use Tavily for conceptual queries, Firecrawl for known URLs
3. Cross-reference at least 2 sources for version pinning
4. SearXNG (localhost:8888) is fallback only — not primary
5. Include date in queries for time-sensitive information