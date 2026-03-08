"""
GitHub Data Fetcher: Fetches user contribution data from GitHub REST API.
"""


import asyncio
from typing import Dict, Any, List
from utils import github_api_get, github_graphql_query

class GitHubFetcher:
    def __init__(self, github_token: str = None):
        self.github_token = github_token

    async def fetch_contributed_repos_graphql(self, username: str):
        """
        Uses GitHub GraphQL API to fetch repositories the user has contributed to (not just owned).
        """
        query = '''
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              commitContributionsByRepository(maxRepositories: 100) {
                repository {
                  nameWithOwner
                  owner { login }
                  isFork
                  isPrivate
                }
                contributions {
                  totalCount
                }
              }
              pullRequestContributionsByRepository(maxRepositories: 100) {
                repository {
                  nameWithOwner
                  owner { login }
                  isFork
                  isPrivate
                }
                contributions {
                  totalCount
                }
              }
            }
          }
        }
        '''
        variables = {"login": username}
        data = await github_graphql_query(query, variables, self.github_token)
        print(f"[DEBUG] GraphQL data: {data}")
        return data

    async def fetch_user_contributions(self, username: str) -> List[Dict[str, Any]]:
        """
        Fetches repositories, commits, PRs, lines added/removed, files modified for the user.
        Returns a list of dicts per repository, only for repos NOT owned by the user.
        """
        print(f"[DEBUG] fetch_user_contributions called for {username}")
        # 1. Get user public events (pushes, PRs, etc.)
        events = await github_api_get(f"/users/{username}/events", self.github_token)
        print(f"[DEBUG] events fetched: {len(events)}")
        repo_stats = {}
        for event in events:
            repo_name = event["repo"]["name"]
            event_type = event["type"]
            # Fetch repo details to check owner (cache per repo)
            if repo_name not in repo_stats:
                repo_info = await github_api_get(f"/repos/{repo_name}", self.github_token)
                owner_login = repo_info["owner"]["login"].lower()
                if owner_login == username.lower():
                    print(f"[DEBUG] Skipping {repo_name} (owned by user) [{event_type}]")
                    continue  # skip repos owned by the user
                print(f"[DEBUG] Including {repo_name} (owner: {owner_login}) [{event_type}]")
                repo_stats[repo_name] = {
                    "commits": 0,
                    "pull_requests": 0,
                    "lines_added": 0,
                    "lines_removed": 0,
                    "files_modified": set(),
                }
            else:
                print(f"[DEBUG] Already tracking {repo_name} [{event_type}]")
            if event_type == "PushEvent":
                repo_stats[repo_name]["commits"] += len(event["payload"].get("commits", []))
            if event_type == "PullRequestEvent":
                repo_stats[repo_name]["pull_requests"] += 1
        # Convert sets to counts
        for repo in repo_stats:
            repo_stats[repo]["files_modified"] = len(repo_stats[repo]["files_modified"])
        print(f"[DEBUG] repo_stats for {username}: {repo_stats}")
        # Return as list
        return [dict(repo=repo, **stats) for repo, stats in repo_stats.items()]
