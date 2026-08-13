/* The front door. Two cards, and every figure on both read off the catalog.
 *
 * There is no navigation bar here on purpose: this page is a fork in the road
 * and the two applications each own their own chrome. A third nav would imply a
 * place above them that a reader can return to, and there is nothing there.
 *
 * Above the fork sits the site itself — five real machines replayed through the
 * window the telemetry table actually covers. It is there because a reader who
 * is asked to choose a door should first know there is something behind it.
 */

const C = DATA.catalog.counts;
const HITL = DATA.catalog.agents.filter((a) => a.is_entrypoint && a.hitl_required).length;
const SIG = DATA.signals;

/* ---------- the recorded-window strip ---------- */

/* Criticality comes off the asset graph, which is the same record the blast
   radius traversal reads. It is shown as a badge and not as the colour of the
   trace: a criticality rating is a standing property of the machine, and
   drawing three of five traces in the alarm colour would say those three
   machines are in trouble right now, which none of these readings claim. The
   six-hue palette is likewise not used here — those hues are bound to value
   branches, and a branch is not what this row is about. */
const ASSET_META = {};
DATA.graph.nodes.forEach((n) => {
  if (n.type === "Asset" && n.graph === "asset") ASSET_META[n.id] = n.detail;
});
const RATING = { CRITICAL: "b-crit", HIGH: "b-warn", MEDIUM: "b-info", LOW: "b-idle" };

/** Decimals that suit the magnitude. A payload of 172.4831 t is false
 *  precision on a truck scale; a vibration of 5 Hz has thrown away the reading. */
function places(max) {
  if (max >= 100) return 0;
  if (max >= 10) return 1;
  return 2;
}

const FROM = new Date(SIG.window.from.replace(" ", "T"));
const TO = new Date(SIG.window.to.replace(" ", "T"));
const STEPS = SIG.buckets;

function stamp(i) {
  const at = new Date(FROM.getTime() + ((TO - FROM) * i) / (STEPS - 1));
  return at.toISOString().slice(0, 10);
}

el("strip-lede").textContent =
  "Every reading below is in this repository. The window runs " +
  stamp(0) +
  " to " +
  stamp(STEPS - 1) +
  ", reduced to " +
  STEPS +
  " points of equal duration. It is recorded history on a scrubber, not a live " +
  "feed — drag it and the five figures move to what those machines actually read.";

el("scrub").innerHTML =
  "<span>Recorded window</span>" +
  `<span class="mono">${esc(stamp(0))}</span>` +
  `<input type="range" id="play" min="0" max="${STEPS - 1}" value="0" ` +
  'aria-label="Scrub the recorded telemetry window">' +
  `<span class="mono">${esc(stamp(STEPS - 1))}</span>` +
  '<span>At <span class="at" id="at"></span></span>';

el("strip").innerHTML = SIG.assets
  .map((a) => {
    const meta = ASSET_META[a.asset_id] || {};
    const rating = meta.criticality
      ? `<span class="badge ${RATING[meta.criticality] || "b-idle"}">${esc(
          meta.criticality
        )}</span>`
      : '<span class="badge b-idle">rating not held locally</span>';
    return (
      '<div class="card asset reveal">' +
      '<div style="display:flex;gap:8px;align-items:center;justify-content:space-between">' +
      `<span class="who">${esc(a.asset_id)}</span>${rating}</div>` +
      `<div class="val"><span id="v-${esc(a.asset_id)}">—</span>` +
      `<span class="u">${esc(a.unit)}</span></div>` +
      `<div class="what">${esc(a.label)}</div>` +
      `<div class="plot"><div id="p-${esc(a.asset_id)}" class="playhead" style="left:0"></div>` +
      // 46px rather than the 34 a branch card uses: these are 2-hourly sensor
      // readings and they are genuinely noisy, and at 34 the noise collapses
      // into a smudge that reads as texture instead of as a signal.
      sparkline(a.points, { height: 46, label: a.asset_id + " " + a.metric }) +
      "</div>" +
      `<div class="what" style="text-transform:none;letter-spacing:0;margin-top:8px">${esc(
        meta.name || ""
      )}</div>` +
      "</div>"
    );
  })
  .join("");

const VALUE_NODES = SIG.assets.map((a) => ({
  asset: a,
  value: el("v-" + a.asset_id),
  head: el("p-" + a.asset_id),
  decimals: places(a.max),
}));

