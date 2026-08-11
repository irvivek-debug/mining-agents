import subprocess
from agents.config import settings

REQUIRED = ["agent_catalog", "agent_approvals", "agent_run_log", "v_fatigue_scored"]


def _bq_objects():
    s = settings()
    out = subprocess.run(
        [s.bq_binary, "ls", "--max_results=1000", f"{s.project_id}:{s.dataset}"],
        capture_output=True, text=True, check=True,
    ).stdout
    return out


def test_all_additive_objects_exist():
    out = _bq_objects()
    missing = [name for name in REQUIRED if name not in out]
    assert missing == [], f"missing BigQuery objects: {missing}"


def test_v_fatigue_scored_never_exposes_raw_heart_rate():
    s = settings()
    out = subprocess.run(
        [s.bq_binary, "query", "--use_legacy_sql=false", "--nouse_cache",
         "--format=csv", "--max_rows=5",
         f"SELECT * FROM `{s.project_id}.{s.dataset}.v_fatigue_scored` LIMIT 5"],
        capture_output=True, text=True, check=True,
    ).stdout
    header = out.splitlines()[0].lower()
    # DLP requirement: none of the sensitive numeric inputs may appear in the view
    assert "heart_rate_bpm" not in header
    assert "sleep_deficit_hours" not in header
    assert "microsleep_events_detected" not in header
    assert "fatigue_band" in header
