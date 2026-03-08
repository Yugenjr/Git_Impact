# 🚀 GitImpact

**GitImpact** is a developer tool that analyzes your real GitHub contribution impact across all repositories you contributed to, and generates a compact SVG dashboard card for your README.

## Features
- Analyzes commits, PRs, lines added/removed, files modified
- Computes an impact score and contributor role per repository
- Ranks your top repositories by engineering impact
- Generates a clean, embeddable SVG dashboard card

## Example Usage

Embed your GitImpact dashboard in your README:

```markdown
![GitImpact](https://gitimpact-api.vercel.app/api/card?username=YOUR_GITHUB_USERNAME)
```

## Project Structure

- `backend/` — API, data fetcher, analyzer, scoring, SVG generator
- `frontend/` — Dashboard layout design (assets, mockups)

## Backend Tech
- Python
- FastAPI
- GitHub REST API
- SVG generation (svgwrite, etc.)

---

> See backend/ for implementation details.
