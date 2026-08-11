"""The single entry point. Builds every agent from the catalog."""
from __future__ import annotations

from agents.catalog.definitions import DEEP, SWARMS
from agents.patterns.deep import build_deep_agent
from agents.patterns.swarm import build_swarm


def build_all() -> dict[str, object]:
    """agent_id -> built agent, for the 52 externally-callable entrypoints.

    Swarms are keyed by swarm.swarm_id ("S01".."S12").
    Deep agents are keyed by agent.agent_id ("D01".."D40").
    Total: 52 keys, matching agents.registry.registrable().
    """
    built: dict[str, object] = {}
    for swarm in SWARMS:
        built[swarm.swarm_id] = build_swarm(swarm)
    for agent in DEEP:
        built[agent.agent_id] = build_deep_agent(agent)
    return built


if __name__ == "__main__":
    agents = build_all()
    print(f"built {len(agents)} entrypoints: {', '.join(sorted(agents))}")
