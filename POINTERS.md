# Where everything lives

This repo (private: `irvivek-debug/mining-agents-internal`, branch `main`)
is the authoritative codebase. Heavy and live assets live outside git:

| Asset | Location |
|---|---|
| Agent sales recordings (100) | `gs://mining-agents-showcase-genial-union-475913/videos/` |
| BQ Data Agent scenario recordings (v2) | same bucket, `videos/bq/` |
| Internal showcase (org + google.com, IAP) | https://mining-agents-showcase-297934069315.us-central1.run.app |
| Public scrubbed showcase (GitHub Pages) | https://irvivek-debug.github.io/mining-agents/ (repo `mining-agents`, branch `public-showcase`) |
| Reusable kit (method + team + machinery) | repo `agentic-showcase-kit` |
| Agent estate (100 ADK agents) | Vertex AI Agent Engine + Gemini Enterprise, project `genial-union-475913-i7` |
| BQ Data Agent | `mining-insight-showcase` (Conversational Analytics, location `global`) |

Videos are deliberately NOT in git: GitHub rejects the payload and they are
regenerable (`scripts/uat_run.py`, `scripts/record_bq_scenarios.py`).
Local branches named `internal-showcase*` are dead ends from an aborted
video-push experiment — ignore them; do not merge them.

Evidence trail: `data/uat/ledger*.jsonl`, `data/grounding/results.jsonl`,
`reports/`.
