"""
Contribution Analyzer: Processes raw GitHub data into per-repository statistics.
"""

from typing import List, Dict, Any

class ContributionAnalyzer:
    def analyze(self, user_contributions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregates and normalizes per-repo stats.
        """
        analyzed = []
        for repo in user_contributions:
            analyzed.append({
                "repo": repo["repo"],
                "commits": repo.get("commits", 0),
                "pull_requests": repo.get("pull_requests", 0),
                "lines_added": repo.get("lines_added", 0),
                "lines_removed": repo.get("lines_removed", 0),
                "files_modified": repo.get("files_modified", 0),
                "total_commits": repo.get("total_commits", 0),
                "total_prs": repo.get("total_prs", 0),
            })
        return analyzed
