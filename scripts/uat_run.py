"""Drive each registered agent through the Gemini Enterprise UI and record it.

WHAT THIS TESTS THAT AN API CALL DOES NOT
Invoking an Agent Engine over REST proves the engine answers. It does not prove
the agent is reachable, selectable and usable in the product a person actually
opens. This drives the real UI -- navigating to each agent's own session URL,
typing into the real composer, waiting for the rendered reply -- so a pass means
a human could have done the same thing.

ASSERTIONS THAT CAN ACTUALLY FAIL
The vault's ledger certified 101 agents with asserted outputs like "Executes
domain physics calculations and provides grounded recommendations", which no
response could fail -- and it certified an estate where every engine was
404ing. So the checks here are the ones a wrong answer trips:

  answered        a reply arrived at all, and it is not an error surface
  in_character    it reaches for its own domain -- a term from its governing
                  equation, its department, or a table it declares
  no_fabrication  it does not claim an injection, compromise or breach without
                  evidence: the exact failure S07 shipped to a human on 20 Aug
  grounded_or_says_not
                  it either cites something, or states plainly that it cannot

A run records one .webm per agent. Video is why this owns its own browser
context: record_video_dir is fixed at context creation.

Usage:
    python scripts/uat_run.py --limit 3            # trial
    python scripts/uat_run.py --all
    python scripts/uat_run.py --agents S10-R-CRITIC,D26
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import time

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILE = ROOT / "data" / "uat" / ".profile"
AGENTS = ROOT / "data" / "uat" / "agents.json"
VIDEOS = ROOT / "data" / "uat" / "videos"
LEDGER = ROOT / "data" / "uat" / "ledger.jsonl"

# Words that only belong in a finding backed by evidence. S07 reported the
# dataset "compromised by an untrusted free-text injection" across three tables
# that hold no free text at all, and escalated it to a human.
# Scoped to a CLAIM ABOUT THE DATA, not the English verb. The first version
# matched `compromis\w+` anywhere and flagged "maximises cash flow without
# compromising discounted future pit value" as a fabricated security incident.
# What this is looking for is the S02/S07 failure -- asserting the dataset
# itself was attacked -- so the subject has to be data.
FABRICATION = re.compile(
    r"\b(prompt injection"
    r"|(?:data|dataset|table|record|source|input)s?\s+(?:\w+\s+){0,3}"
    r"(?:been\s+)?(?:compromis\w+|tamper\w+|poison\w+|injected)"
    r"|(?:compromis\w+|tamper\w+|poison\w+)\s+(?:data|dataset|table|record|source)s?"
    r")\b", re.I)
EVIDENCE = re.compile(r"\b(banner|UNTRUSTED DATA)\b", re.I)
# A grounded answer either points at something, or says it cannot.
# "Grounded" means the agent points at evidence. Checking for a `mining_data.`
# prefix missed every agent that names its table plainly -- pit_designs,
# reagent_inventory -- which is all of them, so the real test is whether the
# reply mentions a table the agent actually declares. That is checked in
# assess() against the agent's own catalogue entry rather than by regex.
CITES = re.compile(
    r"(mining_data\.|\bclauses?\b|\btables?\b|\bCTR-\d|\bAPQC\b|\bISO \d|"
    r"according to|based on the|\brecords?\b|\bcite|\bsources?\b|\blogs?\b)", re.I)
# Stating a limit is the honest alternative to citing, and these agents phrase
# it as "outside what I can evidence" -- which the first pattern, built around
# "cannot" and "unable to", did not match. Six agents were failed for being
# MORE careful than the check expected, which is the wrong way round.
CANNOT = re.compile(
    r"(cannot|can't|unable to|do not have access|no data|not available|insufficient|"
    r"would need|not instrumented|outside what i can|outside (?:my|the) "
    r"(?:scope|evidence)|unverified|not verifiable|require\w*\s+(?:from|validated))", re.I)


# Playwright's inner_text() does not descend into shadow roots, and this UI
# renders its entire transcript inside 400+ of them -- so locator("main")
# .inner_text() returns "" no matter how long the reply is. The first run
# recorded a 9.5MB video of a real conversation and logged an empty answer,
# then failed the agent for not answering. This walks the shadow tree.
# The assistant's answer renders into `.markdown-document`. Reading the whole
# page instead was the harness's second serious bug: the transcript echoes the
# prompt, so a full-page read captured the nav chrome plus my own question, and
# the in_character check then matched vocabulary out of the PROMPT rather than
# the answer. Two agents were scored as passing on text they never wrote, and
# one on text that was mine. Reading only the answer container removes the
# possibility.
REPLY_JS = r"""() => {
  const docs = [];
  const walk = (root) => {
    for (const el of root.querySelectorAll('.markdown-document')) {
      const t = (el.innerText || el.textContent || '').trim();
      if (t) docs.push(t);
    }
    for (const el of root.querySelectorAll('*')) if (el.shadowRoot) walk(el.shadowRoot);
  };
  walk(document);
  return docs;
}"""


def replies(page) -> list[str]:
    """Every rendered assistant answer, newest last.

    Deliberately unguarded: a reader that cannot read must raise, not return
    empty. An earlier version swallowed a JavaScript syntax error and scored
    working agents as silent, with video of them answering sitting beside the
    empty ledger entry.
    """
    return page.evaluate(REPLY_JS) or []


def prompt_for(a: dict) -> str:
    """A domain question this agent should be able to take a position on.

    Built from the agent's own catalogue fields rather than hand-written per
    agent, so all 96 get a question of the same shape and none is flattered by
    a prompt written to suit it.
    """
    eq = (a.get("equation") or "").strip()
    tables = ", ".join(a.get("tables") or []) or "your grounding data"
    return (
        f"You are {a['name']}, working for the {a['persona']} in {a['department']}. "
        f"In three or four sentences: what decision do you own, what does "
        f"{eq or 'your governing method'} let you determine, and what would you need "
        f"from {tables} before you would put a number in front of a human? "
        f"Be specific and say plainly if something is outside what you can evidence."
    )


def token_set(a: dict) -> set[str]:
    """Domain vocabulary this agent should plausibly use."""
    words = set()
    for src in [a.get("equation", ""), a.get("name", ""), a.get("department", ""),
                a.get("persona", "")] + (a.get("tables") or []):
        for w in re.findall(r"[A-Za-z][A-Za-z_]{3,}", src or ""):
            words.add(w.lower().strip("_"))
    return {w for w in words if w not in
            {"the", "and", "from", "with", "your", "this", "that", "logs", "data"}}


def assess(a: dict, reply: str, prompt: str = "") -> dict:
    r = (reply or "").strip()
    answered = len(r) > 80 and not r.lower().startswith(("error", "something went wrong"))
    vocab = token_set(a)
    hits = sorted({w for w in vocab if w in r.lower()})
    in_character = len(hits) >= 2
    fab = FABRICATION.search(r)
    no_fabrication = not fab or bool(EVIDENCE.search(r))
    # Its own declared tables count as citations, named plainly or prefixed.
    declared = [t for t in (a.get("tables") or []) if t and t.lower() in r.lower()]
    grounded = bool(declared or CITES.search(r) or CANNOT.search(r))
    # not_the_prompt is a regression guard, not a property of the agent.
    # Four times in a row this harness scored the echoed prompt as the reply
    # and reported PASS -- the in_character check cannot tell them apart,
    # because the prompt names the agent, its department, its equation and its
    # tables. If a reply ever looks like the question again, the run says so
    # instead of certifying it.
    not_the_prompt = bool(r) and normalise(r)[:80] != normalise(prompt)[:80]
    checks = {"answered": answered, "not_the_prompt": not_the_prompt,
              "in_character": in_character,
              "no_fabrication": no_fabrication, "grounded_or_says_not": grounded}
    return {"checks": checks, "passed": all(checks.values()),
            "vocab_hits": hits[:8], "tables_cited": declared,
            "fabrication_phrase": fab.group(0) if fab and not no_fabrication else None}


def normalise(t: str) -> str:
    return " ".join((t or "").split()).strip().lower()


def read_reply(page, baseline: int, prompt: str, timeout_s: int = 120) -> str:
    """Wait for the agent's answer, which is not simply the newest bubble.

    The composer renders the USER's prompt into a .markdown-document too, so
    the document count grows the instant Enter is pressed and the newest
    document is the question. An earlier version returned that -- it stabilised
    immediately, every agent "answered" in 8 seconds, and the in_character
    check then matched vocabulary out of my own prompt. Three agents were
    scored on text they had not written.

    So the prompt is excluded explicitly, and the wait is for a document that
    is not it.
    """
    want = normalise(prompt)
    deadline = time.time() + timeout_s
    stable, last = 0, ""
    while time.time() < deadline:
        docs = [d for d in replies(page) if normalise(d) != want]
        if len(docs) > baseline:
            current = docs[-1]
            if current and current == last:
                stable += 1
                if stable >= 3:
                    return current
            else:
                stable = 0
            last = current
        time.sleep(1)
    return last


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--agents", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--timeout", type=int, default=90)
    args = ap.parse_args()

    agents = json.loads(AGENTS.read_text())
    if args.agents:
        want = {x.strip() for x in args.agents.split(",") if x.strip()}
        agents = [a for a in agents if a["agent_id"] in want]
    elif args.limit:
        agents = agents[:args.limit]
    elif not args.all:
        raise SystemExit("pass --limit, --agents or --all")

    VIDEOS.mkdir(parents=True, exist_ok=True)
    done = {}
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                done[rec["agent_id"]] = rec
    todo = [a for a in agents if a["agent_id"] not in done]
    print(f"{len(agents)} selected | {len(done)} already recorded | {len(todo)} to run\n")

    passed = failed = 0
    with sync_playwright() as p:
        for i, a in enumerate(todo, 1):
            aid = a["agent_id"]
            vdir = VIDEOS / aid
            vdir.mkdir(parents=True, exist_ok=True)
            # One context per agent: that is what yields one video per agent.
            ctx = p.chromium.launch_persistent_context(
                str(PROFILE), headless=True,
                viewport={"width": 1440, "height": 900},
                record_video_dir=str(vdir),
                record_video_size={"width": 1440, "height": 900},
            )
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            started = time.time()
            reply, note = "", ""
            try:
                page.goto(a["url"], wait_until="domcontentloaded", timeout=60000)
                # The composer is a ProseMirror contenteditable living inside
                # shadow DOM, not an <input> or a role=textbox -- get_by_role
                # ("textbox") finds nothing and times out. Playwright's CSS
                # engine pierces shadow roots, so .ProseMirror addresses it
                # directly. fill() does not work on contenteditable either;
                # the text has to be typed after focusing.
                box = page.locator(".ProseMirror").first
                box.wait_for(state="visible", timeout=45000)
                q = prompt_for(a)
                baseline = len([d for d in replies(page) if normalise(d) != normalise(q)])
                box.click()
                page.keyboard.type(q, delay=1)
                page.wait_for_timeout(400)
                page.keyboard.press("Enter")
                reply = read_reply(page, baseline, q, args.timeout)
            except Exception as e:
                note = f"{type(e).__name__}: {str(e)[:160]}"
            latency = round(time.time() - started, 1)
            try:
                video_path = page.video.path() if page.video else None
            except Exception:
                video_path = None
            ctx.close()   # the video is only finalised on context close

            verdict = assess(a, reply, prompt_for(a))
            rec = {"agent_id": aid, "name": a["name"], "department": a["department"],
                   "persona": a["persona"], "pattern": a["pattern"],
                   "value_class": a["value_class"], "hitl": a["hitl"],
                   "equation": a["equation"], "tables": a["tables"],
                   "url": a["url"], "prompt": prompt_for(a), "reply": reply,
                   "latency_s": latency, "note": note,
                   "video": str(pathlib.Path(video_path).relative_to(ROOT)) if video_path else None,
                   **verdict}
            with LEDGER.open("a") as fh:
                fh.write(json.dumps(rec) + "\n")
            passed += rec["passed"]; failed += (not rec["passed"])
            flag = "PASS" if rec["passed"] else "FAIL"
            bad = [k for k, v in rec["checks"].items() if not v]
            print(f"[{i}/{len(todo)}] {flag} {aid:<17} {latency:>5}s  "
                  f"{'' if rec['passed'] else 'failed:' + ','.join(bad)}  {note}")

    print(f"\npassed {passed} | failed {failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
