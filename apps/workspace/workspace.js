/* Shared pieces of Application 2.
 *
 * The workspace is where a person does the work, so every screen has to answer
 * three questions the case application never had to: what does this agent
 * actually read, by what method, and what part of the answer is not settled.
 * The components below are the four answers, written once:
 *
 *   runState()   — whether the deployed agents are reachable at all
 *   agentCard()  — one entrypoint, at the level of detail a rail needs
 *   method()     — the formula, pattern or model behind a result
 *   inputs()     — the tables and columns, named, with their gaps
 *
 * Nothing here composes prose on an agent's behalf. Where an agent's own words
 * would go, notConnected() goes instead.
 */

const CAT = DATA.catalog;
const WS = DATA.workspace;
const AGENTS = Object.fromEntries(CAT.agents.map((a) => [a.agent_id, a]));
const PERSONAS = DATA.personas.personas;

/* Run states, per docs/phase-2-ux.md: glyph AND word AND colour on every one,
   so none of the three is load-bearing alone. Colour is the third signal, not
   the first — P6 works in hearing protection and P3 in gloves under pit light,
   and neither can be assumed to resolve a hue. */
const STATE = {
  done: { glyph: "✓", word: "DONE", cls: "b-ok" },
  running: { glyph: "●", word: "RUNNING", cls: "b-info" },
  blocked: { glyph: "⚠", word: "BLOCKED", cls: "b-crit" },
  waiting: { glyph: "○", word: "WAITING", cls: "b-idle" },
};

function stateBadge(key, suffix) {
  const s = STATE[key];
  return (
    `<span class="badge ${s.cls}">${s.glyph} ${s.word}` +
    (suffix ? ` · ${esc(suffix)}` : "") +
    "</span>"
  );
}

/** Read a query-string parameter, falling back to a default. */
function param(name, fallback) {
  return new URLSearchParams(location.search).get(name) || fallback;
}

function agentName(id) {
  return AGENTS[id] ? AGENTS[id].display_name : id;
}

/** The block every screen shows where an agent's generated text would appear.
 *
 *  This repository holds no recorded agent responses, and the build says so in
 *  workspace.runtime rather than each screen deciding for itself. Writing a
 *  plausible transcript here would be the single most damaging thing this
 *  artifact could do: everything else on the screen is checkable against the
 *  catalog, and one invented paragraph would put all of it in doubt. */
function notConnected(what) {
  const r = WS.runtime;
  return (
    '<div class="not-connected">' +
    `<div class="badge b-warn">⚠ NOT CONNECTED</div>` +
    `<p class="nc-what">${esc(what)}</p>` +
    `<p class="nc-why">${esc(r.reason)}</p>` +
    `<p class="nc-why">${esc(r.consequence)}</p>` +
    `<p class="nc-route mono">POST ${esc(r.proxy_route)}</p>` +
    "</div>"
  );
}

/** The live runtime band. Asks the server which of the 52 services exist.
 *
 *  Auditor finding A8 asked for a running count on the cockpit. The honest
 *  version of that count is not a number of running agents — Cloud Run scales
 *  to zero, so between calls the true answer is nearly always none, and a
 *  dashboard printing a fabricated "7 running" would be inventing exactly the
 *  figure the architecture guarantees is zero. What can be stated is whether
 *  the estate is reachable and how many services are deployed, so that is what
 *  this asks for and what it prints. */
function runState(node) {
  node.innerHTML =
    '<div class="card"><div class="card-cap">Runtime</div>' +
    '<p class="dim mono" style="font-size:11px;margin:0">checking /api/runtime …</p></div>';

  const offline = (headline, detail) => {
    node.innerHTML =
      '<div class="card"><div class="card-cap">Runtime</div>' +
      '<div class="run-state">' +
      '<span class="badge b-warn">⚠ NOT CONNECTED</span>' +
      `<div><div>${esc(headline)}</div>` +
      `<div class="dim" style="font-size:12.5px;margin-top:4px">${esc(detail)}</div></div>` +
      "</div></div>";
  };

  fetch("/api/runtime")
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error("HTTP " + r.status))))
    .then((r) => {
      if (!r.connected) {
        offline(`${r.stage}: could not reach the deployed agents.`, r.detail);
        return;
      }
      const n = r.deployed.length;
      node.innerHTML =
        '<div class="card"><div class="card-cap">Runtime</div>' +
        '<div class="run-state">' +
        `<span class="badge ${n === r.expected ? "b-ok" : "b-warn"}">` +
        `${n === r.expected ? "✓" : "⚠"} ${n} / ${r.expected} DEPLOYED</span>` +
        `<div><div>${esc(r.project)} · ${esc(r.region)}</div>` +
        `<div class="dim" style="font-size:12.5px;margin-top:4px">${esc(r.note)}</div>` +
        (r.missing.length
          ? `<div class="dim mono" style="font-size:11px;margin-top:4px">not deployed: ${esc(
              r.missing.join(" ")
            )}</div>`
          : "") +
        "</div></div></div>";
    })
    .catch(() =>
      /* Opened straight off disk, or the server is not running. Both are normal
         ways to read these screens and neither is an error worth alarming
         about — but neither can be described as connected either. */
      offline(
        "No runtime to query.",
        "These screens are being served without apps/workspace/server.py, so " +
          "there is nothing to ask about the deployed services. Run " +
          "`python -m uvicorn apps.workspace.server:app` to check them."
      )
    );
}

