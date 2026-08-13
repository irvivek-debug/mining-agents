"""Serve both applications, and proxy the workspace to the deployed agents.

Application 1 is static and needs no server at all. Application 2 needs this
one for exactly one reason: the 52 entrypoints are deployed
`--no-allow-unauthenticated`, so calling one requires a Google-signed OIDC
identity token scoped to that service's URL, and a browser page cannot mint
one. Everything else here is a static file server.

The interesting design decision is what happens when there are no credentials,
which is the state this repository is in most of the time. The route does not
fall back to a canned response. It returns the failure — the exact exception
text from the token mint or the service lookup — and the screens render it as
NOT CONNECTED. A demo that quietly serves a fixture while claiming to have
called an agent is worse than one that says it could not.

Run: python -m uvicorn apps.workspace.server:app --port 8800 --reload
"""
from __future__ import annotations

import pathlib

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from mining_agents.config import settings
from scripts.deploy import REGION, service_name
from mining_agents.registry import registrations

REPO = pathlib.Path(__file__).resolve().parents[2]
APPS = REPO / "apps"

# Cloud Run's Admin API, used once per status check to learn which of the 52
# services actually exist and what their URLs are. Asking the API beats keeping
# a list here: a service that was never deployed, or was deleted, then shows as
# absent instead of as a URL that 404s.
RUN_API = f"https://run.googleapis.com/v2/projects/{{project}}/locations/{REGION}/services"

# ADK's Cloud Run container exposes the standard ADK API server. A caller
# creates a session and then posts a message to it; both paths are ADK's, not
# this repo's, and are spelled here rather than guessed at call time.
SESSION_PATH = "/apps/{app}/users/{user}/sessions/{session}"
RUN_PATH = "/run"

app = FastAPI(title="Mining Agents workspace")


def _entrypoints() -> dict[str, str]:
    """agent_id -> Cloud Run service name, from the same function that deploys.

    Importing `service_name` rather than formatting the string here is the
    whole of the guarantee that this proxy addresses the service the deploy
    script created.
    """
    return {e["agent_id"]: service_name(e["agent_id"]) for e in registrations()}


class NotConnected(Exception):
    """No credentials, or no such service. Carries the reason to the screen."""

    def __init__(self, stage: str, detail: str):
        super().__init__(detail)
        self.stage = stage
        self.detail = detail


def _access_token() -> str:
    """An OAuth access token for the Cloud Run Admin API, from ADC."""
    import google.auth
    import google.auth.transport.requests

    try:
        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        creds.refresh(google.auth.transport.requests.Request())
    except Exception as exc:  # noqa: BLE001 - the text is the product here
        raise NotConnected("application-default credentials", f"{type(exc).__name__}: {exc}")
    return creds.token


def _identity_token(audience: str) -> str:
    """An OIDC identity token for one service URL.

    User credentials from `gcloud auth application-default login` cannot mint
    one of these; a service account or an impersonation grant can. The
    distinction matters enough to surface, because the fix differs.
    """
    import google.auth.transport.requests
    import google.oauth2.id_token

    try:
        return google.oauth2.id_token.fetch_id_token(
            google.auth.transport.requests.Request(), audience
        )
    except Exception as exc:  # noqa: BLE001
        raise NotConnected(
            "identity token",
            f"{type(exc).__name__}: {exc}. A user credential cannot mint an "
            "OIDC token for a Cloud Run audience; set "
            "GOOGLE_APPLICATION_CREDENTIALS to a service-account key, or grant "
            "the signed-in principal Service Account Token Creator on the "
            "runtime account.",
        )


def _services() -> dict[str, str]:
    """Deployed service name -> URL, one Admin API call for all of them."""
    project = settings().project_id
    token = _access_token()
    found: dict[str, str] = {}
    url = RUN_API.format(project=project)
    with httpx.Client(timeout=30) as client:
        while url:
            reply = client.get(url, headers={"Authorization": f"Bearer {token}"})
            if reply.status_code != 200:
                raise NotConnected(
                    "cloud run services.list",
                    f"HTTP {reply.status_code}: {reply.text[:400]}",
                )
            body = reply.json()
            for svc in body.get("services", []):
                found[svc["name"].rsplit("/", 1)[-1]] = svc.get("uri", "")
            page = body.get("nextPageToken")
            url = f"{RUN_API.format(project=project)}?pageToken={page}" if page else None
    return found


