/* Screen 1.3 — value unlock. The screen where the discipline shows.
 *
 * Its argument is a partition. Six branches and one convergence agent account
 * for all 52 entrypoints with nothing counted twice and nothing left over, and
 * the build refuses to emit a tree that does not reconcile — so the claim is
 * enforced upstream rather than asserted by this copy. The APQC table below is
 * the same 52 cut a second way, and that cut deliberately overlaps. Showing
 * both, and naming which is which, is the point of the screen: a reader given
 * one exhaustive view and one overlapping view, each labelled, learns more than
 * a reader given one tidy chart.
 */

mountNav("case", "value.html");

const tree = DATA.value_tree;
const catalog = DATA.catalog;
const personas = DATA.personas.personas;
const evidence = DATA.signals.branch_evidence;

/* One hue per branch, used on the partition cell, the key, the card edge and
   the sparkline. The convergence agent takes the neutral, because it is
   deliberately not a seventh branch. Every coloured element also prints its
   code, so nothing on this screen depends on a reader distinguishing hues. */
const HUE = {};
tree.branches.forEach((b, i) => (HUE[b.code] = `var(--b${i + 1})`));
const CONV_HUE = "var(--bx)";

const TOTAL = catalog.counts.entrypoints;
const CONV = tree.convergence.agents;

el("mece-lede").textContent =
  "The six branches hold " +
  tree.branches.map((b) => b.count).join(", ") +
  " entrypoints. " +
  CONV.join(", ") +
  ", the convergence agent, holds the remaining " +
  CONV.length +
  ". That is " +
  TOTAL +
  " with no overlap and no remainder — the build will not emit a tree whose " +
  "branches fail to reconcile against the catalog that deploys them.";

/* ---------- the partition strip ---------- */

const CELLS = [];
tree.branches.forEach((b) => {
  for (let i = 0; i < b.count; i += 1) CELLS.push({ code: b.code, hue: HUE[b.code] });
});
CONV.forEach((id) => CELLS.push({ code: id, hue: CONV_HUE }));

if (CELLS.length !== TOTAL) {
  throw new Error(
    `the partition drew ${CELLS.length} cells for ${TOTAL} entrypoints; ` +
      "the bundle's value tree and catalog disagree"
  );
}

el("partition").innerHTML = CELLS.map(
  (c, i) =>
    `<div class="cell" data-i="${i}" style="--hue:${c.hue}" ` +
    `title="${esc(c.code)}"></div>`
).join("");

el("mece-key").innerHTML =
  tree.branches
    .map(
      (b) =>
        '<div class="row">' +
        `<span class="chip" style="--hue:${HUE[b.code]}"></span>` +
        `<span><b>${esc(b.code)}</b> ${esc(b.title)}</span>` +
        `<span class="n">${esc(b.count)}</span></div>`
    )
    .join("") +
  '<div class="row">' +
  `<span class="chip" style="--hue:${CONV_HUE}"></span>` +
  `<span><b>${esc(CONV.join(", "))}</b> Convergence — above the six</span>` +
  `<span class="n">${esc(CONV.length)}</span></div>`;

el("mece-sum").innerHTML =
  '<div style="display:flex;align-items:baseline;gap:10px;flex-wrap:wrap">' +
  '<span class="metric" id="running">0</span>' +
  `<span class="metric-sub" style="margin:0">of ${esc(TOTAL)} entrypoints placed</span>` +
  "</div>" +
  '<div class="mono" style="font-size:12px;margin-top:10px;color:var(--fg-muted)">' +
  tree.branches
    .map((b) => `<span style="color:${HUE[b.code]}">${esc(b.count)}</span>`)
    .join(" + ") +
  ` + <span style="color:${CONV_HUE}">${esc(CONV.length)}</span> = ` +
  `<b style="color:var(--fg)">${esc(TOTAL)}</b></div>`;

/* Cells fill in branch order while the total counts with them, so the reader
   watches the partition being assembled rather than being told it adds up.
   setInterval, not requestAnimationFrame: rAF does not fire in a hidden
   document, which is every browser this screen is checked in. */
