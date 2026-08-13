/* Screen 1.3 — what the gap is worth.
 *
 * The order of this screen is the argument, and it was deliberately inverted
 * from an earlier draft that opened with a 52-cell partition. A partition is a
 * proof of tidiness; it answers a question nobody has asked yet. So the price
 * of a recovery point goes first, the six pools that release it go second, and
 * the proof that the six do not overlap goes third — available to a reader who
 * wants it, out of the way of one who has already been convinced.
 *
 * The screen's discipline is that it never states a magnitude it cannot source.
 * One dollar figure in this repository is real. The calculator holds that line
 * by splitting itself in two: what this site's own record settles on the left,
 * what only the client holds on the right, and no arithmetic until the client
 * has typed. A CEO who is shown a number they did not supply stops trusting the
 * screen, and they are right to.
 */

mountNav("case", "value.html");

const tree = DATA.value_tree;
const catalog = DATA.catalog;
const personas = DATA.personas.personas;
const evidence = DATA.signals.branch_evidence;
const GAP = DATA.signals.gap;
const ROI = DATA.signals.roi;
const BENCH = DATA.benchmarks;

/* One hue per branch, used on the partition cell, the key, the card edge and
   the sparkline. The convergence agent takes the neutral, because it is
   deliberately not a seventh branch. Every coloured element also prints its
   code, so nothing on this screen depends on a reader distinguishing hues. */
const HUE = {};
tree.branches.forEach((b, i) => (HUE[b.code] = `var(--b${i + 1})`));
const CONV_HUE = "var(--bx)";

const TOTAL = catalog.counts.entrypoints;
const CONV = tree.convergence.agents;

/* Which measured gap belongs to which pool, and which published finding sits
   beside it. Both maps are deliberately sparse. Two of the six pools have no
   verified third-party benchmark and two have no gap this repository can
   measure, and the cards say so in words rather than leaving a tidy blank —
   the blanks are the honest part of the exhibit. */
const POOL_GAPS = {
  B3: ["recovery", "feed_rate", "conveyor_load"],
  B4: ["payload"],
};
const POOL_BENCH = {
  B1: "discipline_gap",
  B3: "throughput_100_assets",
  B4: "haulage_ahs",
  B5: "procurement",
};

Object.values(POOL_BENCH).forEach((id) => {
  if (!BENCH.by_id[id]) {
    throw new Error(`pool cites benchmark ${id}, which is not in the source file`);
  }
});

const gapRow = (id) => GAP.rows.find((r) => r.id === id);
const RECOVERY = gapRow("recovery");
const RDP = rowPlaces(RECOVERY);
/* The calculator multiplies by the gap the reader can see, not by the full
   float behind it. A panel that prints "1.96 points" and then returns a total
   the reader cannot reach by multiplying is a panel that has to be taken on
   trust, and the whole point of showing the working is that it need not be. */
const GAP_PTS = +RECOVERY.delta.toFixed(RDP);

el("value-lede").textContent =
  "One dollar figure in this repository is real, and it is named where it is " +
  "used. Everything else states exactly how value is released and leaves the " +
  "size of it to the people who hold the volumes, the contracts and the " +
  "tariffs. Where research has published a range for the same mechanism, that " +
  "range is printed beside our measurement and attributed, never merged into it.";

/* ---------- the prize ---------- */

el("roi-lede").textContent =
  "A recovery point is not money until three things are known: how much ore " +
  "goes through the mill, what that ore carries, and what the metal sells for. " +
  "This site's record settles the middle one — " +
  ROI.feed_grade_days +
  " days of concentrator feed assays — and is silent on the other two. So the " +
  "panel below stops exactly there.";

el("roi-known").innerHTML =
  '<div class="known"><span class="v">' +
  esc(fig(ROI.feed_grade_pct, "%")) +
  '</span><span>Copper in the mill feed, the median of ' +
  esc(ROI.feed_grade_days) +
  " days<br><span class=\"dim\" style=\"color:var(--fg-dim);font-size:11.5px\">" +
  esc(ROI.feed_grade_source) +
  "</span></span></div>" +
  '<div class="known"><span class="v">' +
  esc(fig(RECOVERY.delta, "pts", RDP)) +
  '</span><span>Between the ordinary day and the best one<br>' +
  '<span class="dim" style="color:var(--fg-dim);font-size:11.5px">Measured here, ' +
  esc(RECOVERY.days) +
  " days — not a target</span></span></div>" +
  '<div class="known"><span class="v">' +
  esc(fig(ROI.t_per_mt_per_point, "t")) +
  '</span><span>Contained copper per million tonnes milled, ' +
  "for each point of recovery<br>" +
  '<span class="dim" style="color:var(--fg-dim);font-size:11.5px">' +
  esc(ROI.feed_grade_pct) +
  "% × 1% × 1,000,000 t</span></span></div>";