/** One entrypoint as a rail row: id, name, and the two facts that change how
 *  you approach it — whether it needs a human, and what it is built from.
 *
 *  Descriptions are inline and never on hover. Auditor finding A2: P3 works
 *  from a rugged tablet in gloves and P7 from a handheld, and neither device
 *  has a hover state, so content behind one is content those two personas
 *  cannot reach. Nothing in this suite hides behind hover. */
function agentRow(id, href, current) {
  const a = AGENTS[id];
  const kind = a.pattern === "A" ? `swarm of ${swarmSize(a.swarm_id)}` : "deep agent";
  return (
    `<a class="rail-row${id === current ? " on" : ""}" href="${href}">` +
    `<span class="rail-id mono">${esc(id)}</span>` +
    `<span class="rail-body"><span class="rail-name">${esc(a.display_name)}</span>` +
    `<span class="rail-sub mono">${esc(kind)} · ${esc(a.apqc_code)}</span></span>` +
    (a.hitl_required ? '<span class="badge b-warn">⚠ APPROVAL</span>' : "") +
    "</a>"
  );
}

function swarmSize(swarmId) {
  const s = CAT.swarms[swarmId];
  return s ? 2 + s.specialists.length : 0;
}

/** The method behind an agent's answer, drawn from what the catalog grants it.
 *
 *  docs/phase-2-ux.md: "For deterministic agents the method is the provenance.
 *  Hiding it behind 'the agent calculated' is what makes an engineer distrust
 *  the whole suite." So a declared formula prints its expression, a declared
 *  traversal prints its SQL, a declared model prints its name — and an agent
 *  whose method is a query the model composes at runtime says exactly that,
 *  rather than implying a rigour it does not have. */
function method(id) {
  const a = AGENTS[id];
  const parts = [];

  for (const [key, f] of Object.entries(WS.formulas.registry)) {
    if (!f.named_by.includes(id)) continue;
    parts.push(
      '<div class="method">' +
        `<div class="method-cap mono">FORMULA · ${esc(key)}</div>` +
        `<div class="expression mono">${esc(f.expression)}</div>` +
        `<div class="method-sub mono">inputs: ${esc(f.inputs.join(", "))}</div>` +
        "</div>"
    );
  }

  for (const t of a.traversals) {
    const spec = WS.traversals[t];
    if (!spec) continue;
    parts.push(
      '<div class="method">' +
        `<div class="method-cap mono">GRAPH TRAVERSAL · ${esc(t)}</div>` +
        `<div class="console">${esc(spec.sql)}</div>` +
        `<div class="method-sub mono">binds ${esc(spec.params.join(", "))} · returns ${esc(
          spec.columns.join(", ")
        )}</div>` +
        "</div>"
    );
  }

  for (const m of a.models) {
    parts.push(
      '<div class="method">' +
        '<div class="method-cap mono">BQML MODEL</div>' +
        `<div class="expression mono">${esc(m)}</div>` +
        '<div class="method-sub mono">called through bqml_predict; the prediction ' +
        "is the model's, not the language model's</div>" +
        "</div>"
    );
  }

  if (a.tools.includes("operational_math") && !parts.some((p) => p.includes("FORMULA"))) {
    parts.push(
      '<div class="method">' +
        '<div class="method-cap mono">DETERMINISTIC MATH</div>' +
        `<div class="method-sub">${esc(WS.formulas.note)} Available here: ` +
        `${esc(Object.keys(WS.formulas.registry).join(", "))}.</div>` +
        "</div>"
    );
  }

  if (a.tools.includes("bq_query")) {
    parts.push(
      '<div class="method">' +
        '<div class="method-cap mono">SQL, COMPOSED AT RUNTIME</div>' +
        '<div class="method-sub">bq_query takes whatever SELECT the model writes ' +
        "against the tables below. There is no fixed statement to print here, " +
        "which is why the tables and their columns are named instead — that " +
        "boundary is fixed and this one is not.</div>" +
        "</div>"
    );
  }

  return parts.join("");
}

/** The tables an agent reads, named to the column, with their gaps stated.
 *
 *  "The inputs panel names the table and the column, not 'inventory data'."
 *  Three statuses are kept apart on purpose: a table whose meaning is
 *  documented, one whose schema is known but whose business meaning is still
 *  being written, and one that BigQuery holds but this machine does not. */
