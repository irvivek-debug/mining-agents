---
name: front-end
description: Use when building or verifying front-end screens for agent products — covers grounding UI in live data, harness calibration against real behaviour, shadow-DOM automation, and headless capture traps.
---

# Front End — patterns from the mining-agents engagement

## Screens bind to live data or they lie
Every figure a screen shows should be traceable to the warehouse or a
recorded agent reply. When demo data must be synthetic, it ships behind
passing generator tests and thresholds — never hand-tuned numbers.

## The UI you automate is not the DOM you think
Gemini Enterprise renders inside 400+ nested shadow roots:
- The composer is a ProseMirror contenteditable — `get_by_role("textbox")`
  finds nothing, `fill()` does nothing; use the `.ProseMirror` CSS
  selector (Playwright pierces shadow roots) and `keyboard.type`.
- Read answers only from the answer container (`.markdown-document` via a
  shadow-root walk), never full-page text — a full-page read once scored
  agents as passing on vocabulary from the question itself.
- Prefer `textContent` fallbacks: `innerText` requires layout and returns
  empty for hidden/unpainted nodes in headless runs.

## Type-and-verify, never type-and-hope
A composer can render before its editor wiring is live; typed text is
silently lost and Enter submits nothing. After typing, assert the
composer contains the prompt prefix; after Enter, assert it cleared;
retry otherwise.

## Calibrate gates to current behaviour, not remembered behaviour
An "answered" gate demanding >80 characters failed rebuilt agents whose
correct answer was 41 characters. When the system under test improves,
the harness is the thing most likely to be wrong — judge substance
(content present, matches source), not shape (length, verbosity).

## Deep links carry their full path
GE agent URLs need the `/home/cid/<cloud-identity>/r/agent/{id}/session/-`
form. The bare `/r/agent/...` 404s — and Google serves 404 (not a
redirect) for short links a session cannot access, so a "no redirect"
check does NOT prove the session is signed in; check the page content.
