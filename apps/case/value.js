/* Screen 1.3 — value unlock. The screen where the discipline shows. */

mountNav("case", "value.html");

const tree = DATA.value_tree;
const catalog = DATA.catalog;
const personas = DATA.personas.personas;

const widest = Math.max(...tree.branches.map((b) => b.count));

el("branches").innerHTML =
  `<div style="margin-bottom:14px;color:var(--fg-muted)">Root: <b style="color:var(--fg)">${esc(
    tree.root
  )}</b> — the metric a mining CEO is actually measured on, and the only root wide enough to hold all six branches without one of them going homeless.</div>` +
  tree.branches
    .map(
      (b) =>
        '<div class="bar-row">' +
        `<div class="name">${esc(b.code)} · ${esc(b.title)}</div>` +
        `<div class="bar"><span style="width:${(b.count / widest) * 100}%"></span></div>` +
        `<div class="n">${esc(b.count)}</div>` +
        "</div>"
    )
    .join("") +
  '<div class="note info" style="margin-top:16px"><strong>The convergence layer</strong><br>' +
  esc(tree.convergence.note) +
  ` Held by ${esc(tree.convergence.agents.join(", "))}. Six branches plus that one ` +
  `entry point reconcile to ${esc(catalog.counts.entrypoints)}.</div>`;

/* Each branch states its mechanism and then, deliberately, refuses to state a
   magnitude it cannot source. B1 is the exception: the mill downtime rate is
   the one figure this repository establishes. */
el("detail").innerHTML = tree.branches
  .map((b) => {
    const magnitude = b.anchored
      ? `<div class="metric accent">$${DATA.facts.mill_downtime_usd_per_hour.toLocaleString(
          "en-US"
        )}</div><div class="metric-sub">Per hour of mill downtime</div>`
      : clientInput() +
        '<div class="metric-sub">Baseline not held in this repository</div>';

    const who = b.personas
      .map((c) => `${esc(c)} ${esc(personas[c] ? personas[c].title : "")}`)
      .join(" · ");

    return (
      '<div class="card c6">' +
      `<div class="card-cap">${esc(b.code)} · APQC ${esc(b.apqc)}</div>` +
      `<h3 style="margin-top:0">${esc(b.title)}</h3>` +
      `<p style="color:var(--fg-muted);margin-top:0">${esc(b.mechanism)}</p>` +
      '<div style="border-top:1px solid var(--border);padding-top:12px;margin-top:12px">' +
      magnitude +
      "</div>" +
      `<div class="mono" style="font-size:10.5px;color:var(--fg-dim);margin-top:12px;text-transform:uppercase;letter-spacing:.06em">${esc(
        b.count
      )} entry points · ${who}</div>` +
      "</div>"
    );
  })
  .join("");

/* Rolled up to the atomic process code. The literal code strings include seven
   compound codes, so a table keyed on them shows a dash where a process name
   belongs and splits one process across several rows. An agent spanning two
   domains appears under both, which is why these counts sum above 52. */
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
  "processes and are counted under both, so the column above sums above " +
  `${esc(catalog.counts.entrypoints)}. The catalog also spells some pairs in either ` +
  "order — " +
  catalog.compound_apqc_codes
    .map((c) => `<span class="mono">${esc(c)}</span>`)
    .join(", ") +
  " — which is a catalog tidy-up, not a modelling difference." +
  "</div>";

el("prov").innerHTML = provenance(
  `<dt>Value tree</dt><dd>${esc(tree.root_source)}</dd>` +
    "<dt>Correction</dt><dd>That document's branch table gives Branch 6 a count of 10 while " +
    "listing 9 entry points, which absorbs S12 into a branch its own prose places above all " +
    "six. The catalog settles it: safety holds 9, S12 stands alone. The build refuses to emit " +
    "a tree whose branches do not reconcile to the catalog.</dd>"
);