function showFrame(i) {
  el("at").textContent = stamp(i);
  const left = (i / (STEPS - 1)) * 100;
  VALUE_NODES.forEach((n) => {
    const v = n.asset.points[i];
    n.head.style.left = left + "%";
    n.value.textContent =
      v === null || v === undefined
        ? "—"
        : v.toLocaleString("en-US", {
            minimumFractionDigits: n.decimals,
            maximumFractionDigits: n.decimals,
          });
  });
}

/* Plays through once and stops, then the reader owns it. setInterval rather
   than requestAnimationFrame for the reason motion.js gives; a slider input
   cancels the playback rather than fighting it. */
const play = el("play");
let frame = 0;
showFrame(0);

const reduced =
  window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

let sweep = null;
if (reduced) {
  play.value = String(STEPS - 1);
  showFrame(STEPS - 1);
} else {
  sweep = window.setInterval(() => {
    frame += 1;
    if (frame >= STEPS) {
      window.clearInterval(sweep);
      sweep = null;
      return;
    }
    play.value = String(frame);
    showFrame(frame);
  }, 90);
}

play.addEventListener("input", () => {
  if (sweep) {
    window.clearInterval(sweep);
    sweep = null;
  }
  showFrame(Number(play.value));
});

/* ---------- the two doors ---------- */

const APPS = [
  {
    href: "case/index.html",
    eyebrow: "Application 1 · five screens",
    title: "The case for change",
    lede:
      "Why the estate is worth building, told in the order a decision is made: " +
      "the proposition, the mine as this demo holds it, where the value is " +
      "unlocked, how the answer is assembled, and the property graph the " +
      "traversals actually run over.",
    facts: [
      [C.agent_nodes, "agent nodes", "counted from the module that builds them"],
      [
        DATA.value_tree.branches.length,
        "value branches",
        "rooted on all-in sustaining cost per tonne",
      ],
      [
        Object.keys(DATA.graph.graphs).length,
        "property graphs",
        "drawn, traversable, with the SQL on screen",
      ],
    ],
    cta: "Read the case",
  },
  {
    href: "workspace/index.html",
    eyebrow: "Application 2 · five screens",
    title: "The site workspace",
    lede:
      "What a person does with the estate once it exists: find the right " +
      "entrypoint out of " +
      C.entrypoints +
      ", see how a swarm is wired, work the entrypoints one role is " +
      "accountable for, approve what cannot act alone, and read the handover " +
      "at shift change.",
    facts: [
      [C.entrypoints, "callable entrypoints", "of the " + C.agent_nodes + " nodes"],
      [HITL, "need a human", "bound to request_approval by the catalog"],
      [
        C.swarms,
        "swarms of five",
        "a coordinator, specialists and a critic — one console each",
      ],
    ],
    cta: "Open the workspace",
  },
];

el("apps").innerHTML = APPS.map(
  (a) =>
    '<div class="card c6 lift reveal">' +
    `<div class="card-cap">${esc(a.eyebrow)}</div>` +
    `<h2 style="margin:0 0 8px">${esc(a.title)}</h2>` +
    `<p style="font-size:14px;margin:0 0 16px">${esc(a.lede)}</p>` +
    a.facts
      .map(
        ([n, label, sub]) =>
          '<div style="display:flex;gap:12px;align-items:baseline;padding:8px 0;' +
          'border-top:1px solid var(--border-soft)">' +
          `<span class="metric" style="font-size:22px;min-width:2.5ch;text-align:right" ` +
          `data-count="${esc(n)}"></span>` +
          `<span style="font-size:13px"><b>${esc(label)}</b><br>` +
          `<span class="dim" style="color:var(--fg-dim)">${esc(sub)}</span></span></div>`
      )
      .join("") +
    '<div class="btn-row" style="margin-top:16px">' +
    `<a class="btn primary" href="${a.href}">${esc(a.cta)}</a></div>` +
    "</div>"
).join("");

el("prov").innerHTML = provenance(
  "<dt>Applications</dt><dd>Both read one bundle; neither holds a figure of its own.</dd>" +
    `<dt>Signals</dt><dd>${esc(SIG.source)}, reduced at build time to ${esc(
      SIG.buckets
    )} points per series.</dd>`
);

reveal();
countAll();
