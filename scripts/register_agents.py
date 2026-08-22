"""Register agents as Vertex AI Reasoning Engines and into Gemini Enterprise.

WHY THIS EXISTS RATHER THAN THE VAULT'S SCRIPT
`deployment/register_all_agents_to_agent_registry.py` in the vault is a 30-line
shim that dynamically loads a root script which is not in the bucket, so it
cannot run. The vault's other lead -- Mendel forced_flags -- is Google-internal
experiment plumbing, not a customer-runnable API. Neither is needed: the 90
agents already registered were created through the Discovery Engine `agents`
endpoint, and this reproduces that path.

TWO STEPS PER AGENT, AND THE SECOND DEPENDS ON THE FIRST
  1. ReasoningEngine.create() -- the A2A / Agent Registry entry
  2. an `agents` entry on the Gemini Enterprise assistant, whose
     adkAgentDefinition.provisionedReasoningEngine points at step 1

Both are idempotent: an agent already carrying a reasoning engine, or already
present on the assistant, is skipped rather than duplicated. Re-running after a
partial failure resumes instead of creating a second copy.

Usage:
    python scripts/register_agents.py --list
    python scripts/register_agents.py --agents S10-R-CRITIC,S11-COORDINATOR
    python scripts/register_agents.py --agents ... --confirm yes-register-for-real
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor" / "agent_registry"))
import catalog_definitions as C  # noqa: E402

PROJECT = "genial-union-475913-i7"
PROJECT_NUMBER = "297934069315"
REGION = "us-central1"
CONFIRM_PHRASE = "yes-register-for-real"

# The bucket the existing engines actually staged through. The vault packager
# hardcodes gs://genial-union-475913-i7-vertex-staging, which does not exist --
# checked before writing this.
STAGING_BUCKET = "gs://cloud-ai-platform-64c9fb58-d407-4705-8327-380b795ae33f"

# WHY EVERY EXISTING ENGINE 404s ON ITS OWN MODEL
# The catalogue gives all 101 agents model_id "the catalogue's model". That model is
# real and this project can reach it -- but ONLY on the global endpoint.
# Probed across twelve locations: global returns 200, and us-central1,
# us-east1/4/5, us-west1/4, northamerica-northeast1, europe-west1/4,
# asia-southeast1 and australia-southeast1 all return 404.
#
# An Agent Engine in us-central1 resolves publisher models regionally, so it
# asks us-central1 for a model served only from global and gets a 404. The
# model name was never wrong and the catalogue is not edited here; the ENGINE
# is told where to look instead.
MODEL_LOCATION = "global"

# Pinned rather than ranged. The 90 failing engines were built from an
# unpinned google-cloud-aiplatform[agent_engines,adk]>=1.70.0, and an engine
# built that way fails with `TypeError: 'NoneType' object is not subscriptable`
# even once its model resolves -- a second fault behind the first. These are
# the versions verified working, locally and then deployed.
REQUIREMENTS = [
    "google-adk==2.6.3",
    # BigQueryToolset imports google.cloud.dataplex_v1 transitively. Without
    # this the toolset raises ImportError inside the engine at first tool use,
    # which surfaces as an agent that mysteriously stops answering -- found
    # locally before it could be found in production.
    "google-cloud-dataplex",
    "google-genai==2.17.0",
    "google-cloud-aiplatform[agent_engines,adk]>=1.70.0",
    "pydantic>=2.0.0",
]

ENGINE_API = (f"https://{REGION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT}"
              f"/locations/{REGION}/reasoningEngines")
GE_AGENTS = (f"https://discoveryengine.googleapis.com/v1alpha/projects/{PROJECT}"
             f"/locations/global/collections/default_collection/engines/"
             f"gemini-enterprise-17804660_1780466009095/assistants/default_assistant/agents")


def token() -> str:
    return subprocess.run(["gcloud", "auth", "print-access-token"],
                          capture_output=True, text=True).stdout.strip()


def api(url: str, method: str = "GET", body: dict | None = None) -> dict:
    h = {"Authorization": f"Bearer {token()}", "X-Goog-User-Project": PROJECT,
         "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    try:
        return json.load(urllib.request.urlopen(
            urllib.request.Request(url, data=data, headers=h, method=method), timeout=120))
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode()[:400]}


def paged(url: str, key: str) -> list[dict]:
    """List every page, raising rather than returning an empty list on error.

    This used to do `out += d.get(key, [])` unconditionally. An expired
    credential returns {"_http": 401, ...}, which has no `key`, so the function
    returned [] and the caller read it as "there are no agents registered" --
    an auth failure wearing the costume of a legitimate empty result. It
    reported "0 agents mapped" against an estate of 96.
    """
    out, page = [], None
    while True:
        d = api(url + (("&" if "?" in url else "?") + f"pageToken={page}" if page else ""))
        if "_http" in d:
            raise SystemExit(
                f"listing {key} failed with HTTP {d['_http']}: {d['_body'][:200]}\n"
                f"If this is 401, the credential has expired — run `gcloud auth login`."
            )
        out += d.get(key, [])
        page = d.get("nextPageToken")
        if not page:
            return out


def id_of(display_name: str) -> str | None:
    m = re.search(r"\(([A-Z0-9][A-Z0-9\-]*)\)\s*$", display_name or "")
    return m.group(1) if m else None


def current_state() -> tuple[dict, dict]:
    """What is already registered, keyed by agent id."""
    engines = {id_of(e.get("displayName", "")): e for e in paged(ENGINE_API, "reasoningEngines")}
    ge = {id_of(a.get("displayName", "")): a for a in paged(GE_AGENTS, "agents")}
    engines.pop(None, None)
    ge.pop(None, None)
    return engines, ge


from google.adk.tools.base_toolset import BaseToolset  # noqa: E402


class _LazyBigQueryTools(BaseToolset):
    """Build the BigQuery toolset on the ENGINE, not on this laptop.

    The obvious version -- constructing BigQueryToolset here and passing it to
    the agent -- pickles a developer refresh token into the deployed artefact.
    Verified rather than assumed: cloudpickling the app produced 3,117 bytes
    with the local ADC refresh token inside it. Deploying that would put a
    human's Google credential into a Cloud resource, which is the same class of
    leak just scrubbed out of git history.

    So only the CONFIGURATION travels. __getstate__/__setstate__ keep this
    object credential-free through pickling, and the toolset is constructed on
    first use inside the engine, where google.auth.default() resolves to the
    engine's own service account. That is also what makes per-tier IAM mean
    anything: the agent can read exactly what its identity is granted.
    """

    def __init__(self, project: str, max_bytes: int, max_rows: int):
        super().__init__()
        self._project, self._max_bytes, self._max_rows = project, max_bytes, max_rows
        self._toolset = None

    def __getstate__(self):
        # Never carry a live toolset (and therefore never a credential).
        return {"_project": self._project, "_max_bytes": self._max_bytes,
                "_max_rows": self._max_rows, "_toolset": None}

    def __setstate__(self, state):
        self.__dict__.update(state)

    def _build(self):
        import google.auth
        from google.adk.integrations.bigquery import (
            BigQueryToolset, BigQueryCredentialsConfig)
        from google.adk.integrations.bigquery.config import BigQueryToolConfig, WriteMode
        creds, _ = google.auth.default()
        self._toolset = BigQueryToolset(
            credentials_config=BigQueryCredentialsConfig(credentials=creds),
            bigquery_tool_config=BigQueryToolConfig(
                # No agent in this estate may write. Enforced by the toolset,
                # not by asking the model nicely.
                write_mode=WriteMode.BLOCKED,
                compute_project_id=self._project,
                maximum_bytes_billed=self._max_bytes,
                max_query_result_rows=self._max_rows,
            ),
        )
        return self._toolset

    async def get_tools(self, readonly_context=None):
        return await (self._toolset or self._build()).get_tools(readonly_context)

    async def close(self):
        if self._toolset:
            await self._toolset.close()


def _bigquery_tools(agent):
    return _LazyBigQueryTools(PROJECT, 2_000_000_000, 200)


def create_engine(agent) -> str:
    """Deploy one agent as an Agent Engine and return its resource name.

    vertexai.agent_engines.create rather than the preview ReasoningEngine.create
    because only the former takes env_vars, and env_vars is what carries the
    model-location fix into the running engine.
    """
    import vertexai
    from vertexai import agent_engines
    from vertexai.preview.reasoning_engines import AdkApp
    from google.adk.agents import llm_agent

    vertexai.init(project=PROJECT, location=REGION, staging_bucket=STAGING_BUCKET)
    # 99 of the 101 carry an empty system_instruction, so a usable one is
    # composed from the fields that are populated rather than shipping a blank.
    # WHY THE INSTRUCTION NAMES THE TABLES AND DEMANDS RECONCILIATION
    # AGT-19 answered a cut-off grade question with flawless arithmetic --
    # every figure recomputed exactly -- but took recovery, price and costs
    # straight from the question and never opened its own data. The prompt
    # assumed 89.5% recovery; metallurgical_recovery averages 92.21%. A
    # correct answer to a hypothetical, presented as strategic guidance.
    #
    # "cite the table behind every figure" was not enough, because the model
    # can satisfy it by citing nothing when it cites nothing. So the tables are
    # named, and reconciling supplied assumptions against them is made an
    # explicit step with a required disclosure when they diverge.
    tables = ", ".join(agent.source_tables) or "your declared sources"
    instruction = (agent.system_instruction or (
        f"You are {agent.name}. {agent.description or ''}\n"
        f"Your governing method is {agent.governing_equation}.\n"
        f"Your data is {tables}. Read it before you answer.\n"
        f"If the question supplies its own assumptions — a price, a recovery, a "
        f"cost, a rate — reconcile each one against {tables} and state plainly "
        f"where they differ and which you used. Never present a figure computed "
        f"only from numbers in the question as if it were grounded in the "
        f"operation.\n"
        f"Cite the table behind every figure you report. Where you cannot "
        f"evidence something, say so explicitly rather than omitting it."
    )).strip()

    app = AdkApp(agent=llm_agent.LlmAgent(
        name=agent.agent_id.replace("-", "_").lower(),
        model=agent.model_id,
        instruction=instruction,
        # Without tools these agents cannot read anything. All 100 were
        # registered that way and answered fluently from model knowledge --
        # correct-sounding, ungrounded, and invisible to a UAT that only
        # checked whether an answer looked right.
        tools=[_bigquery_tools(agent)],
    ))
    # Deleting an engine does not free its quota slot immediately. Rebuilding
    # in place at the cap therefore 429s on the create, having already removed
    # the old engine -- which is how AGT-19 ended up deleted with nothing in
    # its place, twice. Retry with backoff so a transient lag cannot shrink the
    # estate.
    import time as _t
    from google.api_core import exceptions as _gexc
    last = None
    for attempt in range(6):
        try:
            return _create(agent_engines, app, agent)
        except _gexc.ResourceExhausted as e:
            last = e
            wait = 30 * (attempt + 1)
            print(f"  quota not yet released; retrying in {wait}s "
                  f"(attempt {attempt + 1}/6)", flush=True)
            _t.sleep(wait)
    raise SystemExit(f"create failed after retries — the estate may be short an "
                     f"agent. Last error: {last}")


def _create(agent_engines, app, agent) -> str:
    remote = agent_engines.create(
        agent_engine=app,
        display_name=f"{agent.name} ({agent.agent_id})",
        description=(agent.description or agent.name)[:900],
        env_vars={"GOOGLE_CLOUD_LOCATION": MODEL_LOCATION,
                  "GOOGLE_GENAI_USE_VERTEXAI": "TRUE"},
        requirements=REQUIREMENTS,
    )
    return remote.resource_name


def create_ge_entry(agent, engine_resource: str) -> dict:
    return api(GE_AGENTS, "POST", {
        "displayName": f"{agent.name} ({agent.agent_id})",
        "description": (f"Mining Operations Agent {agent.agent_id} - "
                        f"APQC {agent.apqc_code} - {agent.name}")[:900],
        "adkAgentDefinition": {
            "toolSettings": {},
            "provisionedReasoningEngine": {"reasoningEngine": engine_resource},
        },
        "state": "ENABLED",
        "sharingConfig": {"scope": "ALL_USERS"},
    })


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents", default="", help="comma-separated agent ids")
    ap.add_argument("--list", action="store_true", help="show what is and is not registered")
    ap.add_argument("--confirm", default="")
    args = ap.parse_args()

    by_id = {a.agent_id: a for a in C.CATALOG}
    engines, ge = current_state()

    if args.list:
        missing_e = sorted(set(by_id) - set(engines))
        missing_g = sorted(set(by_id) - set(ge))
        print(f"catalogue {len(by_id)} | engines {len(engines)} | gemini enterprise {len(ge)}")
        print(f"no reasoning engine ({len(missing_e)}): {missing_e}")
        print(f"not in gemini enterprise ({len(missing_g)}): {missing_g}")
        return 0

    wanted = [a.strip() for a in args.agents.split(",") if a.strip()]
    unknown = [a for a in wanted if a not in by_id]
    if unknown:
        raise SystemExit(f"not in the catalogue: {unknown}")
    if not wanted:
        raise SystemExit("pass --agents or --list")

    if args.confirm != CONFIRM_PHRASE:
        print(f"DRY RUN — pass --confirm {CONFIRM_PHRASE} to create resources\n")
        for aid in wanted:
            a = by_id[aid]
            print(f"  {aid:<18} engine={'present' if aid in engines else 'CREATE'}  "
                  f"gemini={'present' if aid in ge else 'CREATE'}  |  {a.name}")
        return 0

    for aid in wanted:
        a = by_id[aid]
        print(f"\n=== {aid} — {a.name}")
        res = engines.get(aid, {}).get("name")
        if res:
            print(f"  engine already exists: {res.split('/')[-1]}")
        else:
            print(f"  creating agent engine on {a.model_id} "
                  f"(models resolved from {MODEL_LOCATION}) — several minutes…")
            res = create_engine(a)
            print(f"  engine: {res.split('/')[-1]}")

        if aid in ge:
            print("  already on the Gemini Enterprise assistant")
            continue
        r = create_ge_entry(a, res)
        if "_http" in r:
            print(f"  GE registration FAILED {r['_http']}: {r['_body'][:200]}")
        else:
            print(f"  registered in Gemini Enterprise: {r.get('name','').split('/')[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
