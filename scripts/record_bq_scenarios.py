"""Record the four BigQuery Data Agent showcase scenarios, on video.

One conversation per scenario in the console's Chat-with-your-data surface,
driving the prompt arcs from reports/bq_data_agent_showcase_prd.md. Each
video ends with the guided review scroll. The transcript of every
conversation is saved beside the video for the ground-truth cross-check —
a number spoken in a sales video must match SQL, or the video is re-cut.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILE = ROOT / "data" / "uat" / ".profile"
OUT = ROOT / "data" / "uat" / "bq_scenarios"
PROJECT = "genial-union-475913-i7"
BQ_URL = ("https://console.cloud.google.com/bigquery/agents_hub;"
          f"agentsPath=%2Fbq%2Fagents-catalog?project={PROJECT}")
AGENT_CARD = "Mining Operations Insight Agent"

SCENARIOS = {
  "S1-grade-reconciliation": [
    "What is our planned head grade by rock type, and how many blocks does the resource model hold?",
    "What head grades did the assay lab actually measure, by logged rock type?",
    "Reconcile planned against assayed head grade by rock type. Where is the resource model most wrong, in percentage points?",
    "For that rock type: how many blocks are affected, and what is the estimated contained metal at risk if the assayed grade is the truth? Show the calculation.",
    "Three sentences for the mine GM: what is misestimated, by how much, and the first corrective action.",
  ],
  "S2-anomaly-hunt": [
    "What does our plant telemetry cover, and how many readings per instrument metric?",
    "Trend the busiest metric as a daily average. Any drift a reliability engineer should worry about?",
    "Hunt for anomalous readings across the plant: anything beyond three standard deviations for its metric. How many, and which assets are the worst offenders?",
    "For the worst offender: show its anomalies in time order. Developing fault or bad sensor? Argue from the data.",
    "Write tomorrow morning's shift-handover paragraph for the plant supervisor.",
  ],
  "S3-parts-failure-graph": [
    "Which spare parts are at stock-out risk right now, and what are their supplier lead times?",
    "Which maintenance work orders historically consumed those at-risk parts?",
    "Which assets did that maintenance repair, and what has each asset cost us in repairs through those parts?",
    "Rank the assets most exposed if we stock out this week — weigh the number of at-risk parts, the repair cost history, and the longest supplier lead time. Explain the ranking.",
    "We can expedite three purchase orders. Which parts, and why those three?",
  ],
  "S4-pit-to-port-cascade": [
    "What is the crusher's average feed rate, and how often is it running in bypass?",
    "A six-hour crusher outage at that feed rate: how many tonnes of production do we lose?",
    "How many hours of reclaim buffer does each stockpile hold before running empty, and which run out first?",
    "Trace the exposure downstream: which rail consists load from the at-risk stockpiles, and which vessels do those consists feed?",
    "For those vessels: demurrage days on record, tonnes loaded, and the demurrage exposure if loading slips a day — state your day-rate assumption as a range.",
    "Five lines for the logistics manager: the chain from crusher to vessel, the first bottleneck, and the single action that buys the most time.",
  ],
}


REVIEW_JS = r"""async () => {
  let sc = null;
  const walk = (root) => {
    for (const el of root.querySelectorAll('*')) {
      if (el.scrollHeight > el.clientHeight + 200 &&
          /message|chat|conversation|scroll|content/i.test((el.className||'').toString()))
        sc = el;
      if (el.shadowRoot) walk(el.shadowRoot);
    }
  };
  walk(document);
  if (!sc) sc = document.scrollingElement;
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  sc.scrollTo({top: 0, behavior: 'smooth'}); await sleep(2500);
  const bottom = sc.scrollHeight - sc.clientHeight;
  for (let y = 0; y <= bottom; y += 110) { sc.scrollTo({top: y, behavior: 'smooth'}); await sleep(600); }
  await sleep(3500); return true;
}"""


def frame_with(pg, text):
    """The console renders this product inside iframes: text visible in a
    screenshot is invisible to main-frame locators. Search every frame."""
    for f in pg.frames:
        try:
            if f.get_by_text(text).count():
                return f
        except Exception:
            continue
    return None


def find_input(pg):
    for f in pg.frames:
        try:
            loc = f.locator("textarea")
            for i in range(loc.count()):
                el = loc.nth(i)
                ph = (el.get_attribute("placeholder") or el.get_attribute("aria-label") or "")
                if el.is_visible() and ("ask" in ph.lower() or "question" in ph.lower()):
                    return f, el
        except Exception:
            continue
    return None, None


def wait_reply(frame, prev_len, timeout_s=300):
    """A reply is done when the chat frame has grown and held still for 15s."""
    deadline, stable, last = time.time() + timeout_s, 0, prev_len
    while time.time() < deadline:
        time.sleep(5)
        try:
            n = frame.evaluate("() => document.body.innerText.length")
        except Exception:
            continue
        if n > prev_len + 40 and n == last:
            stable += 1
            if stable >= 3:
                return n
        else:
            stable = 0
        last = n
    return last


def record(name, prompts):
    OUT.mkdir(parents=True, exist_ok=True)
    vdir = OUT / name
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE), headless=True,
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(vdir),
            record_video_size={"width": 1440, "height": 900})
        pg = ctx.new_page()
        pg.goto(BQ_URL, timeout=120000, wait_until="domcontentloaded")
        pg.wait_for_timeout(20000)
        card_frame = None
        for attempt in range(10):
            card_frame = frame_with(pg, AGENT_CARD)
            if card_frame:
                break
            print(f"  [{name}] card not rendered (attempt {attempt+1})", flush=True)
            if attempt % 2 == 1:      # a stuck fetch needs a fresh page, not patience
                pg.reload(timeout=120000, wait_until="domcontentloaded")
                pg.wait_for_timeout(20000)
            else:
                pg.wait_for_timeout(15000)
        if not card_frame:
            pg.screenshot(path=str(vdir / "no_agent_card.png"))
            raise RuntimeError(f"{name}: agent card never rendered in any frame")
        card_frame.get_by_text(AGENT_CARD).first.click()
        pg.wait_for_timeout(10000)
        pg.wait_for_timeout(8000)   # the card click navigates; let frames settle

        def send(q):
            """Re-find the input at send time: frame navigations detach stale
            handles, and fill() carries its own actionability wait."""
            last_err = None
            for _ in range(4):
                f, b = find_input(pg)
                if b is None:
                    pg.wait_for_timeout(5000)
                    continue
                try:
                    b.fill(q, timeout=20000)
                    pg.wait_for_timeout(400)
                    b.press("Enter")
                    return f
                except Exception as e:
                    last_err = e
                    pg.wait_for_timeout(5000)
            pg.screenshot(path=str(vdir / "send_failed.png"))
            raise RuntimeError(f"{name}: could not send prompt ({type(last_err).__name__ if last_err else 'no input found'})")

        chat_frame = None
        for i, q in enumerate(prompts, 1):
            probe_frame = chat_frame or pg.main_frame
            try:
                n0 = probe_frame.evaluate("() => document.body.innerText.length")
            except Exception:
                n0 = 0
            chat_frame = send(q)
            print(f"  [{name}] prompt {i}/{len(prompts)} sent", flush=True)
            wait_reply(chat_frame, n0)
        transcript = chat_frame.evaluate("() => document.body.innerText")
        (vdir / "transcript.txt").write_text(transcript)
        try:
            chat_frame.evaluate(REVIEW_JS)
        except Exception as e:
            print(f"  [{name}] review scroll failed: {type(e).__name__}", flush=True)
        ctx.close()
    print(f"  [{name}] DONE — video + transcript in {vdir}", flush=True)


if __name__ == "__main__":
    names = sys.argv[1:] or list(SCENARIOS)
    failed = []
    for n in names:
        for attempt in (1, 2):
            try:
                record(n, SCENARIOS[n])
                break
            except Exception as e:
                print(f"  [{n}] attempt {attempt} failed: {e}", flush=True)
                time.sleep(30)
        else:
            failed.append(n)
    if failed:
        print(f"SCENARIOS_FAILED: {','.join(failed)}", flush=True)
        sys.exit(1)
    print("ALL_SCENARIOS_RECORDED", flush=True)
