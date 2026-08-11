"""Validate the definitions and publish them to mining_data.agent_catalog."""
from __future__ import annotations

from google.cloud import bigquery

from agents.catalog.definitions import ALL_AGENTS
from agents.config import settings


def _rows() -> list[dict]:
    rows = []
    for a in ALL_AGENTS:
        if not a.source_tables:
            raise ValueError(
                f"agent {a.agent_id!r} declares no source_tables; "
                "every agent must reference at least one real table"
            )
        rows.append(
            {
                "agent_id": a.agent_id,
                "display_name": a.display_name,
                "pattern": a.pattern,
                "swarm_id": a.swarm_id,
                "swarm_role": a.swarm_role,
                "apqc_code": a.apqc_code,
                "persona": a.persona,
                "value_branch": a.value_branch,
                "model_tier": a.model_tier,
                "hitl_required": a.hitl_required,
                "source_tables": a.source_tables,
            }
        )
    return rows


def upsert_catalog() -> int:
    """Replace mining_data.agent_catalog with the current definitions."""
    if len(ALL_AGENTS) != 100:
        raise ValueError(f"expected 100 agents, have {len(ALL_AGENTS)}")
    s = settings()
    client = bigquery.Client(project=s.project_id, location=s.location)
    table_id = f"{s.project_id}.{s.dataset}.agent_catalog"
    job = client.load_table_from_json(
        _rows(), table_id,
        job_config=bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            schema=client.get_table(table_id).schema,
        ),
    )
    job.result()
    return len(ALL_AGENTS)


if __name__ == "__main__":
    print(f"loaded {upsert_catalog()} agents into agent_catalog")