@app.get("/api/runtime")
def runtime() -> JSONResponse:
    """Whether the workspace can reach the agents, and which ones exist.

    This is the honest answer to "which agents are running right now". Cloud
    Run scales to zero by design, so no agent is *running* between calls; what
    can be stated is which services are deployed and reachable. A screen that
    invented a live count would be inventing the one number this architecture
    guarantees is usually zero.
    """
    expected = _entrypoints()
    try:
        live = _services()
    except NotConnected as exc:
        return JSONResponse(
            {
                "connected": False,
                "stage": exc.stage,
                "detail": exc.detail,
                "project": settings().project_id,
                "region": REGION,
                "expected": len(expected),
            }
        )
    deployed = {aid: live[svc] for aid, svc in expected.items() if svc in live}
    return JSONResponse(
        {
            "connected": True,
            "project": settings().project_id,
            "region": REGION,
            "expected": len(expected),
            "deployed": sorted(deployed),
            "missing": sorted(set(expected) - set(deployed)),
            "note": (
                "Cloud Run scales to zero. 'Deployed' means the service exists "
                "and has a URL; between calls no instance is running, and that "
                "is the intended cost behaviour, not a fault."
            ),
        }
    )


@app.post("/api/invoke/{agent_id}")
async def invoke(agent_id: str, request: Request) -> JSONResponse:
    """Forward one prompt to one agent, over an OIDC identity token.

    Body: {"prompt": str, "user_id": str, "session_id": str}. The reply is
    ADK's own event list, passed through unchanged — reshaping it here would
    put a second opinion between the screen and the agent.
    """
    expected = _entrypoints()
    if agent_id not in expected:
        return JSONResponse(
            {"connected": False, "stage": "catalog",
             "detail": f"{agent_id} is not an externally callable entrypoint"},
            status_code=404,
        )

    body = await request.json()
    prompt = (body.get("prompt") or "").strip()
    if not prompt:
        return JSONResponse(
            {"connected": False, "stage": "request", "detail": "prompt is required"},
            status_code=400,
        )
    user_id = body.get("user_id") or "workspace"
    session_id = body.get("session_id") or "workspace-session"

    try:
        live = _services()
        base = live.get(expected[agent_id])
        if not base:
            raise NotConnected(
                "cloud run",
                f"service {expected[agent_id]} is not deployed in {REGION}",
            )
        token = _identity_token(base)
    except NotConnected as exc:
        return JSONResponse(
            {"connected": False, "stage": exc.stage, "detail": exc.detail},
            status_code=503,
        )

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(base_url=base, timeout=300, headers=headers) as client:
        # ADK requires the session to exist before /run accepts a message for
        # it. Re-creating an existing session answers 400, which is not an
        # error here: it means the session is already there.
        await client.post(
            SESSION_PATH.format(app=agent_id, user=user_id, session=session_id),
            json={},
        )
        reply = await client.post(
            RUN_PATH,
            json={
                "app_name": agent_id,
                "user_id": user_id,
                "session_id": session_id,
                "new_message": {"role": "user", "parts": [{"text": prompt}]},
            },
        )
    if reply.status_code != 200:
        return JSONResponse(
            {"connected": False, "stage": "agent",
             "detail": f"HTTP {reply.status_code}: {reply.text[:800]}"},
            status_code=502,
        )
    return JSONResponse({"connected": True, "agent_id": agent_id,
                         "events": reply.json()})


@app.get("/")
def home() -> RedirectResponse:
    return RedirectResponse("/workspace/")


# Mounted last so the API routes above win. The mount point is apps/, not
# apps/workspace/, because every screen in both applications links to
# ../shared/ for tokens.css and the data bundle; serving one application in
# isolation would break those paths and force a second copy of the shared tree.
app.mount("/", StaticFiles(directory=APPS, html=True), name="apps")
