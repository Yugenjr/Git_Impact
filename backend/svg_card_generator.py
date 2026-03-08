"""
SVG Card Generator: Renders a compact dashboard SVG for embedding in README.
"""


import svgwrite
from typing import List, Dict, Any

class SVGCardGenerator:
    def generate(self, username: str, repo_stats: List[Dict[str, Any]]) -> str:
        """
        Generates a modern SVG dashboard card for the user, GitHub analytics style.
        """
        # Show top 5 repos where user is NOT the owner, sorted by commit percentage
        # Only include repos where owner is an individual (not org) and not the user
        def is_valid_repo(repo):
            owner = repo["repo"].split("/")[0].lower()
            # Exclude user's own repos
            if owner == username.lower():
                return False
            # Exclude known orgs (add more as needed)
            known_orgs = {"sece-24-28", "sece", "org", "organization"}
            if owner in known_orgs:
                return False
            return True

        filtered_repos = [r for r in repo_stats if is_valid_repo(r) and r.get("total_commits", 0) > 0]
        for r in filtered_repos:
            r["commit_percent"] = (r["commits"] / r["total_commits"]) * 100 if r["total_commits"] else 0
        top_repos = sorted(filtered_repos, key=lambda r: r["commit_percent"], reverse=True)[:5]

        width = 600
        row_height = 54
        height = 60 + row_height * len(top_repos) + 16
        bar_width = 340
        code_font = "Fira Mono, JetBrains Mono, Consolas, Menlo, monospace"
        dwg = svgwrite.Drawing(size=(f"{width}px", f"{height}px"), profile='tiny')

        # Gradient and shadow defs
        bg_gradient = dwg.linearGradient(id="bg-gradient", x1="0%", y1="0%", x2="100%", y2="100%")
        bg_gradient.add_stop_color(0, "#161b22")
        bg_gradient.add_stop_color(1, "#1f2937")
        dwg.defs.add(bg_gradient)
        bar_gradient = dwg.linearGradient(id="bar-gradient", x1="0%", y1="0%", x2="100%", y2="0%")
        bar_gradient.add_stop_color(0, "#3b82f6")
        bar_gradient.add_stop_color(1, "#22d3ee")
        dwg.defs.add(bar_gradient)

        # Background card
        dwg.add(dwg.rect(insert=(0, 0), size=(width, height), rx=12, fill="url(#bg-gradient)"))

        # Header
        dwg.add(dwg.text("<GitImpact />", insert=(24, 36), fill="#c9d1d9",
                 font_size="20px", font_weight="600", font_family=code_font))
        # User icon
        dwg.add(dwg.circle(center=(width-120, 28), r=10, fill="#22272e", stroke="#30363d", stroke_width=1))
        dwg.add(dwg.text("👤", insert=(width-126, 34), font_size="13px"))
        # Username
        dwg.add(dwg.text(f"@{username}", insert=(width-104, 34), fill="#8ab4f8",
                 font_size="14px", font_weight="500", font_family=code_font))
        # Divider
        dwg.add(dwg.line(start=(16, 44), end=(width-16, 44), stroke="#23272e", stroke_width=1))

        # Repo card rows
        badge_colors = {
            "Core Contributor": "#34d399",
            "Major Contributor": "#3b82f6",
            "Feature Contributor": "#facc15",
            "Minor Contributor": "#64748b"
        }
        for i, repo in enumerate(top_repos):
            y_offset = 52 + i * row_height
            # Repo card container (minimal, code style)
            dwg.add(dwg.rect(insert=(16, y_offset), size=(width-32, row_height-8), rx=7, fill="#161b22"))
            # Repo icon
            dwg.add(dwg.text("📦", insert=(32, y_offset+22), font_size="14px"))
            # Repo name (prominent, code font)
            dwg.add(dwg.text(repo["repo"].split("/")[-1], insert=(52, y_offset+22), fill="#fff",
                             font_size="16px", font_weight="700", font_family=code_font))
            # Contribution percentage (highlighted, code font)
            percent_commits = repo["commit_percent"]
            dwg.add(dwg.text(f"{percent_commits:.1f}%", insert=(width-160, y_offset+22), fill="#22d3ee",
                             font_size="18px", font_weight="700", font_family=code_font))
            dwg.add(dwg.text("of all commits", insert=(width-100, y_offset+22), fill="#8ab4f8",
                             font_size="11px", font_family=code_font))
            # Progress bar background
            dwg.add(dwg.rect(insert=(52, y_offset+30), size=(bar_width, 10), rx=5, fill="#23272e"))
            # Progress bar fill
            fill_width = int(bar_width * percent_commits / 100)
            dwg.add(dwg.rect(insert=(52, y_offset+30), size=(fill_width, 10), rx=5, fill="url(#bar-gradient)"))
            # Contributor role badge (smaller, code style)
            badge_color = badge_colors.get(repo["role"], "#64748b")
            badge_x = width-120
            badge_y = y_offset+32
            badge_w = 110
            badge_h = 16
            dwg.add(dwg.rect(insert=(badge_x, badge_y), size=(badge_w, badge_h), rx=8, fill=badge_color, opacity=0.95))
            # Badge icon and text centered
            badge_icon = "⭐" if repo["role"] == "Core Contributor" else "🔷" if repo["role"] == "Major Contributor" else "✨" if repo["role"] == " Feature Contributor" else "👤"
            badge_label = repo["role"]
            # Center text in badge
            badge_text = f"{badge_icon} {badge_label}"
            # Estimate text width (monospace, 6px per char for slightly larger font)
            text_len = len(badge_text)
            text_x = badge_x + (badge_w // 2) - (text_len * 6 // 2) - 10
            text_y = badge_y + badge_h // 2 + 3
            dwg.add(dwg.text(badge_text, insert=(text_x, text_y), fill="#fff",
                             font_size="9px", font_weight="600", font_family=code_font))

        return dwg.tostring()
        return dwg.tostring()