const cellNodes = Array.from(el("partition").querySelectorAll(".cell"));
const running = el("running");
const reduced =
  window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (reduced) {
  cellNodes.forEach((n) => n.classList.add("on"));
  running.textContent = String(TOTAL);
} else {
  let filled = 0;
  const fill = window.setInterval(() => {
    cellNodes[filled].classList.add("on");
    filled += 1;
    running.textContent = String(filled);
    if (filled >= cellNodes.length) window.clearInterval(fill);
  }, 26);
}

el("convergence").innerHTML =
  '<div class="note info"><strong>The convergence layer</strong><br>' +
  esc(tree.convergence.note) +
  ` Held by ${esc(CONV.join(", "))}. It is the 52nd entrypoint and the one cell ` +
  "above that is not a branch colour.</div>";

/* ---------- branch cards ---------- */

/** The measurement this repository holds for a branch, drawn as what it is.
 *
 *  A series gets a line. A block model gets a distribution, because it is
 *  spatial and has no time axis. A stock level gets a share of its whole,
 *  because it is a position rather than a history. Drawing all three as
 *  sparklines would make five identical cards and two false claims.
 */
/** Round a range label to the precision the instrument plausibly has. The
 *  export keeps four decimals because it is a mean and rounding is the
 *  screen's business; a header reading "3.6429 – 4.5323 MW" claims a mill
 *  power meter resolves to a hundred watts. */
function round(v) {
  // Counts are already exact. "0.00 – 7.00 alerts" invents a fractional alert.
  if (Number.isInteger(v)) return v.toLocaleString("en-US");
  const step = Math.abs(v) >= 100 ? 0 : Math.abs(v) >= 10 ? 1 : 2;
  return v.toLocaleString("en-US", {
    minimumFractionDigits: step,
    maximumFractionDigits: step,
  });
}

function evidenceBlock(code, hue) {
  const e = evidence[code];
  if (!e) return "";
  const head = (left, right) =>
    `<div class="head"><span>${esc(left)}</span><span>${esc(right)}</span></div>`;
  const foot =
    `<div class="cap">${esc(e.caption)}</div>` +
    `<div class="src">${esc(e.source)}</div>`;

  let body = "";
  if (e.kind === "series") {
    body =
      head(e.label, `${round(e.min)} – ${round(e.max)} ${e.unit}`) +
      sparkline(e.points, { colour: hue, label: e.label });
  } else if (e.kind === "distribution") {
    const tallest = Math.max(...e.bins);
    body =
      head(
        e.label,
        `${round(e.edges[0])} – ${round(e.edges[e.edges.length - 1])} ${e.unit}`
      ) +
      '<div class="dist reveal">' +
      e.bins
        .map(
          (n) =>
            `<span style="--hue:${hue};height:${((n / tallest) * 100).toFixed(1)}%" ` +
            `title="${esc(n)} blocks"></span>`
        )
        .join("") +
      "</div>";
  } else if (e.kind === "share") {
    body =
      head(e.label, `${e.part} of ${e.whole}`) +
      `<div class="share"><span data-share="${((e.part / e.whole) * 100).toFixed(
        2
      )}" style="--hue:${hue}"></span></div>`;
  }
  return `<div class="evidence">${body}${foot}</div>`;
}

/* Each branch states its mechanism and then, deliberately, refuses to state a
   magnitude it cannot source. B1 is the exception: the mill downtime rate is
   the one figure this repository establishes. */
