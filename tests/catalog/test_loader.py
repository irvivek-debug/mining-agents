from agents.catalog.definitions import ALL_AGENTS
from agents.catalog.loader import upsert_catalog
from agents.tools.bq_query import run_query


def test_upsert_writes_every_agent():
    written = upsert_catalog()
    assert written == 100
    rows, _ = run_query(
        "SELECT COUNT(*) AS n_agents FROM `mining_data.agent_catalog`",
        {}, ["mining_data.agent_catalog"],
    )
    assert rows[0]["n_agents"] == 100


def test_upsert_is_idempotent():
    upsert_catalog()
    upsert_catalog()
    rows, _ = run_query(
        "SELECT COUNT(*) AS n_agents FROM `mining_data.agent_catalog`",
        {}, ["mining_data.agent_catalog"],
    )
    assert rows[0]["n_agents"] == 100


def test_every_declared_source_table_exists_in_bigquery():
    """A catalog row pointing at a phantom table would fail the PRD metric."""
    rows, _ = run_query(
        "SELECT table_name FROM `mining_data.INFORMATION_SCHEMA.TABLES`",
        {}, ["mining_data.INFORMATION_SCHEMA.TABLES"],
    )
    live = {r["table_name"] for r in rows}
    graphs = {"MiningAssetGraph", "MiningSupplyChainGraph",
              "MiningOperationsSafetyGraph", "MiningOntologyGraph"}
    missing = {}
    for agent in ALL_AGENTS:
        bad = [t for t in agent.source_tables
               if t.split(".")[-1] not in live | graphs]
        if bad:
            missing[agent.agent_id] = bad
    assert missing == {}, f"agents reference non-existent objects: {missing}"
