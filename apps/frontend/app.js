/* Agentic AI Mining — five-screen front end.
 *
 * WHY THIS FILE IS NAMESPACED
 * The two handover files each defined switchScreen, inspectNode, selectPersona,
 * initParticleCanvas, copyAgentUrn and fallbackCopyText — six names, two
 * different bodies each. Concatenating them would have let the second
 * definition silently win, and the failure mode is a screen that renders but
 * behaves as though it belongs to the other file. Each screen therefore owns a
 * closure (S1..S5) and exposes only what the router calls. Nothing is global
 * except App.
 *
 * The markup carries no inline onclick. Every binding is attached here, so a
 * renamed function fails loudly at wire-up instead of quietly at click time.
 */
(function () {
  "use strict";

  var SCREENS = ["macro", "schematic", "personas", "ecosystem", "governance"];

  function el(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }
  function on(id, evt, fn) { var e = el(id); if (e) e.addEventListener(evt, fn); }

  /* ------------------------------------------------------------- clipboard */
  var Clip = (function () {
    function toast(text) {
      var t = el("copy-toast");
      if (!t) return;
      t.textContent = text;
      t.style.display = "block";
      setTimeout(function () { t.style.display = "none"; }, 2200);
    }
    function fallback(text) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.cssText = "position:fixed;top:0;left:0;width:2em;height:2em;border:none;background:transparent;";
      document.body.appendChild(ta);
      ta.focus(); ta.select();
      try { document.execCommand("copy"); } catch (e) { /* clipboard unavailable */ }
      document.body.removeChild(ta);
    }
    return {
      copy: function (text, btn) {
        if (!text) return;
        var span = btn && btn.querySelector("span");
        if (span) {
          var prev = span.textContent;
          span.textContent = "Copied";
          setTimeout(function () { span.textContent = prev; }, 1600);
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text)
            .then(function () { toast("Copied: " + text); })
            .catch(function () { fallback(text); toast("Copied: " + text); });
        } else {
          fallback(text); toast("Copied: " + text);
        }
      }
    };
  })();

  /* =========================================================== S1 — Macro */
  var S1 = (function () {
    var HEADWINDS = [
      { label: "ORE GRADE DECAY",      val: "0.48%", cmp: "0.82%", unit: null,   desc: "Industry average decline over 10 years", fill: 45 },
      { label: "SPECIFIC ENERGY",      val: "18.4",  cmp: null,    unit: "kWh/t", desc: "Up from 12 kWh/t baseline",              fill: 82 },
      { label: "DEMURRAGE PENALTIES",  val: "$24M",  cmp: null,    unit: "YTD",   desc: "Port bottleneck inefficiencies",         fill: 68 }
    ];
    var LEVERS = [
      { tag: "CAPEX DISCIPLINE",       desc: "Marginal returns diminishing",   fill: 90, status: "EXHAUSTED" },
      { tag: "VENDOR SQUEEZE",         desc: "Contractual floors reached",     fill: 85, status: "EXHAUSTED" },
      { tag: "HEADCOUNT FREEZES",      desc: "Impacting operational safety",   fill: 95, status: "HARD CEILING" },
      { tag: "AGENTIC DECISION LAYER", desc: "Software-defined optimization",  fill: 100, status: "HIGH GROWTH", extra: "UNCAPPED", highlight: true }
    ];
    var OUTCOMES = [
      { label: "THROUGHPUT UPLIFT",   val: "2-5%",  sub: "Mine-to-market volume" },
      { label: "MAINTENANCE OPEX",    val: "5-15%", sub: "Cost reduction run-rate" },
      { label: "OUTBOUND SCHEDULING", val: "2x",    sub: "Productivity multiplier" },
      { label: "EBITDA IMPACT",       val: "2-4%",  sub: "Percentage point gain" }
    ];

    function render() {
      el("s1-headwinds").innerHTML = HEADWINDS.map(function (h) {
        var right = h.cmp
          ? '<span class="headwind-baseline">' + esc(h.cmp) + "</span>"
          : '<span class="headwind-unit">' + esc(h.unit) + "</span>";
        return '<div class="headwind-card">' +
          '<div class="headwind-header"><span>' + esc(h.label) + "</span>" +
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#D93025" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>' +
          "</div>" +
          '<div class="headwind-val-row"><span class="headwind-val">' + esc(h.val) + "</span>" + right + "</div>" +
          '<div class="headwind-desc">' + esc(h.desc) + "</div>" +
          '<div class="red-bar-fill"><div class="fill-inner" style="width:' + h.fill + '%"></div></div>' +
          "</div>";
      }).join("");

      el("s1-levers").innerHTML = LEVERS.map(function (l) {
        var bar = l.highlight
          ? '<div class="lever-track-blue"><span></span></div>'
          : '<div class="red-bar-fill"><div class="fill-inner" style="width:' + l.fill + '%"></div></div>';
        var status = l.highlight
          ? '<span class="status-active">' + esc(l.status) + "</span><span class=\"status-active\">" + esc(l.extra) + "</span>"
          : '<span class="status-exhausted">' + esc(l.status) + "</span>";
        return '<div class="lever-col' + (l.highlight ? " highlight" : "") + '">' +
          '<div class="lever-tag">' + esc(l.tag) + "</div>" +
          '<div class="lever-desc">' + esc(l.desc) + "</div>" + bar +
          '<div class="lever-status-row">' + status + "</div></div>";
      }).join("");

      el("s1-outcomes").innerHTML = OUTCOMES.map(function (o) {
        return '<div class="outcome-kpi-block">' +
          '<div class="outcome-label">' + esc(o.label) + "</div>" +
          '<div class="outcome-val">' + esc(o.val) + "</div>" +
          '<div class="outcome-subtext">' + esc(o.sub) + "</div></div>";
      }).join("");
    }
    return { render: render };
  })();

  /* ======================================================= S2 — Schematic */
  var S2 = (function () {
    var TELEMETRY = [
      { node: "pita",     name: "Pit Alpha Operations", badge: "badge-optimal",  badgeText: "OPTIMAL",  a: ["Extraction Rate", "6,204", "TPH"],  b: ["Active Fleet", "42", "Units"] },
      { node: "crusher",  name: "Crusher-03",           badge: "badge-critical", badgeText: "CRITICAL", a: ["Bearing Temp", "104.2", "°C"], b: ["Throughput", "4,152", "TPH"], critical: true },
      { node: "sag",      name: "SAG Mill Circuit",     badge: "badge-optimal",  badgeText: "OPTIMAL",  a: ["Power Draw", "14.21", "MW"],        b: ["P80 Size", "125", "µm"] },
      { node: "flot",     name: "Flotation Cells",      badge: "badge-stable",   badgeText: "STABLE",   a: ["Recovery Rate", "88.42", "%"],      b: ["Reagent Dose", "12.5", "g/t"] },
      { node: "tailings", name: "Tailings Facility",    badge: "badge-stable",   badgeText: "STABLE",   a: ["Water Return", "65.2", "%"],        b: ["Seepage", "0.02", "L/s"] },
      { node: "port",     name: "Port Berth",           badge: "badge-optimal",  badgeText: "OPTIMAL",  a: ["Stockpile", "124.4k", "t"],         b: ["Demurrage", "0", "Days"] }
    ];

    /* GEOMETRY IS MEASURED, NOT DECLARED.
     *
     * The handover file carried the connector paths and particle conduits as
     * hard-coded coordinates in a 1100x460 space. The nodes, however, are laid
     * out by a CSS grid (1.1fr 2fr 1.5fr), so their real positions are decided
     * by the browser, not by that constant. Measured on this build the two
     * disagreed by 45-144px, worsening left to right, and every responsive
     * breakpoint widened the gap further -- particles drifting through empty
     * canvas while the nodes they were meant to connect sat elsewhere.
     *
     * So the topology is declared as node-id pairs and the geometry is read
     * from the live element rects each time the canvas starts. The streams
     * land on the nodes at any viewport, and adding a node to the markup is
     * enough to route flow through it. */
    var EDGES = [
      { a: "pita",     b: "sh05",     type: "material", color: "#C28B53", size: 3.5, speed: 0.006, bend: -18 },
      { a: "pitb",     b: "sh05",     type: "material", color: "#C28B53", size: 3.5, speed: 0.005, bend:  18 },
      { a: "sh05",     b: "trks",     type: "material", color: "#C28B53", size: 4.0, speed: 0.015, bend: 0 },
      { a: "trks",     b: "crusher",  type: "material", color: "#C28B53", size: 4.5, speed: 0.012, bend: 0 },
      { a: "crusher",  b: "conveyor", type: "material", color: "#F59E0B", size: 3.5, speed: 0.015, bend: 0 },
      { a: "conveyor", b: "sag",      type: "material", color: "#F59E0B", size: 3.5, speed: 0.015, bend: 0 },
      { a: "sag",      b: "ball",     type: "material", color: "#00ACC1", size: 3.0, speed: 0.008, bend: -14 },
      { a: "sag",      b: "flot",     type: "material", color: "#00ACC1", size: 3.2, speed: 0.009, bend:  14 },
      { a: "flot",     b: "rail",     type: "material", color: "#FFB300", size: 3.0, speed: 0.007, bend: -22 },
      { a: "rail",     b: "port",     type: "material", color: "#FFB300", size: 4.0, speed: 0.014, bend: 0 },
      { a: "flot",     b: "tailings", type: "material", color: "#78909C", size: 3.2, speed: 0.006, bend:  22 },
      { a: "tailings", b: "water",    type: "water",    color: "#29B6F6", size: 2.8, speed: 0.008, bend: 0 },
      { a: "water",    b: "sag",      type: "water",    color: "#29B6F6", size: 2.5, speed: 0.005, bend:  70 }
    ];

    var geometry = [];
    var particles = [];
    var rafId = null;
    var activeNode = null;

    /* Centre of a node in canvas space, or null if it is not laid out. */
    function centre(id, box) {
      var n = el("node-" + id);
      if (!n) return null;
      var r = n.getBoundingClientRect();
      if (!r.width) return null;
      return { x: r.left - box.left + r.width / 2, y: r.top - box.top + r.height / 2 };
    }

    function measure() {
      var host = el("schematic-container");
      if (!host) return false;
      var box = host.getBoundingClientRect();
      geometry = [];
      EDGES.forEach(function (e) {
        var from = centre(e.a, box), to = centre(e.b, box);
        if (!from || !to) return;
        var mx = (from.x + to.x) / 2, my = (from.y + to.y) / 2;
        var dx = to.x - from.x, dy = to.y - from.y;
        var len = Math.hypot(dx, dy) || 1;
        geometry.push({
          edge: e, from: from, to: to,
          ctrl: { x: mx + (-dy / len) * e.bend, y: my + (dx / len) * e.bend }
        });
      });

      particles = [];
      if (!geometry.length) return false;
      for (var i = 0; i < 70; i++) {
        var g = geometry[i % geometry.length];
        particles.push({
          g: g, t: Math.random(),
          speed: g.edge.speed * (0.8 + Math.random() * 0.4),
          telem: (i % 3 === 0)
        });
      }
      return true;
    }

    function point(p0, p1, ctrl, t) {
      var u = 1 - t;
      return { x: u*u*p0.x + 2*u*t*ctrl.x + t*t*p1.x, y: u*u*p0.y + 2*u*t*ctrl.y + t*t*p1.y };
    }

    function startCanvas() {
      var canvas = el("schematic-particle-canvas");
      var host = el("schematic-container");
      if (!canvas || !host) return;
      var rect = host.getBoundingClientRect();
      if (!rect.width) return;
      canvas.width = rect.width;
      canvas.height = rect.height;
      if (!measure()) return;
      var ctx = canvas.getContext("2d");

      function frame(now) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        /* Connectors are drawn here rather than left to the static SVG: the
           SVG paths carried the same fixed coordinates the particles did, so
           they missed the nodes by the same margin. Drawing both from one
           measured geometry keeps the line and the flow on top of each other. */
        geometry.forEach(function (g) {
          ctx.beginPath();
          ctx.moveTo(g.from.x, g.from.y);
          ctx.quadraticCurveTo(g.ctrl.x, g.ctrl.y, g.to.x, g.to.y);
          ctx.strokeStyle = g.edge.type === "water" ? "rgba(41,182,246,0.45)" : "#BDC1C6";
          ctx.lineWidth = 1.5;
          if (g.edge.type === "water") { ctx.setLineDash([4, 4]); } else { ctx.setLineDash([]); }
          ctx.stroke();
          ctx.setLineDash([]);
        });

        var pulse = (Math.sin(now * 0.005) + 1) * 0.5;
        var crush = centre("crusher", host.getBoundingClientRect());
        if (crush) {
          ctx.beginPath();
          ctx.arc(crush.x, crush.y, 54 + pulse * 14, 0, Math.PI * 2);
          ctx.strokeStyle = "rgba(217,48,37," + (0.4 - pulse * 0.28) + ")";
          ctx.lineWidth = 2.5;
          ctx.stroke();
        }

        particles.forEach(function (p) {
          p.t += p.speed;
          if (p.t > 1) p.t = 0;
          var pt = point(p.g.from, p.g.to, p.g.ctrl, p.t);
          ctx.beginPath();
          if (p.telem) {
            var id = p.g.edge.a + "-" + p.g.edge.b;
            var alert = id.indexOf("crusher") !== -1 || id.indexOf("sag") !== -1;
            ctx.fillStyle = alert ? "#FF1744" : "#00E5FF";
            ctx.fillRect(pt.x - 2.5, pt.y - 2.5, 5, 5);
          } else {
            ctx.fillStyle = p.g.edge.color;
            ctx.arc(pt.x, pt.y, p.g.edge.size, 0, Math.PI * 2);
            ctx.fill();
          }
        });

        rafId = requestAnimationFrame(frame);
      }

      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(frame);
    }

    function stopCanvas() { if (rafId) { cancelAnimationFrame(rafId); rafId = null; } }

    /* Named inspect() rather than inspectNode(): the two source files defined
       inspectNode differently and this closure must not be mistaken for either. */
    function inspect(key) {
      var d = window.nodePRDData[key];
      if (!d) return;
      activeNode = key;
      Array.prototype.forEach.call(
        document.querySelectorAll(".schematic-node, .node-crusher-critical"),
        function (n) { n.classList.remove("node-active-selected"); }
      );
      var node = el("node-" + key);
      if (node) node.classList.add("node-active-selected");

      el("drawer-node-title").textContent = d.title;
      el("drawer-isa95-tag").textContent = d.tag;
      var hb = el("drawer-badge-health");
      hb.className = "badge " + d.healthClass;
      hb.textContent = d.health;
      el("drawer-swarm-id").textContent = d.swarm;
      el("drawer-swarm-coord").textContent = d.coord;
      el("drawer-solver-id").textContent = d.solver;
      el("drawer-formula-code").textContent = d.formula;
      el("drawer-sap-id").textContent = d.sap;
      el("drawer-telemetry-metrics").innerHTML = d.metrics.map(function (m) {
        return '<div class="drawer-keyval-row"><span class="drawer-key">' + esc(m.key) +
          ':</span><span class="drawer-val">' + esc(m.val) + "</span></div>";
      }).join("");
      el("schematic-inspector-drawer").classList.add("open");
    }

    function close() {
      el("schematic-inspector-drawer").classList.remove("open");
      Array.prototype.forEach.call(
        document.querySelectorAll(".schematic-node, .node-crusher-critical"),
        function (n) { n.classList.remove("node-active-selected"); }
      );
      activeNode = null;
    }

    function render() {
      el("s2-telemetry").innerHTML = TELEMETRY.map(function (t) {
        return '<div class="telemetry-card' + (t.critical ? " card-border-critical" : "") +
          '" data-node="' + t.node + '">' +
          '<div class="telemetry-card-header"><span' + (t.critical ? ' style="color:var(--m3-critical)"' : "") + ">" +
            esc(t.name) + '</span><span class="badge ' + t.badge + '">' + esc(t.badgeText) + "</span></div>" +
          '<div class="telemetry-values-row">' +
            '<div><div class="telemetry-stat-label">' + esc(t.a[0]) + "</div>" +
              '<div class="telemetry-stat-num' + (t.critical ? " critical-text" : "") + '">' + esc(t.a[1]) +
              ' <span class="telemetry-unit">' + esc(t.a[2]) + "</span></div></div>" +
            '<div><div class="telemetry-stat-label">' + esc(t.b[0]) + "</div>" +
              '<div class="telemetry-stat-num">' + esc(t.b[1]) +
              ' <span class="telemetry-unit">' + esc(t.b[2]) + "</span></div></div>" +
          "</div></div>";
      }).join("");

      Array.prototype.forEach.call(document.querySelectorAll("[data-node]"), function (n) {
        n.addEventListener("click", function () { inspect(n.getAttribute("data-node")); });
      });
      on("btn-close-drawer", "click", close);
      on("btn-drawer-dismiss", "click", close);
      on("btn-drawer-to-studio", "click", function () {
        var d = activeNode && window.nodePRDData[activeNode];
        close();
        App.go("ecosystem");
        if (d) S4.openDeepDive(d.coord.split(" ")[0]);
      });
    }

    return { render: render, enter: startCanvas, leave: stopCanvas, resize: startCanvas };
  })();

  /* ======================================================== S3 — Personas */
  var S3 = (function () {
    var ORDER = ["elena", "marcus", "dave", "sarah", "tariq", "priya", "chen", "claire"];
    var current = "elena";

    /* Named select() not selectPersona(): both source files defined
       selectPersona over different persona sets. */
    function select(key) {
      var p = window.personaPRDData[key];
      if (!p) return;
      current = key;

      Array.prototype.forEach.call(document.querySelectorAll(".persona-tab-btn"), function (b) {
        var on = b.getAttribute("data-persona") === key;
        b.classList.toggle("active", on);
        b.setAttribute("aria-selected", on ? "true" : "false");
      });

      el("persona-code-badge").textContent = p.code;
      el("persona-title-display").textContent = p.title;
      el("persona-mandate-display").textContent = p.mandate;
      el("persona-jtbd-display").textContent = p.jtbd;
      el("persona-broken-text").textContent = p.broken;
      el("persona-agentic-text").textContent = p.agentic;

      el("squad-list-container").innerHTML =
        '<div class="agent-cards-grid">' + p.squad.map(function (s) {
          var critic = s.auth.indexOf("CRITIC") !== -1;
          return '<div class="eco-agent-card" data-agent="' + esc(s.id) + '">' +
            "<div><div class=\"eco-agent-header\">" +
              '<span class="badge-agent-id">' + esc(s.id) + "</span>" +
              '<span class="badge ' + (critic ? "badge-critical" : "badge-optimal") + '">' + esc(s.auth) + "</span>" +
            "</div>" +
            '<div class="eco-agent-title">' + esc(s.name) + "</div>" +
            '<div class="eco-agent-desc">' + esc(s.desc) + "</div></div>" +
            '<div class="eco-agent-footer">' +
              '<span style="font-size:11px; font-weight:700; color:#137333;">' + esc(s.val) + "</span>" +
              '<span style="font-size:11.5px; font-weight:700; color:var(--m3-primary);">Open deep dive &rsaquo;</span>' +
            "</div></div>";
        }).join("") + "</div>";

      Array.prototype.forEach.call(el("squad-list-container").querySelectorAll("[data-agent]"), function (c) {
        c.addEventListener("click", function () {
          App.go("ecosystem");
          S4.openDeepDive(c.getAttribute("data-agent"));
        });
      });
    }

    function render() {
      el("persona-tabs").innerHTML = ORDER.map(function (k) {
        var p = window.personaPRDData[k];
        var label = p.code.split("•")[0].trim() + ": " + p.title.split(",")[0];
        return '<button class="persona-tab-btn" role="tab" data-persona="' + k + '">' + esc(label) + "</button>";
      }).join("");

      Array.prototype.forEach.call(document.querySelectorAll(".persona-tab-btn"), function (b) {
        b.addEventListener("click", function () { select(b.getAttribute("data-persona")); });
      });

      on("btn-persona-studio", "click", function () {
        var p = window.personaPRDData[current];
        App.go("ecosystem");
        if (p) S4.openDeepDive(p.coordinatorId);
      });

      select("elena");
    }
    return { render: render };
  })();

  /* ======================================================= S4 — Ecosystem */
  var S4 = (function () {
    var TIERS = [
      { key: "L0", title: "Strategic Governance (NPV Optimization)", badge: "badge-primary",
        desc: "The apex node. Translates macro-economic directives into actionable mining constraints. Focuses on maximizing Net Present Value." },
      { key: "L2", title: "Domain Swarms (Specialized automation)", badge: "badge-critical",
        desc: "Coordinators, specialists and adversarial critics executing heuristics and predictive analysis across the pit-to-port value chain." },
      { key: "L3", title: "Physics Solvers (Deterministic truth)", badge: "badge-stable",
        desc: "The immutable ground truth. Hard-coded thermodynamic, kinetic and geospatial engines. Agents propose; solvers dispose." }
    ];
    var ids = [];
    var active = null;

    function agents() { return window.agentCatalogData || {}; }

    function cardHtml(a) {
      var critic = a.id.indexOf("CRITIC") !== -1;
      return '<div class="eco-agent-card" data-agent="' + esc(a.id) + '">' +
        '<div><div class="eco-agent-header">' +
          '<div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">' +
            '<span class="badge-agent-id">' + esc(a.id) + "</span>" +
            '<span class="badge badge-stable" style="font-size:9.5px;">' + esc(a.apqc) + "</span>" +
          "</div>" +
          '<span class="badge ' + (critic ? "badge-critical" : "badge-optimal") + '" style="font-size:9.5px;">' + esc(a.authority) + "</span>" +
        "</div>" +
        '<div class="eco-agent-title">' + esc(a.name) + "</div>" +
        '<div class="eco-agent-desc">' + esc(String(a.mechanism || "").slice(0, 115)) + "…</div></div>" +
        '<div class="eco-agent-footer">' +
          '<span style="font-size:11px; font-weight:700; color:#137333;">' + esc(a.valueClass) + "</span>" +
          '<span style="font-size:11.5px; font-weight:700; color:var(--m3-primary);">Inspect &rsaquo;</span>' +
        "</div></div>";
    }

    function bindCards(root) {
      Array.prototype.forEach.call(root.querySelectorAll("[data-agent]"), function (c) {
        c.addEventListener("click", function () { openDeepDive(c.getAttribute("data-agent")); });
      });
    }

    function renderTopology() {
      var all = agents();
      var counts = window.agentTierCounts || {};
      el("eco-hero-count").textContent = String(Object.keys(all).length);

      el("eco-filter-chips").innerHTML =
        '<button class="filter-chip active" data-tier="ALL">All (' + Object.keys(all).length + ")</button>" +
        TIERS.map(function (t) {
          return '<button class="filter-chip" data-tier="' + t.key + '">' + t.key + " (" + (counts[t.key] || 0) + ")</button>";
        }).join("");

      el("topology-stack").innerHTML = TIERS.map(function (t) {
        var members = Object.keys(all).map(function (k) { return all[k]; })
          .filter(function (a) { return a.tierKey === t.key; });

        var body;
        if (t.key === "L2") {
          var groups = {};
          members.forEach(function (a) {
            var g = a.id.slice(0, 3);
            (groups[g] = groups[g] || []).push(a);
          });
          body = Object.keys(groups).sort().map(function (g) {
            return '<div class="swarm-group-block">' +
              '<div class="swarm-group-title"><span>' + esc(g) + " Domain Swarm</span>" +
                '<span class="badge badge-primary" style="font-size:10px;">' + groups[g].length + " agents</span></div>" +
              '<div class="agent-cards-grid">' + groups[g].map(cardHtml).join("") + "</div></div>";
          }).join("");
        } else {
          body = '<div class="agent-cards-grid">' + members.map(cardHtml).join("") + "</div>";
        }

        return '<div class="topology-timeline-item" data-tier-row="' + t.key + '">' +
          '<div class="timeline-badge-node">' + t.key + "</div>" +
          '<div class="timeline-card-wrapper expanded" data-tier-card="' + t.key + '">' +
            '<div class="tier-header-bar" data-tier-toggle="' + t.key + '">' +
              '<div class="tier-title-cluster"><div class="tier-main-title">' + esc(t.title) + "</div>" +
                '<div class="tier-main-desc">' + esc(t.desc) + "</div></div>" +
              '<div class="tier-right-cluster">' +
                '<span class="badge ' + t.badge + '" style="font-size:11px;">' + members.length + " agents</span>" +
                '<svg class="tier-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>' +
              "</div></div>" +
            '<div class="tier-accordion-body">' + body + "</div>" +
          "</div></div>";
      }).join("");

      bindCards(el("topology-stack"));

      Array.prototype.forEach.call(document.querySelectorAll("[data-tier-toggle]"), function (h) {
        h.addEventListener("click", function () {
          var w = document.querySelector('[data-tier-card="' + h.getAttribute("data-tier-toggle") + '"]');
          if (w) w.classList.toggle("expanded");
        });
      });
      Array.prototype.forEach.call(document.querySelectorAll("[data-tier]"), function (chip) {
        chip.addEventListener("click", function () {
          var tier = chip.getAttribute("data-tier");
          Array.prototype.forEach.call(document.querySelectorAll("[data-tier]"), function (c) {
            c.classList.toggle("active", c === chip);
          });
          TIERS.forEach(function (t) {
            var row = document.querySelector('[data-tier-row="' + t.key + '"]');
            if (row) row.style.display = (tier === "ALL" || tier === t.key) ? "flex" : "none";
          });
        });
      });

      var sel = el("agent-quick-select");
      ids = Object.keys(all);
      sel.innerHTML = ids.map(function (k) {
        return '<option value="' + esc(k) + '">' + esc(k) + " — " + esc(all[k].name) + "</option>";
      }).join("");
    }

    function search(q) {
      q = (q || "").toLowerCase().trim();
      var results = el("eco-search-results"), stack = el("topology-stack");
      if (!q) { results.style.display = "none"; stack.style.display = "block"; return; }
      var all = agents();
      var hits = Object.keys(all).map(function (k) { return all[k]; }).filter(function (a) {
        return (a.id + " " + a.name + " " + a.apqc + " " + a.department + " " + a.persona + " " + a.mechanism)
          .toLowerCase().indexOf(q) !== -1;
      });
      stack.style.display = "none";
      results.style.display = "block";
      el("search-results-count").textContent = hits.length + " matching agents and solvers";
      el("search-cards-container").innerHTML = hits.length
        ? hits.map(cardHtml).join("")
        : '<div style="padding:20px; font-size:13px; color:var(--m3-text-secondary);">No matching agents. Try "geology", "crusher", "NPV", "D01" or "S05".</div>';
      bindCards(el("search-cards-container"));
    }

    function openDeepDive(agentId) {
      var all = agents();
      var a = all[agentId] || all[ids[0]];
      if (!a) return;
      active = a.id;

      el("dd-badge-id").textContent = a.id;
      el("dd-badge-apqc").textContent = a.apqc;
      el("dd-badge-status").textContent = a.hitl ? "HUMAN APPROVAL REQUIRED" : "ADVISORY";
      el("dd-title").textContent = a.name;
      el("dd-process").textContent = "Persona: " + a.persona + " · " + a.department;
      el("dd-value-amount").textContent = a.valueClass;
      el("dd-value-period").textContent = a.hitl ? "Dual-key human release required" : "Advisory output, human executes";
      el("dd-authority-text").textContent =
        "Authority " + a.authority + ". " +
        (a.hitl
          ? "This agent cannot release its own action: a named human holds the key."
          : "Advisory by default — every recommendation lands with a named human.") +
        " Endpoint: " + a.endpoint + ".";
      el("dd-mechanism-text").textContent = a.mechanism || "—";
      el("dd-code-lang").textContent = a.model || "";
      el("dd-code-box").textContent = a.governingEquation || "—";
      el("dd-btn-urn").setAttribute("data-urn",
        "urn:agent:genial-union-475913-i7:us-central1:" + a.id.toLowerCase());

      el("dd-provenance-list").innerHTML = (a.provenance || []).length
        ? a.provenance.map(function (p) {
            return '<div class="prov-item-row"><div class="prov-left">' +
              '<span class="prov-dot ' + (p.type === "SAP" ? "prov-dot-amber" : "prov-dot-blue") + '"></span>' +
              '<span>' + esc(p.name) + "</span></div>" +
              '<span class="prov-badge">' + esc(p.type) + "</span></div>";
          }).join("")
        : '<div style="font-size:11.5px; color:var(--m3-text-secondary);">No grounding tables declared.</div>';

      el("agent-quick-select").value = a.id;
      el("view-ecosystem-overview").classList.remove("active");
      el("view-agent-deepdive").classList.add("active");
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function backToOverview() {
      el("view-agent-deepdive").classList.remove("active");
      el("view-ecosystem-overview").classList.add("active");
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function cycle(step) {
      var i = ids.indexOf(active);
      if (i === -1) i = 0;
      openDeepDive(ids[(i + step + ids.length) % ids.length]);
    }

    function render() {
      renderTopology();
      on("eco-search-input", "input", function (e) { search(e.target.value); });
      on("btn-clear-search", "click", function () { el("eco-search-input").value = ""; search(""); });
      on("btn-back-topology", "click", backToOverview);
      on("btn-agent-prev", "click", function () { cycle(-1); });
      on("btn-agent-next", "click", function () { cycle(1); });
      on("agent-quick-select", "change", function (e) { openDeepDive(e.target.value); });
      on("dd-btn-urn", "click", function (e) {
        Clip.copy(e.currentTarget.getAttribute("data-urn"), e.currentTarget);
      });
      on("btn-launch-sim", "click", function () {
        var a = agents()[active];
        if (!a) return;
        el("sim-modal-title").textContent = "Simulation: " + a.name + " (" + a.id + ")";
        el("sim-modal-desc").textContent = "Deterministic reasoning over " + a.department + " with zero-hallucination verification.";
        el("sim-terminal-output").innerHTML =
          "[INIT] Connecting to reasoning engine…<br>" +
          "[GROUNDING] " + ((a.provenance || []).map(function (p) { return p.name; }).join(", ") || "no declared tables") + "<br>" +
          "[SOLVER] " + esc(a.governingEquation) + "<br>" +
          "[AUTHORITY] " + esc(a.authority) + (a.hitl ? " — dual-key human release required" : "") + "<br>" +
          "[VALUE] " + esc(a.valueClass) + "<br>" +
          "[STAGING] Emitting mediated non-SCADA advisory payload…<br>" +
          "[DONE] 0 exceptions";
        el("modal-sim").classList.add("active");
      });
      on("btn-lineage-trace", "click", function () {
        var a = agents()[active];
        el("lineage-modal-title").textContent = "Lineage: " + (a ? a.id : "");
        el("lineage-steps").innerHTML = [
          ["1. Physical sensors", "OT INGRESS"], ["2. Air-gap diode", "IEC-62443 SL4"],
          ["3. BigQuery grounding", "BIGQUERY"], ["4. Swarm + solver", "ZERO-HALLUCINATION"],
          ["5. Staged payload", "DUAL-KEY"]
        ].map(function (s, i, arr) {
          return '<div style="background:var(--m3-surface-subtle); padding:10px 14px; border-radius:4px; display:flex; justify-content:space-between; gap:10px;">' +
            "<span><strong>" + esc(s[0]) + "</strong></span>" +
            '<span class="badge badge-primary">' + esc(s[1]) + "</span></div>" +
            (i < arr.length - 1 ? '<div style="text-align:center; color:var(--m3-primary);">&darr;</div>' : "");
        }).join("");
        el("modal-lineage").classList.add("active");
      });
      on("btn-close-sim", "click", function () { el("modal-sim").classList.remove("active"); });
      on("btn-done-sim", "click", function () { el("modal-sim").classList.remove("active"); });
      on("btn-close-lineage", "click", function () { el("modal-lineage").classList.remove("active"); });
      on("btn-done-lineage", "click", function () { el("modal-lineage").classList.remove("active"); });

      openDeepDive(ids[0]);
      backToOverview();
    }

    return { render: render, openDeepDive: openDeepDive, backToOverview: backToOverview };
  })();

  /* ====================================================== S5 — Governance */
  var S5 = (function () {
    var STACK = [
      { tier: "L0", name: "Strategic Governance (AGT-19)", desc: "Dynamic cut-off grade and capital allocation optimizer." },
      { tier: "L1", name: "ROC Central Arbiters",          desc: "Pit-to-port balancing across competing constraints." },
      { tier: "L2", name: "Multi-Agent Swarms",            desc: "Coordinators, specialists and adversarial critics." },
      { tier: "L3", name: "Deterministic Physics Solvers", desc: "Zero-hallucination microservices." },
      { tier: "L4", name: "Enterprise Data Lakehouse",     desc: "BigQuery telemetry ingest and property graphs." }
    ];
    var STAGING = [
      { n: "01", color: "var(--m3-primary)",  title: "Agent proposal",     sub: "Agent suggests a parameter change via API." },
      { n: "02", color: "var(--m3-critical)", title: "ERP staging area",   sub: "Action held in an isolated ERP buffer." },
      { n: "03", color: "#137333",            title: "Dual-key MFA release", sub: "Human operator plus shift boss token.", final: true }
    ];
    var PROVENANCE = [
      { stage: "STAGE 1", title: "Raw telemetry",   desc: "Sensor data from heavy machinery streams via MQTT." },
      { stage: "STAGE 2", title: "Ingest & cleanse", desc: "Optical diode validation and BigQuery staging tables." },
      { stage: "STAGE 3", title: "Property graphs", desc: "GoogleSQL transformations construct entity relationships." },
      { stage: "STAGE 4", title: "Agent inference", desc: "Swarms analyse state and output mediated ERP proposals." }
    ];

    function render() {
      el("gov-stack-steps").innerHTML = STACK.map(function (s) {
        return '<div class="stack-step"><div class="stack-step-icon">' + esc(s.tier) + "</div>" +
          '<div><div style="font-size:12px; font-weight:700;">' + esc(s.name) + "</div>" +
          '<div style="font-size:11px; color:var(--m3-text-secondary);">' + esc(s.desc) + "</div></div></div>";
      }).join("");

      el("gov-staging-steps").innerHTML = STAGING.map(function (s) {
        return '<div class="staging-step' + (s.final ? " step-final" : "") + '">' +
          '<span style="font-weight:700; color:' + s.color + ';">' + esc(s.n) + "</span>" +
          "<div><strong>" + esc(s.title) + "</strong><br>" +
          '<span style="color:var(--m3-text-secondary); font-size:10.5px;">' + esc(s.sub) + "</span></div></div>";
      }).join("");

      el("gov-provenance-steps").innerHTML = PROVENANCE.map(function (p) {
        return '<div class="provenance-step-box">' +
          '<div style="font-size:10.5px; font-weight:700; color:var(--m3-primary);">' + esc(p.stage) + "</div>" +
          '<div style="font-weight:700; font-size:12px; margin:2px 0;">' + esc(p.title) + "</div>" +
          '<div style="font-size:10.5px; color:var(--m3-text-secondary);">' + esc(p.desc) + "</div></div>";
      }).join("");

      /* The audit line is stamped at render, not hard-coded: a frozen date on a
         security posture screen reads as a stale audit, which is worse than no
         date at all. */
      var now = new Date();
      el("gov-audit-line").innerHTML =
        "LAST RENDER: " + now.toISOString().slice(0, 16).replace("T", " ") + "Z<br>POSTURE: ENFORCED";
    }
    return { render: render };
  })();

  /* ============================================================== ROUTER */
  var App = {
    go: function (screen) {
      if (SCREENS.indexOf(screen) === -1) screen = "macro";

      SCREENS.forEach(function (s) {
        var pane = el("pane-" + s), tab = el("tab-" + s);
        if (pane) pane.classList.toggle("active", s === screen);
        if (tab) {
          tab.classList.toggle("active", s === screen);
          tab.setAttribute("aria-selected", s === screen ? "true" : "false");
        }
      });

      /* Only Screen 2 animates. Leaving its rAF loop running while another
         screen is showing burns a frame budget on a canvas nobody can see, so
         the router starts and stops it explicitly rather than letting it idle. */
      if (screen === "schematic") { setTimeout(S2.enter, 50); } else { S2.leave(); }

      try {
        if (window.history && window.history.pushState) {
          window.history.pushState(null, "", "#" + screen);
        }
      } catch (e) { /* restricted embedding context */ }

      window.scrollTo({ top: 0, behavior: "smooth" });
    },

    init: function () {
      S1.render(); S2.render(); S3.render(); S4.render(); S5.render();

      SCREENS.forEach(function (s) {
        var tab = el("tab-" + s);
        if (tab) tab.addEventListener("click", function (e) { e.preventDefault(); App.go(s); });
      });

      on("btn-header-search", "click", function () {
        App.go("ecosystem");
        var input = el("eco-search-input");
        if (input) input.focus();
      });

      window.addEventListener("hashchange", function () {
        App.go((window.location.hash || "").replace(/^#/, ""));
      });
      window.addEventListener("resize", function () {
        if (el("pane-schematic").classList.contains("active")) S2.resize();
      });

      var initial = (window.location.hash || "").replace(/^#/, "");
      App.go(SCREENS.indexOf(initial) !== -1 ? initial : "macro");
    }
  };

  window.App = App;
  document.addEventListener("DOMContentLoaded", App.init);
})();
