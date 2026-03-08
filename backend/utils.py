
import httpx
from typing import Dict, Any

GITHUB_API_URL = "https://api.github.com"
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

async def github_api_get(endpoint: str, token: str = None, params: Dict[str, Any] = None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GITHUB_API_URL}{endpoint}", headers=headers, params=params)
        response.raise_for_status()
        return response.json()

async def github_graphql_query(query: str, variables: Dict[str, Any] = None, token: str = None):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"bearer {token}"
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    async with httpx.AsyncClient() as client:
        response = await client.post(GITHUB_GRAPHQL_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
