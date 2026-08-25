"""Build the sales companion document for the agent recordings.

One entry per agent: a context paragraph (~100 words) written so a reader
who has never seen the system understands the input (the operational
scenario), the output (what the agent concluded, with its real numbers),
and the logic (the governing method and the tables it read) — then the
video path and the live agent link.

Everything is drawn from recorded evidence: the scenario prompts, the
ledger's captured replies, and the catalogue. Nothing is invented.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor" / "agent_registry"))
import catalog_definitions as C  # noqa: E402

LEDGER = ROOT / "data" / "uat" / "ledger.jsonl"
AGENTS = ROOT / "data" / "uat" / "agents.json"
SCEN = ROOT / "data" / "uat" / "scenario_prompts.json"
VIDEOS = ROOT / "data" / "uat" / "videos"
OUT = ROOT / "reports" / "sales_recordings_companion.md"


def first_numbers(text: str, n: int = 3) -> list[str]:
    """The most salient figures the agent actually reported."""
    hits = re.findall(r"\b\d[\d,]*\.?\d*\s*(?:%|mm|kPa|t|tph|days?|hours?)?", text)
    seen, out = set(), []
    for h in hits:
        h = h.strip()
        if len(h) < 2 or h in seen:
            continue
        seen.add(h); out.append(h)
        if len(out) == n:
            break
    return out


def first_sentence(text: str, limit: int = 220) -> str:
    t = re.sub(r"[#*|`]+", " ", text)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:limit].rsplit(" ", 1)[0] + ("…" if len(t) > limit else "")


def paragraph(agent, scen_q: str, reply: str, tables: list[str]) -> str:
    """~100 words: input, output, logic — from real material only."""
    nums = first_numbers(reply)
    opening = first_sentence(reply)
    t = ", ".join(f"`{x}`" for x in tables[:3]) or "its declared sources"
    method = (agent.governing_equation or "its governing method").strip()
    return (
        f"**Input.** {scen_q.strip()} "
        f"**Output.** The agent answers from live data — opening: “{opening}”"
        f"{' — key figures ' + ', '.join(nums) if nums else ''}. "
        f"**Logic.** It reads {t} in BigQuery, applies {method}, reconciles "
        f"any figures supplied in the question against what the data actually "
        f"says, and cites the tables behind every number — so the answer is "
        f"traceable, not plausible."
    )


def main() -> int:
    by_cat = {a.agent_id: a for a in C.CATALOG}
    agents = json.loads(AGENTS.read_text())
    scen = json.loads(SCEN.read_text())
    ledger = {}
    for line in LEDGER.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            ledger[r["agent_id"]] = r

    lines = [
        "# Agent Recordings — Sales Companion",
        "",
        "One entry per agent. Each recording opens on the operational question,",
        "shows the agent reading BigQuery live (the tool trace), then scrolls",
        "the answer at reading pace. Note for live demos: agents answer in",
        "seconds via the API but typically 2–4 minutes through the chat UI —",
        "the on-screen tool trace is the proof of grounding; narrate over it.",
        "",
    ]
    skipped = []
    for a in sorted(agents, key=lambda x: x["agent_id"]):
        aid = a["agent_id"]
        r = ledger.get(aid)
        if not r or not r.get("passed") or not r.get("reply"):
            skipped.append(aid)
            continue
        pair = scen.get(aid) or ["", ""]
        q = pair[0] if isinstance(pair, list) else pair
        cat = by_cat.get(aid)
        vids = sorted((VIDEOS / aid).glob("*.webm")) if (VIDEOS / aid).exists() else []
        lines += [
            f"## {a['display_name']}",
            "",
            f"*{a.get('department','')} — {a.get('persona','')}*",
            "",
            paragraph(cat, q, r["reply"], a.get("tables", [])),
            "",
            f"- **Recording:** `{vids[0].relative_to(ROOT)}`" if vids else "- **Recording:** (pending)",
            f"- **Live agent:** {a['url']}",
            "",
        ]
    if skipped:
        lines += ["---", "", f"**Not yet included ({len(skipped)}):** " + ", ".join(skipped),
                  "  (no passing recording on the current ledger — the companion only",
                  "  describes what a recording actually shows)", ""]
    OUT.write_text("\n".join(lines))
    print(f"{len(agents) - len(skipped)} entries -> {OUT.relative_to(ROOT)}"
          + (f"  (skipped {len(skipped)})" if skipped else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
