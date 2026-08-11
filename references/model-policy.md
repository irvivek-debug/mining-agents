# Model Policy

This is the **only** file in the repository permitted to contain a raw model ID.
All agent code refers to tiers. `agents.config.model_for_tier()` parses the table below.

| Tier | Model ID | Used by |
|---|---|---|
| `reasoning` | `gemini-2.5-pro` | 12 swarm coordinators, 12 swarm critics |
| `balanced` | `gemini-2.5-flash` | 36 swarm specialists, 40 Pattern B deep agents |

There is no `high-volume-subagent` tier. No Pattern C agent is in scope for this build.

To change a model, edit this table only. No code change is required.
