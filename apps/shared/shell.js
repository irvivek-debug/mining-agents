/* Shared chrome and helpers for both applications.
 *
 * The data arrives as window.MINING_DATA from data/bundle.js, which is a
 * script tag rather than a fetch so the screens also work when opened straight
 * off disk. Everything here reads that object; nothing here holds a figure of
 * its own, because a helper with a hardcoded count is how a screen starts
 * disagreeing with the catalog it claims to describe.
 */

/* `typeof window` rather than plain `window`: this file is also `require`d from
 * Node by the JS tests, which need esc/fig/num/rowPlaces without a DOM. In a
 * browser both guards are true and nothing below changes. */
const DATA = typeof window !== "undefined" ? window.MINING_DATA : undefined;
if (!DATA && typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    document.body.innerHTML =
      '<div class="wrap"><div class="note"><strong>Data missing</strong><br>' +
      "data/bundle.js did not load. Run <code>python -m scripts.build_app_data</code>." +
      "</div></div>";
  });
}

/* Application 1, in the order the argument is made: what the problem is, how
   big it is here, what closing it is worth, how it is closed, and only then
   what it is built on. The labels are the argument, not the file names. */
const CASE_NAV = [
  { href: "index.html", label: "1 · The case" },
  { href: "scenario.html", label: "2 · The gap" },
  { href: "value.html", label: "3 · The prize" },
  { href: "solution.html", label: "4 · The solution" },
  { href: "graph.html", label: "5 · The graph" },
];

/* Application 2. The four destinations are the four standing screens; the
   approval sheet is deliberately absent because it is a modal raised from an
   agent team or a role page and never a place you navigate to on its own. */
const WORK_NAV = [
  { href: "index.html", label: "Cockpit" },
  { href: "swarm.html", label: "Agent teams" },
  { href: "persona.html", label: "My role" },
  { href: "handover.html", label: "Handover" },
];

/* The pill in the corner of every screen. It differs between the two
   applications because the two applications are addressed to different
   readers: the case is read by someone deciding whether the gap is real, and
   the workspace by someone who has already decided and wants to know what is
   deployed. An entrypoint count in the corner of screen one answers a question
   that has not been asked yet, and quietly changes what the screen is about. */
const NAVS = {
  case: {
    items: CASE_NAV,
    brand: "Mining Agents · The case for change",
    pill: () => {
      const row = DATA.signals.gap.rows[0];
      const dp = rowPlaces(row);
      return {
        text: `Recovery ${fig(row.median, row.unit, dp)} → ${fig(row.p90, row.unit, dp)}`,
        title: `${row.label}: this site's ordinary day against its own best day, over ${row.days} days`,
      };
    },
  },
  workspace: {
    items: WORK_NAV,
    brand: "Mining Agents · Site workspace",
    /* The two figures are a distinction, not a pair. "52 entrypoints · 100
       agents" reads as a hundred things to talk to and fifty-two of something
       technical; the truth is the other way round, and it is the fact a reader
       most needs before they start looking for the right agent. */
    pill: () => ({
      text:
        `${DATA.catalog.counts.entrypoints} agents you can talk to · ` +
        `${DATA.catalog.counts.agent_nodes} in the teams behind them`,
      title: "Source of every figure on this page",
    }),
  },
};

/** Escape before interpolation. Part descriptions and technician notes are
 *  free text from the warehouse, and they land inside innerHTML. */