function inputs(id) {
  const a = AGENTS[id];
  if (!a.source_tables.length) {
    return '<p class="dim">This agent reads no table; it computes.</p>';
  }
  return a.source_tables
    .map((qualified) => {
      const t = WS.tables.tables[qualified];
      if (!t) return `<div class="tbl"><div class="mono">${esc(qualified)}</div></div>`;
      const cols = t.columns
        .map(
          (c) =>
            `<li><span class="mono">${esc(c.name)}</span> ` +
            `<span class="dim mono">${esc(c.type)}</span>` +
            (c.meaning ? `<div class="col-meaning">${esc(c.meaning.trim())}</div>` : "") +
            "</li>"
        )
        .join("");
      return (
        '<details class="tbl">' +
        "<summary>" +
        `<span class="mono">${esc(qualified)}</span>` +
        `<span class="dim mono">${esc(t.columns.length)} cols · ${num(
          t.rows_at_profile
        )} rows at profile</span>` +
        (t.local_parquet
          ? '<span class="badge b-ok">✓ LOCAL COPY</span>'
          : '<span class="badge b-idle">○ WAREHOUSE ONLY</span>') +
        "</summary>" +
        (t.description
          ? `<p class="tbl-desc">${esc(t.description)}</p>`
          : '<p class="tbl-desc dim">Business meaning for this table has not been ' +
            "written yet; the column names and types below are BigQuery's own.</p>") +
        `<ul class="cols">${cols}</ul>` +
        "</details>"
      );
    })
    .join("");
}

/** What this agent's answer cannot settle, derived rather than asserted.
 *
 *  Every screen that shows a result also shows this, and SC-4 makes it the
 *  loudest element on the sheet. The list is computed from three real
 *  conditions, so it shrinks on its own as the gaps close. */
function flagsFor(ids) {
  const list = [].concat(ids);
  const tables = [...new Set(list.flatMap((id) => AGENTS[id].source_tables))];
  const models = [...new Set(list.flatMap((id) => AGENTS[id].models))];
  const flags = [];

  const remote = tables.filter((t) => !(WS.tables.tables[t] || {}).local_parquet);
  if (remote.length) {
    flags.push({
      what: `${remote.length} of ${tables.length} source tables are not on this machine`,
      detail: remote.join(", "),
      remedy: "Re-run scripts/build_app_data.py with BigQuery credentials.",
    });
  }

  const undocumented = tables.filter((t) => !(WS.tables.tables[t] || {}).description);
  if (undocumented.length) {
    flags.push({
      what: `${undocumented.length} source tables have no written column semantics`,
      detail: undocumented.join(", "),
      remedy:
        `docs/column-semantics.yaml covers ${WS.tables.documented.length} of ` +
        `${WS.tables.documented.length + WS.tables.undocumented.length} tables; the rest are in progress.`,
    });
  }

  for (const m of models) {
    flags.push({
      what: `BQML model ${m} was not verified by this build`,
      detail: "Whether the model exists and what it was trained on is a warehouse fact.",
      remedy: "Query INFORMATION_SCHEMA.MODELS with credentials.",
    });
  }

  flags.push({
    what: "No response from the deployed agent",
    detail: WS.runtime.reason,
    remedy: "Serve these screens through apps/workspace/server.py with credentials.",
  });

  return flags;
}

function unverified(ids) {
  const flags = flagsFor(ids);
  return (
    '<div class="unverified">' +
    '<div class="unverified-cap"><span class="badge b-crit">⚠ UNVERIFIED</span>' +
    `<span>${flags.length} item${flags.length === 1 ? "" : "s"} this screen cannot settle</span></div>` +
    "<ul>" +
    flags
      .map(
        (f) =>
          `<li><strong>${esc(f.what)}</strong>` +
          `<div class="dim mono">${esc(f.detail)}</div>` +
          `<div class="remedy">Remedy: ${esc(f.remedy)}</div></li>`
      )
      .join("") +
    "</ul></div>"
  );
}

/** The persona whose journey names this agent, with the citation.
 *
 *  These summaries are transcribed from docs/personas-and-value-tree.md with
 *  the source line recorded, which is what lets a scenario appear on screen
 *  without anyone having written a scenario for the screen. Where the persona's
 *  journey does not name this agent, nothing is printed rather than a
 *  paraphrase stretched to fit. */
function journeyFor(id) {
  const a = AGENTS[id];
  const p = PERSONAS[a.persona];
  if (!p || !p.journey) return "";
  const named = new RegExp(`\\b${id}\\b`).test(p.journey.summary);
  if (!named) return "";
  return (
    '<div class="card"><div class="card-cap">The scenario this runs in</div>' +
    `<h3>${esc(p.journey.title)}</h3>` +
    `<p>${esc(p.journey.summary.trim())}</p>` +
    '<p class="cite mono">' +
    `${esc(p.title)} · docs/personas-and-value-tree.md line ${esc(p.journey.source_line)}` +
    "</p></div>"
  );
}
