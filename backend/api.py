"""
FastAPI app: Exposes API endpoint for SVG card generation.
"""

from fastapi import FastAPI, Query, Response
from github_fetcher import GitHubFetcher
from contribution_analyzer import ContributionAnalyzer
from scoring_engine import ScoringEngine
from svg_card_generator import SVGCardGenerator
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()
print(f"[DEBUG] GITHUB_TOKEN on startup: {os.getenv('GITHUB_TOKEN')}")

app = FastAPI()

@app.get("/api/card")
async def get_gitimpact_card(username: str = Query(...)):
    github_token = os.getenv("GITHUB_TOKEN")
    print(f"[DEBUG] GITHUB_TOKEN: {github_token}")
    try:
        fetcher = GitHubFetcher(github_token=github_token)
        # Use GraphQL to fetch contributed repos
        gql_data = await fetcher.fetch_contributed_repos_graphql(username)
        # Parse GraphQL response
        user = gql_data.get("data", {}).get("user", {})
        contribs = user.get("contributionsCollection", {})
        repo_stats = {}
        # Commits
        import asyncio
        from utils import github_api_get

        import httpx
        async def get_total_commits(repo_name, token):
            # Use the /repos/{owner}/{repo}/commits?per_page=1 API and parse Link header for last page
            url = f"https://api.github.com/repos/{repo_name}/commits"
            headers = {"Accept": "application/vnd.github+json"}
            if token:
                headers["Authorization"] = f"token {token}"
            params = {"per_page": 1}
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code != 200:
                    print(f"[ERROR] Could not fetch commits for {repo_name}: {resp.text}")
                    return 0
                if "Link" in resp.headers:
                    # Parse last page number from Link header
                    link = resp.headers["Link"]
                    import re
                    m = re.search(r'&page=(\d+)>; rel="last"', link)
                    if m:
                        return int(m.group(1))
                # If no Link header, only one page
                return len(resp.json())

        async def get_total_prs(repo_name, token):
            url = f"https://api.github.com/repos/{repo_name}/pulls"
            headers = {"Accept": "application/vnd.github+json"}
            if token:
                headers["Authorization"] = f"token {token}"
            params = {"state": "all", "per_page": 1}
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code != 200:
                    print(f"[ERROR] Could not fetch PRs for {repo_name}: {resp.text}")
                    return 0
                if "Link" in resp.headers:
                    link = resp.headers["Link"]
                    import re
                    m = re.search(r'&page=(\d+)>; rel="last"', link)
                    if m:
                        return int(m.group(1))
                return len(resp.json())

        # Prepare to fetch total_commits and total_prs for each repo (not doubled)
        commit_tasks = []
        pr_tasks = []
        repo_names = []
        for entry in contribs.get("commitContributionsByRepository", []):
            repo = entry["repository"]
            repo_name = repo["nameWithOwner"]
            owner = repo["owner"]["login"]
            is_fork = repo.get("isFork", False)
            if owner.lower() == username.lower() or is_fork:
                continue  # skip owned or forked repos
            if repo_name not in repo_stats:
                repo_stats[repo_name] = {"repo": repo_name, "commits": 0, "pull_requests": 0, "lines_added": 0, "lines_removed": 0, "files_modified": 0, "total_commits": 0, "total_prs": 0}
                repo_names.append(repo_name)
            repo_stats[repo_name]["commits"] += entry["contributions"]["totalCount"]
        for entry in contribs.get("pullRequestContributionsByRepository", []):
            repo = entry["repository"]
            repo_name = repo["nameWithOwner"]
            owner = repo["owner"]["login"]
            is_fork = repo.get("isFork", False)
            if owner.lower() == username.lower() or is_fork:
                continue  # skip owned or forked repos
            if repo_name not in repo_stats:
                repo_stats[repo_name] = {"repo": repo_name, "commits": 0, "pull_requests": 0, "lines_added": 0, "lines_removed": 0, "files_modified": 0, "total_commits": 0, "total_prs": 0}
                repo_names.append(repo_name)
            repo_stats[repo_name]["pull_requests"] += entry["contributions"]["totalCount"]

        # Now, for each repo, fetch total_commits and total_prs (one call each)
        for repo_name in repo_names:
            commit_tasks.append(get_total_commits(repo_name, github_token))
            pr_tasks.append(get_total_prs(repo_name, github_token))
        total_commits_list = await asyncio.gather(*commit_tasks)
        total_prs_list = await asyncio.gather(*pr_tasks)
        for idx, repo_name in enumerate(repo_names):
            repo_stats[repo_name]["total_commits"] = total_commits_list[idx] if idx < len(total_commits_list) else 0
            repo_stats[repo_name]["total_prs"] = total_prs_list[idx] if idx < len(total_prs_list) else 0
        repo_stats_list = list(repo_stats.values())
        print(f"[DEBUG] repo_stats_list: {repo_stats_list}")
        analyzer = ContributionAnalyzer()
        analyzed_stats = analyzer.analyze(repo_stats_list)
        scorer = ScoringEngine()
        scored_stats = scorer.compute_score(analyzed_stats)
        generator = SVGCardGenerator()
        svg = generator.generate(username, scored_stats)
        return Response(content=svg, media_type="image/svg+xml")
    except Exception as e:
        print(f"[ERROR] {e}")
        return Response(content=f"Internal Server Error: {e}", media_type="text/plain", status_code=500)