el("roi-inputs").innerHTML =
  "<label>" +
  '<span class="name">Annual mill throughput' +
  '<span class="whose">your figure</span></span>' +
  '<input type="number" id="roi-mt" min="0" step="0.1" inputmode="decimal" ' +
  'placeholder="million tonnes per year">' +
  '<span class="hint">Not in this repository. The files hold one crusher\'s ' +
  "feed rate, which is not a plant figure and will not be presented as one." +
  "</span></label>" +
  "<label>" +
  '<span class="name">Copper price' +
  '<span class="whose">your figure</span></span>' +
  '<input type="number" id="roi-price" min="0" step="100" inputmode="decimal" ' +
  'placeholder="US dollars per tonne">' +
  '<span class="hint">Your realised price, net of your own terms — not a ' +
  "spot quote this screen looked up.</span></label>";

const mtInput = el("roi-mt");
const priceInput = el("roi-price");

function money(v) {
  return (
    "$" +
    v.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 })
  );
}

/* The equation is printed whether or not it can be evaluated. A calculator that
   shows only its answer asks to be trusted; one that shows its working can be
   checked, and this one is meant to be checked. */
function renderRoi() {
  const mt = parseFloat(mtInput.value);
  const price = parseFloat(priceInput.value);
  const eq =
    '<div class="eq">throughput (Mt/yr) × ' +
    esc(fig(ROI.t_per_mt_per_point, "t")) +
    " per Mt per point × " +
    esc(fig(GAP_PTS, "points", RDP)) +
    " × price ($/t)<br>" +
    esc(ROI.basis) +
    "</div>";

  const ok = Number.isFinite(mt) && mt > 0 && Number.isFinite(price) && price > 0;
  if (!ok) {
    el("roi-out").innerHTML =
      clientInput() +
      '<div class="metric-sub">Two figures short of an answer, and this screen ' +
      "will not supply either</div>" +
      eq;
    return;
  }

  const tonnesPerPoint = mt * ROI.t_per_mt_per_point;
  const tonnesAtGap = tonnesPerPoint * GAP_PTS;
  el("roi-out").innerHTML =
    '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));' +
    'gap:20px;margin-bottom:14px">' +
    "<div>" +
    `<div class="metric">${esc(money(tonnesPerPoint * price))}</div>` +
    '<div class="metric-sub">A year, for one point of recovery — ' +
    esc(fig(tonnesPerPoint, "t")) +
    " of contained copper</div></div>" +
    "<div>" +
    // The accent goes on the gap, not on the unit rate: the unit rate is the
    // arithmetic, the gap is the finding.
    `<div class="metric accent">${esc(money(tonnesAtGap * price))}</div>` +
    '<div class="metric-sub">A year, at the ' +
    esc(fig(GAP_PTS, "point", RDP)) +
    " gap this site already reached — " +
    esc(fig(tonnesAtGap, "t")) +
    "</div></div></div>" +
    eq;
}

mtInput.addEventListener("input", renderRoi);
priceInput.addEventListener("input", renderRoi);
renderRoi();

el("roi-note").innerHTML =
  '<div class="note"><strong>What this figure is not</strong><br>' +
  esc(GAP.caveat) +
  " The tonnes above are contained metal: smelter payability and treatment and " +
  "refining charges take a cut for which this repository holds no terms, so the " +
  "money is an upper bound on the concentrate, not a number to put in a board " +
  "paper without your commercial team on it.</div>";

/* ---------- the six pools ---------- */

el("pools-lede").textContent =
  "Each pool states how value is released, what this repository can measure of " +
  "it, and what independent research has published for the same mechanism. " +
  "Where either is missing the pool says so. A pool with a mechanism and no " +
  "measurement is still worth naming; a pool with a number and no mechanism " +
  "would not be.";

/** Round a range label to the precision the instrument plausibly has. The
 *  export keeps four decimals because it is a mean and rounding is the
 *  screen's business; a header reading "3.6429 – 4.5323 MW" claims a mill
 *  power meter resolves to a hundred watts. */
function round(v) {
  // Counts are already exact. "0.00 – 7.00 alerts" invents a fractional alert.
  if (Number.isInteger(v)) return v.toLocaleString("en-US");
  return fig(v);
}

/** The measurement this repository holds for a branch, drawn as what it is.
 *
 *  A series gets a line. A block model gets a distribution, because it is
 *  spatial and has no time axis. A stock level gets a share of its whole,
 *  because it is a position rather than a history. Drawing all three as
 *  sparklines would make five identical cards and two false claims.
 */
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