function esc(value) {
  if (value === null || value === undefined) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function num(value) {
  return typeof value === "number" ? value.toLocaleString("en-US") : esc(value);
}

/** How many decimals a figure of this size deserves. A plant does not run to
 *  four decimal places, and an export that carries them because it averaged
 *  something is not a licence to print them. */
function places(v) {
  return Math.abs(v) >= 100 ? 0 : Math.abs(v) >= 10 ? 1 : 2;
}

function fig(v, unit, dp) {
  const step = dp === undefined ? places(v) : dp;
  const n = v.toLocaleString("en-US", {
    minimumFractionDigits: step,
    maximumFractionDigits: step,
  });
  if (!unit) return n;
  // A per-cent sign closes up against its number in English setting; a tonne
  // or a megawatt takes the space. Handling it here rather than at each call
  // site is what keeps "92.32%" and "204.5 t" both right on the same row.
  return unit === "%" ? `${n}%` : `${n} ${unit}`;
}

/** The precision a whole gap row must be printed at.
 *
 *  A gap row prints three numbers that have to survive a reader subtracting
 *  them: 92.3, 94.3 and a gap of 1.96 is a screen caught out by mental
 *  arithmetic. So a row is printed at whatever precision makes its own
 *  subtraction come out, starting from the least that could work — the
 *  cheapest fix is more decimals, and more decimals than the measurement
 *  deserves is its own dishonesty.
 */
function rowPlaces(row) {
  // Where the gap is an absolute difference it is the subject of the row, so
  // it sets the precision too. Rounding a 1.96-point gap to 2.0 because it
  // sits on a 92 discards the measurement to suit its neighbour, and then
  // overstates it by two percent on the way past.
  const start =
    row.delta_kind === "points"
      ? Math.max(places(row.median), places(row.delta))
      : places(row.median);
  for (let dp = start; dp <= 4; dp += 1) {
    const shown = +row.p90.toFixed(dp) - +row.median.toFixed(dp);
    if (Math.abs(shown - +row.delta.toFixed(dp)) < Math.pow(10, -dp) / 2) return dp;
  }
  return 4;
}

/** A magnitude this repository does not establish. Rendered as words, never as
 *  a number, so it cannot be misread as one at a glance. */
function clientInput() {
  return '<div class="metric gap">[CLIENT&nbsp;INPUT<br>REQUIRED]</div>';
}

function mountNav(app, current) {
  const nav = NAVS[app];
  if (!nav) throw new Error(`no nav defined for app ${app}`);
  const links = nav.items
    .map(
      (i) =>
        `<a href="${i.href}"${
          i.href === current ? ' aria-current="page" style="color:var(--fg);border-color:var(--border)"' : ""
        }>${esc(i.label)}</a>`
    )
    .join("");
  const pill = nav.pill();
  const bar = document.createElement("div");
  bar.className = "topbar";
  bar.innerHTML =
    `<span class="brand">${esc(nav.brand)}</span>` +
    `<nav>${links}</nav>` +
    '<span style="flex:1"></span>' +
    `<span class="pill" title="${esc(pill.title)}">${esc(pill.text)}</span>`;
  document.body.prepend(bar);
}

/** The one collapsible every screen ends with.
 *
 *  The instruction was explicit: plain language and tables first, technical
 *  detail at the end, behind something the reader opens on purpose. One helper
 *  rather than ten hand-written <details> blocks, because ten of them is ten
 *  chances for one screen to call it something else and break the pattern the
 *  reader has just learned.
 */
function technicalDrawer(bodyHtml, hint) {
  return (
    '<details class="tbl drawer">' +
    "<summary>Technical detail" +
    (hint ? `<span class="dim">${esc(hint)}</span>` : "") +
    "</summary>" +
    `<div class="drawer-body">${bodyHtml}</div>` +
    "</details>"
  );
}

/** The footer every screen carries: when the data was generated and from what.
 *  A screen that cannot say where its numbers came from is a screen that
 *  cannot be checked. */
function provenance(extra) {
  return (
    '<hr class="rule">' +
    '<div class="card"><div class="card-cap">Provenance</div>' +
    // A dl, not a div: these are dt/dd pairs, which are only valid inside one.
    // The extra class is what lets the stylesheet stack them on a phone, where
    // the two-column form leaves too little room for a dotted module path.
    '<dl class="kv prov">' +
    `<dt>Catalog</dt><dd>${esc(DATA.catalog.source)}</dd>` +
    `<dt>Generated</dt><dd class="mono">${esc(DATA.catalog.generated_at)}</dd>` +
    (extra || "") +
    "</dl></div>"
  );
}

function el(id) {
  const node = document.getElementById(id);
  if (!node) throw new Error(`no element #${id} on this page`);
  return node;
}

/* ---------- whether the deployed agents can be reached ---------- */

/* One /api/runtime call per page, shared by every block that needs the answer.
 *
 * Screens used to render DATA.workspace.runtime — a constant baked into
 * bundle.js when it was generated — so five call sites printed NOT CONNECTED in
 * production while the service was connected to all 52 agents. Being wrong in
 * the pessimistic direction is still being wrong, and it is the more expensive
 * kind here: it says the thing does not work.
 *
 * This lives in the shared shell because the role page had a second copy of the
 * same fetch, guarded differently — one read a 500 with a JSON body as a
 * not-connected runtime, the other as an unreadable reply — and two answers to
 * one question is how two screens in one application come to disagree.
 *
 * Four outcomes, kept apart because they are four different problems. The
 * server answered yes; the server answered no and said why; the server answered
 * with something that is not an answer, so the state is unknown and must not be
 * rendered as either extreme; or there was no server to ask, which is the only
 * case where the baked constant is the true answer.
 */
let _runtimePromise = null;

function runtimeState() {
  if (!_runtimePromise) {
    _runtimePromise = fetch("/api/runtime")
      .then((reply) =>
        reply
          .json()
          .then((body) => {
            // A FastAPI 500 answers {"detail": "Internal Server Error"} — valid
            // JSON, with no `connected` field — and a connected reply with no
            // deployed list cannot support the count every screen prints from
            // it. Neither is a not-connected runtime, and reporting them as one
            // sends a reader looking for a fault in the estate that is really a
            // fault in the endpoint.
            const answered =
              typeof body.connected === "boolean" &&
              (!body.connected || Array.isArray(body.deployed));
            if (!answered) throw new Error("the reply carried no usable answer");
            return body;
          })
          .catch((err) => ({
            connected: false,
            unreadable: true,
            stage: `/api/runtime answered HTTP ${reply.status}`,
            detail: err.message,
          }))
      )
      // The one case where the baked constant is the true answer: no API to
      // ask, because the page is open off disk or behind a static file server.
      .catch(() => ({ ...DATA.workspace.runtime, connected: false, offline: true }));
  }
  return _runtimePromise;
}

/** The three answers in words, written once for every screen that shows one.
 *
 *  The reader here is a supervisor, not an engineer. The stage the check
 *  stopped at and the exception it caught are the two things they can do
 *  nothing with and an administrator cannot do without, so they come back
 *  separately, as drawer markup, rather than as the body copy. A page whose
 *  loudest sentence is `RefreshError: Reauthentication is needed…` has told its
 *  reader nothing they can act on.
 */
function connectionCopy(state) {
  const rows = (pairs) => {
    const kept = pairs.filter((pair) => pair[1]);
    if (!kept.length) return "";
    return (
      "<dl>" +
      kept
        .map(([term, value]) => `<dt>${esc(term)}</dt><dd class="mono">${esc(value)}</dd>`)
        .join("") +
      "</dl>"
    );
  };

  if (state.connected) {
    return {
      key: "ready",
      cls: "b-ok",
      badge: "✓ READY",
      // Scoped to the load, like every other state here: this is one fetch, and
      // it is never revalidated, so the present tense would be a claim about a
      // moment the page has no way of standing behind.
      //
      // The second sentence is about what this build does, not about what is
      // currently on the screen. "Nothing here was written by an agent" is
      // false the moment a reader uses the handover sheet's Run button, and
      // this block is drawn once and never drawn again.
      lines: [
        `${state.deployed.length} of ${state.expected} agents were deployed and ` +
          "reachable when this page loaded.",
        "Nothing on this page is written on an agent's behalf. Where one has not " +
          "been asked, the space is left empty rather than filled in for it.",
      ],
      detail: "",
    };
  }

  if (state.unreadable) {
    return {
      key: "unknown",
      cls: "b-idle",
      badge: "○ CONNECTION UNKNOWN",
      lines: [
        "The workspace server answered the connection check with something this " +
          "page could not read, so whether the deployed agents can be reached is " +
          "not known. This is neither a yes nor a no.",
        "Nothing on this page is written on an agent's behalf either way. The " +
          "check itself is worth reporting to whoever administers this workspace.",
      ],
      detail: rows([
        ["What was asked", "/api/runtime"],
        ["What came back", state.stage],
        ["Why it could not be read", state.detail],
      ]),
    };
  }

  if (state.offline) {
    return {
      key: "not-connected",
      cls: "b-warn",
      badge: "⚠ NOT CONNECTED",
      lines: [
        "These screens are open without the workspace server, so nothing on this " +
          "page has asked the deployed agents anything.",
        state.reason,
        state.consequence,
      ].filter(Boolean),
      detail: "",
    };
  }

  return {
    key: "not-connected",
    cls: "b-warn",
    badge: "⚠ NOT CONNECTED",
    lines: [
      "This workspace could not reach the deployed agents when the page loaded, " +
        "so nothing here has been written by one.",
      "Everything else on the screen — the tables, the method and the counts — " +
        "is read from the deployed catalog and is unaffected. Restoring the " +
        "connection is a job for whoever administers this workspace.",
    ],
    detail: rows([
      ["Where the check stopped", state.stage],
      ["What it reported", state.detail],
    ]),
  };
}

/* The pure half only. mountNav, provenance and el read the document or the
 * bundle global, and exporting them would invite a test to call one and get a
 * DOM error instead of an answer. Everything below is a function of its
 * arguments alone, which is what makes it worth pinning from Node. */
if (typeof module !== "undefined") {
  module.exports = { esc, num, places, fig, rowPlaces, clientInput, technicalDrawer };
}
