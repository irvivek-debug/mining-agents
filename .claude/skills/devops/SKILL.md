---
name: devops
description: Use when running long unattended jobs, browser automation at scale, or credentialed batch work — covers pause-at-boundary auth handling, observable watchers, monitor design, background-run traps, and secret hygiene.
---

# DevOps — patterns from the mining-agents engagement

## Long runs pause at boundaries on auth death
Org reauth policies kill CLI and ADC on their own schedule; no token TTL
survives them. A run that detects 401/RefreshError and exits at a batch
boundary with a PAUSED marker costs one login to resume; a run that fails
forward costs an inventory of half-destroyed state (19 agents, one
overnight).

## Watchers must prove they are alive
A grant-watcher hung silently for four hours (heredoc-in-command-
substitution); its empty log was the only symptom. Every polling loop
logs every iteration, including no-change ticks; smoke-test one iteration
in the foreground before backgrounding. A watcher that cannot show a
heartbeat is worse than none.

## Monitors match failure signatures, not just success
Grep alternations must include the ways things actually die: 401/429 (as
`HTTP 401` / `"code": 429` — bare digits false-match engine IDs),
RefreshError, Traceback, quota. Silence must mean "passing", which
requires failure lines to be impossible to miss.

## Background-run traps (macOS/agent-harness)
- A foreground command dies at the harness's 2-minute cap — long jobs get
  `nohup ... &` + `disown`, with `caffeinate -i` to hold sleep.
- `setsid` does not exist on macOS.
- `$VAR` does not persist across separate shell invocations — full paths.
- `pgrep -f` matches your own monitoring shell; match the exact
  interpreter+script string.
- Piping a launcher through `head` truncates the run you are launching.
- Subprocess `env=` overrides silently drop HOME/PATH — gcloud then fails
  as if logged out. Inherit `os.environ` and override only what you must.

## Sessions are singular; clones die
Google rotates browser-session cookies: two copies of one profile diverge
and the loser is signed out mid-run. Parallel browser workers need
separately-minted logins (a human signs in per profile), never copies —
and the run must stop and wait for a human rather than work around auth.

## Secret hygiene is structural
Never `git add -A` near browser profiles or SDK caches; stage named
paths. Session stores (`.profile/`, token caches, `*.pem`) enter
.gitignore before the tool that creates them first runs. If a secret
lands in history: back up, rewrite history, tell the human — their call.

## Estate changes are idempotent and quota-aware
Delete-then-create at the quota cap races reconciliation; poll for a free
slot before uploading, back off in minutes (10/15/20/30) not seconds, and
keep batches small so the blast radius of a mid-batch failure is small.
