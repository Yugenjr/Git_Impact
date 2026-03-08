"""
Impact Score Engine: Computes normalized impact scores and contributor roles.
"""

from typing import List, Dict, Any

class ScoringEngine:
    def compute_score(self, stats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Computes impact score and assigns contributor role per repo.
        """
        scored = []
        max_score = 0
        # First, compute raw scores
        for repo in stats:
            score = (
                repo["commits"] * 1
                + repo["pull_requests"] * 8
                + repo["files_modified"] * 2
                + repo["lines_added"] / 200.0
            )
            repo["raw_score"] = score
            if score > max_score:
                max_score = score
        # Normalize and assign roles
        for repo in stats:
            norm_score = 0
            if max_score > 0:
                norm_score = min(100, int((repo["raw_score"] / max_score) * 100))
            repo["impact_score"] = norm_score
            if norm_score >= 80:
                role = "Core Contributor"
            elif norm_score >= 50:
                role = "Major Contributor"
            elif norm_score >= 20:
                role = "Feature Contributor"
            else:
                role = "Minor Contributor"
            repo["role"] = role
            scored.append(repo)
        return scored
