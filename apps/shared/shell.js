/* Shared chrome and helpers for both applications.
 *
 * The data arrives as window.MINING_DATA from data/bundle.js, which is a
 * script tag rather than a fetch so the screens also work when opened straight
 * off disk. Everything here reads that object; nothing here holds a figure of
 * its own, because a helper with a hardcoded count is how a screen starts
 * disagreeing with the catalog it claims to describe.
 */

const DATA = window.MINING_DATA;
if (!DATA) {
  document.addEventListener("DOMContentLoaded", () => {
    document.body.innerHTML =
      '<div class="wrap"><div class="note"><strong>Data missing</strong><br>' +
      "data/bundle.js did not load. Run <code>python -m scripts.build_app_data</code>." +
      "</div></div>";
  });
}

const CASE_NAV = [
  { href: "index.html", label: "1 · Proposition" },
  { href: "scenario.html", label: "2 · The mine today" },
  { href: "value.html", label: "3 · Value unlock" },
  { href: "solution.html", label: "4 · The solution" },
  { href: "graph.html", label: "5 · The graph" },
];

/* Application 2. The four destinations are the four standing screens; SC-4,
   the approval sheet, is deliberately absent because it is a modal raised from
   a swarm or a workbench and never a place you navigate to on its own. */
const WORK_NAV = [
  { href: "index.html", label: "Cockpit" },
  { href: "swarm.html", label: "Swarms" },
  { href: "workbench.html", label: "Workbench" },
  { href: "handover.html", label: "Handover" },
];

const NAVS = {
  case: { items: CASE_NAV, brand: "Mining Agents · The case for change" },
  workspace: { items: WORK_NAV, brand: "Mining Agents · Site workspace" },
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
  const bar = document.createElement("div");
  bar.className = "topbar";
  bar.innerHTML =
    `<span class="brand">${esc(nav.brand)}</span>` +
    `<nav>${links}</nav>` +
    '<span style="flex:1"></span>' +
    `<span class="pill" title="Source of every figure on this page">${esc(
      DATA.catalog.counts.entrypoints
    )} entrypoints · ${esc(DATA.catalog.counts.agent_nodes)} agents</span>`;
  document.body.prepend(bar);
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
