---
name: cloud-architect
description: Use when designing or operating GCP estates for AI agents (Vertex Agent Engine, Gemini Enterprise, BigQuery) — covers quota headroom, service-account tiers, credential hygiene, regional model serving, and pagination.
---

# Cloud Architect — patterns from the mining-agents engagement

## Never size an estate exactly at its quota
`ReasoningEngineEntitiesPerProjectPerRegion` defaulted to 100 and the
estate was 100 agents. Every rebuild is delete-then-create, deletion does
not free quota immediately, so every rebuild raced the reconciliation
window — it destroyed an agent three separate times. Keep ≥5 slots of
headroom; file the increase via the Cloud Quotas API
(`quotaPreferences`, programmatic, ~16h to grant) before you need it.

## Few service accounts, not one per agent
Three per-tier service accounts served 100 agents. The engine SA needs
BOTH `bigquery.jobUser` AND `bigquery.dataViewer` — jobUser alone runs
jobs but cannot read tables (signature: tools fire, then
`403 SERVICE_DISABLED`, misleading because the API is enabled).

## Credentials never travel in artifacts
Passing local ADC into an agent build cloudpickles a human refresh token
into the deployed artifact (measured and confirmed). Use
`compute_engine.Credentials()` — resolves at the metadata server at call
time, carries no secret. There is no error signature; only a pickle
inspection finds it.

## Know where the model is served
`gemini-3.7-flash` serves ONLY from the `global` endpoint; eleven regions
404. An engine in us-central1 resolves publisher models regionally — set
`env_vars={"GOOGLE_CLOUD_LOCATION": "global"}`. Signature: every
invocation 404s on a model that demonstrably exists in the console.

## Paginate every listing, always
Two separate incidents came from single-page reads: a quota-poll saw "99
engines" when the truth was one page of many, and a Gemini Enterprise
listing capped at 100 caused 8 duplicate registrations. Any list call
without a pageToken loop is a latent bug.

## Two credential systems, two lifetimes
`gcloud auth login` (CLI) and `gcloud auth application-default login`
(ADC/SDK) are separate credentials that expire separately, and org reauth
policies kill both on a schedule no refresh token survives. Design every
multi-hour run to detect 401/RefreshError and pause at a work boundary —
a run that fails forward turns one login into an inventory of damage.