/** The gap rows this pool acts on, ordinary day to best day. */
function measuredBlock(code) {
  const ids = POOL_GAPS[code];
  if (!ids) {
    return (
      '<div class="pool-measured"><div class="row" style="color:var(--fg-dim)">' +
      "<span>No day-to-day gap this repository can measure</span>" +
      '<span class="move"></span><span class="up">—</span></div></div>'
    );
  }
  return (
    '<div class="pool-measured">' +
    ids
      .map((id) => {
        const r = gapRow(id);
        const dp = rowPlaces(r);
        const up =
          r.delta_kind === "points"
            ? `+${fig(r.delta, "pts", dp)}`
            : `+${fig(r.delta_pct, "%", 1)}`;
        return (
          '<div class="row">' +
          `<span>${esc(r.label)}${r.asset_id ? ` · ${esc(r.asset_id)}` : ""}</span>` +
          `<span class="move">${esc(fig(r.median, "", dp))} → ${esc(
            fig(r.p90, r.unit, dp)
          )}</span>` +
          `<span class="up">${esc(up)}</span></div>`
        );
      })
      .join("") +
    "</div>"
  );
}

/** What somebody other than us has published about the same mechanism. */
function benchBlock(code) {
  const b = BENCH.by_id[POOL_BENCH[code]];
  if (!b) {
    return (
      '<div class="benchline none">No verified benchmark held for this pool</div>'
    );
  }
  return (
    '<div class="benchline">' +
    `<span class="claim">${esc(b.headline)}</span>` +
    `<span class="cite">${esc(b.publisher)}, ${esc(b.year)}</span></div>`
  );
}

/* Each pool states its mechanism and then, deliberately, refuses to state a
   magnitude it cannot source. B1 is the exception: the mill downtime rate is
   the one figure this repository establishes. */
el("detail").innerHTML = tree.branches
  .map((b, i) => {
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
      // The counter, not the branch code. It says the set is closed, which is
      // the one thing about the partition worth carrying this far up.
      `<div class="card-cap">Pool ${esc(i + 1)} of ${esc(tree.branches.length)}</div>` +
      `<h3 style="margin-top:0">${esc(b.title)}</h3>` +
      `<p style="color:var(--fg-muted);margin-top:0">${esc(b.mechanism)}</p>` +
      '<div style="border-top:1px solid var(--border);padding-top:12px;margin-top:12px">' +
      magnitude +
      "</div>" +
      measuredBlock(b.code) +
      benchBlock(b.code) +
      evidenceBlock(b.code, hue) +
      // The pool's place in the estate, kept to a footnote. A reader deciding
      // whether the mechanism is real is not helped by an entrypoint count.
      `<div class="mono" style="font-size:10.5px;color:var(--fg-dim);margin-top:12px;` +
      `text-transform:uppercase;letter-spacing:.06em">${esc(b.code)} · APQC ${esc(
        b.apqc
      )} · ${esc(b.count)} entry points<br>${who}</div>` +
      "</div>"
    );
  })
  .join("");

/* ---------- the partition, demoted ---------- */

el("mece-lede").textContent =
  "The six pools above hold " +
  tree.branches.map((b) => b.count).join(", ") +
  " of the estate's entry points. " +
  CONV.join(", ") +
  ", the convergence agent, holds the remaining " +
  CONV.length +
  ". That is " +
  TOTAL +
  " with no overlap and no remainder — the build will not emit a value tree " +
  "whose branches fail to reconcile against the catalog that deploys them, so " +
  "the claim is enforced upstream rather than asserted by this copy.";

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
  `<span class="metric-sub" style="margin:0">of ${esc(TOTAL)} entry points placed</span>` +
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
  ` Held by ${esc(CONV.join(", "))}. It is the entry point that stands alone, ` +
  "and the one cell above that is not a pool colour.</div>";

/* ---------- the process view, which deliberately does not partition ---------- */

const apqcTotal = Object.values(catalog.by_apqc_code).reduce(
  (sum, info) => sum + info.count,
  0
);

el("apqc-lede").textContent =
  "The same " +
  TOTAL +
  " entry points, grouped by the process framework a mining client already runs " +
  "their operating model against. This cut is not a partition and is not meant " +
  "to be: " +
  catalog.compound_apqc_codes.length +
  " entry points carry a compound code because the work genuinely spans two " +
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

const citedBench = Object.values(POOL_BENCH)
  .filter((id, i, all) => all.indexOf(id) === i)
  .map((id) => {
    const b = BENCH.by_id[id];
    return `${b.title} (${b.publisher}, ${b.year})`;
  })
  .join("; ");

el("prov").innerHTML = provenance(
  `<dt>Value tree</dt><dd>${esc(tree.root_source)}, rooted on ${esc(tree.root)}.</dd>` +
    `<dt>The calculation</dt><dd>Feed grade is the median of ${esc(
      ROI.feed_grade_days
    )} days in ${esc(ROI.feed_grade_source)}. ${esc(GAP.method)} ${esc(
      ROI.basis
    )} Throughput and price are entered by the reader and are never defaulted.</dd>` +
    `<dt>Benchmarks</dt><dd>${esc(citedBench)}. Held in ${esc(
      BENCH.source
    )} with a URL per figure; ${esc(
      BENCH.excluded.length
    )} further figures were found and are recorded there as unverifiable rather ` +
    "than printed.</dd>" +
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
