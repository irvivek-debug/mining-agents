/* Screen 1.2 — the mine as the demo holds it. */

mountNav("case", "scenario.html");

const facts = DATA.facts;

el("site").innerHTML = facts.site
  .map(
    (row) =>
      "<tr>" +
      `<td>${esc(row.label)}</td>` +
      `<td class="num">${num(row.value)}</td>` +
      `<td style="color:var(--fg-muted)">${esc(row.unit)}</td>` +
      `<td class="mono" style="color:var(--fg-dim);font-size:11px">${esc(row.source)}</td>` +
      "</tr>"
  )
  .join("");

el("window").innerHTML =
  '<div class="note info"><strong>Observation window</strong><br>' +
  `Telemetry runs ${esc(facts.window.from)} to ${esc(facts.window.to)}. ` +
  "Every trend an agent reports is bounded by that window, so a question about " +
  "last week is answerable and a question about last year is not." +
  "</div>";

/* The figures the local files cannot settle get their own block. Leaving them
   off the screen entirely would be the quieter choice and the worse one: the
   audience would have no way to know the table above is partial. */
el("unknown").innerHTML = facts.not_locally_derivable.length
  ? '<div class="note"><strong>Not derivable from local files</strong><br>' +
    facts.not_locally_derivable
      .map((u) => `<b>${esc(u.figure)}.</b> ${esc(u.why)}`)
      .join("<br>") +
    "</div>"
  : "";

/* Personas in catalog order, sized by how many agents answer to them, because
   the ordering is itself a claim about where the work is. */
const personas = Object.values(DATA.personas.personas).sort(
  (a, b) => b.agent_count - a.agent_count || a.code.localeCompare(b.code)
);

el("pain").innerHTML = personas
  .map(
    (p) =>
      '<div class="card c6">' +
      '<div class="card-cap">' +
      `${esc(p.code)} · ${esc(p.title)}` +
      `<span style="float:right;color:var(--fg-dim)">${esc(p.agent_count)} agent${
        p.agent_count === 1 ? "" : "s"
      }</span>` +
      "</div>" +
      p.pain_points
        .map(
          (q) =>
            '<blockquote class="verbatim">' +
            esc(q.quote) +
            `<cite>personas-and-value-tree.md:${esc(q.source_line)}</cite>` +
            "</blockquote>"
        )
        .join("") +
      "</div>"
  )
  .join("");

el("prov").innerHTML = provenance(
  `<dt>Personas</dt><dd>${esc(DATA.personas.source)}</dd>` +
    `<dt>Site figures</dt><dd class="mono">${esc(facts.generated_at)}</dd>`
);