el("detail").innerHTML = tree.branches
  .map((b) => {
    const hue = HUE[b.code];
    const magnitude = b.anchored
      ? `<div class="metric accent" data-count="${DATA.facts.mill_downtime_usd_per_hour}" ` +
        'data-prefix="$"></div><div class="metric-sub">Per hour of mill downtime</div>'
      : clientInput() +
        '<div class="metric-sub">Baseline not held in this repository</div>';

    const who = b.personas
      .map((c) => `${esc(c)} ${esc(personas[c] ? personas[c].title : "")}`)
      .join(" · ");

    return (
      `<div class="card c6 branch reveal" style="--hue:${hue}">` +
      `<div class="card-cap">${esc(b.code)} · APQC ${esc(b.apqc)} · ${esc(
        b.count
      )} entry points</div>` +
      `<h3 style="margin-top:0">${esc(b.title)}</h3>` +
      `<p style="color:var(--fg-muted);margin-top:0">${esc(b.mechanism)}</p>` +
      '<div style="border-top:1px solid var(--border);padding-top:12px;margin-top:12px">' +
      magnitude +
      "</div>" +
      evidenceBlock(b.code, hue) +
      `<div class="mono" style="font-size:10.5px;color:var(--fg-dim);margin-top:12px;` +
      `text-transform:uppercase;letter-spacing:.06em">${who}</div>` +
      "</div>"
    );
  })
  .join("");

/* ---------- the process view, which deliberately does not partition ---------- */

const apqcTotal = Object.values(catalog.by_apqc_code).reduce(
  (sum, info) => sum + info.count,
  0
);

el("apqc-lede").textContent =
  "The same " +
  TOTAL +
  " entrypoints, grouped by the process framework a mining client already runs " +
  "their operating model against. This cut is not a partition and is not meant " +
  "to be: " +
  catalog.compound_apqc_codes.length +
  " entrypoints carry a compound code because the work genuinely spans two " +
  "domains, and each is counted under both. The column below therefore sums to " +
  apqcTotal +
  ", not " +
  TOTAL +
  ". A framework a client already owns is worth mapping onto even when it " +
  "overlaps; what is not worth doing is hiding that it does.";

el("apqc").innerHTML = Object.entries(catalog.by_apqc_code)
  .map(
    ([code, info]) =>
      "<tr>" +
      `<td class="mono">${esc(code)}</td>` +
      `<td>${esc(catalog.apqc_names[code] || "Unnamed in this catalog")}</td>` +
      `<td class="num">${esc(info.count)}</td>` +
      `<td class="mono" style="font-size:11px;color:var(--fg-muted)">${esc(
        info.agents.join(" ")
      )}</td>` +
      "</tr>"
  )
  .join("");

el("apqc-note").innerHTML =
  '<div class="note"><strong>Compound codes</strong><br>' +
  `${esc(catalog.compound_apqc_codes.length)} entry points carry a code spanning two ` +
  "processes and are counted under both, so the column above sums to " +
  `${esc(apqcTotal)} against ${esc(TOTAL)} entry points. The catalog also spells ` +
  "some pairs in either order — " +
  catalog.compound_apqc_codes
    .map((c) => `<span class="mono">${esc(c)}</span>`)
    .join(", ") +
  " — which is a catalog tidy-up, not a modelling difference." +
  "</div>";

el("prov").innerHTML = provenance(
  `<dt>Value tree</dt><dd>${esc(tree.root_source)}, rooted on ${esc(tree.root)}.</dd>` +
    `<dt>Evidence</dt><dd>${esc(DATA.signals.source)}, reduced at build time to ${esc(
      DATA.signals.buckets
    )} points per series. Each card names its own file.</dd>` +
    "<dt>Correction</dt><dd>That document's branch table gives Branch 6 a count of 10 while " +
    "listing 9 entry points, which absorbs S12 into a branch its own prose places above all " +
    "six. The catalog settles it: safety holds 9, S12 stands alone. The build refuses to emit " +
    "a tree whose branches do not reconcile to the catalog.</dd>"
);

reveal();
countAll();

/* The share bar grows from zero once it is in the document — the comparison is
   17 against 105, and a bar that is already full when the reader arrives has
   made that comparison for them. */
Array.from(document.querySelectorAll("[data-share]")).forEach((node) => {
  const to = node.getAttribute("data-share") + "%";
  if (reduced) node.style.width = to;
  else window.setTimeout(() => (node.style.width = to), 300);
});
