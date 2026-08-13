/* The page: pick a role, render its panel, and say honestly whether the agents
 * are reachable.
 *
 * The connection state comes from /api/runtime, not from the build. The old
 * screens rendered DATA.workspace.runtime — a constant baked into bundle.js at
 * build time — and therefore printed NOT CONNECTED in production while the
 * service was connected to all 52. Being wrong in the pessimistic direction is
 * still being wrong.
 */
const PERSONAS = DATA.personas.personas;
const CODES = Object.keys(PERSONAS).sort();

function currentCode() {
  const asked = new URLSearchParams(location.search).get("p");
  return PERSONAS[asked] ? asked : CODES[0];
}

function mountPicker(code) {
  const select = el("role-select");
  select.innerHTML = CODES.map(
    (c) => `<option value="${esc(c)}"${c === code ? " selected" : ""}>${esc(PERSONAS[c].title)}</option>`
  ).join("");
  select.addEventListener("change", () => {
    location.search = `?p=${encodeURIComponent(select.value)}`;
  });
}

function drawerBody(code) {
  const persona = PERSONAS[code];
  const byId = {};
  DATA.catalog.agents.forEach((a) => (byId[a.agent_id] = a));
  const rows = (persona.agents || [])
    .map((id) => byId[id])
    .filter(Boolean)
    .map(
      (a) =>
        `<dt class="mono">${esc(a.agent_id)} · ${esc(a.display_name)}</dt>` +
        `<dd>Pattern ${esc(a.pattern)} · ${esc(a.model_tier)} · APQC ${esc(a.apqc_code)}<br>` +
        `<span class="mono">${esc((a.source_tables || []).join(", "))}</span><br>` +
        `<span class="mono">${esc((a.tools || []).concat(a.traversals || []).join(", "))}</span></dd>`
    )
    .join("");
  return (
    `<dl>${rows}</dl>` +
    `<p>${esc(persona.code)} · value branch ` +
    `<span class="mono">${esc(branchesOf(persona.value_branch).join(", "))}</span></p>`
  );
}

/* The honest answer to "can this page reach the agents", asked of the wire. */
async function showRuntime() {
  const box = document.createElement("div");
  box.className = "runtime-state";
  box.textContent = "Checking whether the agents are reachable…";
  el("sidecar").prepend(box);
  try {
    const reply = await fetch("/api/runtime");
    const state = await reply.json();
    if (state.connected) {
      box.className = "runtime-state ok";
      box.textContent =
        `Connected. ${state.deployed.length} of ${state.expected} agents are deployed ` +
        "and can be asked a question.";
    } else {
      box.className = "runtime-state warn";
      box.textContent = `Not connected: ${state.detail}`;
    }
  } catch (err) {
    // The one case where the build-time constant is the true answer: the page
    // is open off disk or behind a static file server, and there is no API.
    box.className = "runtime-state warn";
    box.textContent = DATA.workspace.runtime.reason;
  }
}

const CODE = currentCode();
mountNav("workspace", "persona.html");
mountPicker(CODE);
el("role-lede").textContent = PERSONAS[CODE].title;
el("panel").innerHTML = renderPanel(CODE, DATA);
el("foot").innerHTML = technicalDrawer(drawerBody(CODE), "agent ids, tables, model tiers") +
  provenance();
showRuntime();
