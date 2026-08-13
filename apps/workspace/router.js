/* Which of this persona's agents should take this question, and why.
 *
 * Deterministic string matching over catalogue metadata, not comprehension. It
 * will sometimes be wrong, which is why route() returns the reason and the
 * runners-up: being wrong in the open with a one-click fix is the recovery
 * path, and a hidden wrong decision is not.
 *
 * The candidate set is the persona's own agents and nothing else. The persona
 * page is a claim about scope; a router that quietly left scope would make the
 * page a lie.
 */
var PLAIN = typeof require !== "undefined"
  ? require("../shared/plain.js")
  : window;

/* A traversal match is the strongest signal — three traversals exist across the
 * whole catalogue, so naming one is nearly an address. A table match is next: 25
 * tables, still specific. A tool match is weakest: five tools, shared widely. */
var WEIGHT = { traversal: 4, table: 3, apqc: 2, name: 2, tool: 1 };

var STOP = new Set((
  "a an and are as at be by can could did do does for from get give had has have how i " +
  "if in into is it its me my of on or our right should show so tell that the their them " +
  "then there these they this to us was we what when where which who why will with would you your now"
).split(" "));

function branchesOf(x) {
  if (!x) return [];
  return Array.isArray(x) ? x.slice() : [x];
}

function tokens(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter(function (t) { return t && !STOP.has(t); });
}

/* Every phrase this agent answers to, with the weight of naming it. */
function termsFor(agent) {
  var terms = [];
  (agent.traversals || []).forEach(function (t) {
    terms.push({ kind: "traversal", id: t, plain: PLAIN.plainTraversal(t),
                 weight: WEIGHT.traversal });
  });
  (agent.source_tables || []).forEach(function (t) {
    var bare = PLAIN.bareTable(t);
    terms.push({ kind: "table", id: bare, plain: PLAIN.plainTable(t),
                 weight: WEIGHT.table });
  });
  (agent.apqc_names || []).forEach(function (n) {
    terms.push({ kind: "apqc", id: n, plain: n, weight: WEIGHT.apqc });
  });
  terms.push({ kind: "name", id: agent.agent_id, plain: agent.display_name || "",
               weight: WEIGHT.name });
  (agent.tools || []).forEach(function (t) {
    terms.push({ kind: "tool", id: t, plain: PLAIN.plainTool(t), weight: WEIGHT.tool });
  });
  branchesOf(agent.value_branch).forEach(function (b) {
    terms.push({ kind: "tool", id: b, plain: b.replace(/_/g, " "), weight: WEIGHT.tool });
  });
  return terms;
}

/* A term scores when the question shares a content word with it. Score is the
 * term's weight times the number of distinct shared words, so "crew fatigue
 * readings" beats "fatigue records" on a question that says both. */
function scoreAgent(qTokens, agent) {
  var asked = new Set(qTokens);
  var total = 0;
  var best = null;
  var matched = [];
  termsFor(agent).forEach(function (term) {
    var hits = 0;
    tokens(term.plain).concat(tokens(term.id)).forEach(function (word) {
      if (asked.has(word)) { hits += 1; asked.delete(word); }
    });
    if (!hits) return;
    var points = term.weight * hits;
    total += points;
    matched.push({ term: term, points: points });
    if (!best || points > best.points) best = { term: term, points: points };
  });
  matched.sort(function (a, b) { return b.points - a.points; });
  return { score: total, best: best, matched: matched };
}

/* Total and stable: ties break toward the swarm coordinator, then toward the
 * lowest agent id, so a question of pure stop-words still names an agent. */
function _better(a, b) {
  if (a.score !== b.score) return a.score > b.score;
  var aCoord = a.agent.swarm_role === "coordinator";
  var bCoord = b.agent.swarm_role === "coordinator";
  if (aCoord !== bCoord) return aCoord;
  return a.agent.agent_id < b.agent.agent_id;
}

function _reason(scored, agent) {
  if (!scored.matched.length) {
    return "Nothing in the question named a capability, so it goes to " +
      (agent.display_name || agent.agent_id) + ", the agent this role leads with.";
  }
  var phrases = scored.matched.slice(0, 2).map(function (m) {
    if (m.term.kind === "table") return "reads " + m.term.plain;
    if (m.term.kind === "traversal") return "traces " + m.term.plain;
    if (m.term.kind === "tool") return m.term.plain;
    return "covers " + m.term.plain.toLowerCase();
  });
  return "It " + phrases.join(" and ") + ".";
}

function route(question, personaCode, DATA) {
  var persona = DATA.personas.personas[personaCode];
  var byId = {};
  DATA.catalog.agents.forEach(function (a) { byId[a.agent_id] = a; });
  var candidates = (persona.agents || [])
    .map(function (id) { return byId[id]; })
    .filter(Boolean);

  var qTokens = tokens(question);
  var scored = candidates.map(function (agent) {
    var s = scoreAgent(qTokens, agent);
    return { agent: agent, score: s.score, detail: s };
  });

  var winner = scored[0];
  scored.forEach(function (row) { if (_better(row, winner)) winner = row; });

  var runners = scored
    .filter(function (r) { return r.agent.agent_id !== winner.agent.agent_id && r.score > 0; })
    .sort(function (a, b) {
      return b.score - a.score || (a.agent.agent_id < b.agent.agent_id ? -1 : 1);
    })
    .slice(0, 3)
    .map(function (r) { return { agent_id: r.agent.agent_id, score: r.score }; });

  return {
    agent_id: winner.agent.agent_id,
    reason: _reason(winner.detail, winner.agent),
    runners_up: runners,
  };
}

/* Cold start. No example questions exist anywhere in the catalogue, so these are
 * derived rather than authored: each is built from one capability an agent
 * actually declares, and then checked by routing it back. A starter that did not
 * route to the agent it came from would teach the reader the wrong thing about
 * what the page does, so it is discarded rather than shipped.
 *
 * Only capabilities unique to a single agent within the persona are used, so
 * the round-trip check passes and the question cannot name a phrase that belongs
 * to a sibling agent.
 */
function _candidateQuestions(agent, allAgents) {
  var out = [];

  /* Build a map of which capabilities are shared by how many agents in the set */
  var tableCount = {};
  var traversalCount = {};
  allAgents.forEach(function (a) {
    (a.source_tables || []).forEach(function (t) {
      var bare = PLAIN.bareTable(t);
      tableCount[bare] = (tableCount[bare] || 0) + 1;
    });
    (a.traversals || []).forEach(function (t) {
      traversalCount[t] = (traversalCount[t] || 0) + 1;
    });
  });

  /* Prefer traversals first (highest weight) — only use if unique to this agent */
  (agent.traversals || []).forEach(function (t) {
    if (traversalCount[t] === 1) {
      out.push({ agent: agent, q: "Show me " + PLAIN.plainTraversal(t) + "." });
    }
  });

  /* Then tables unique to this agent */
  (agent.source_tables || []).forEach(function (t) {
    var bare = PLAIN.bareTable(t);
    if (tableCount[bare] === 1) {
      out.push({ agent: agent, q: "What do " + PLAIN.plainTable(t) + " show right now?" });
    }
  });

  return out;
}

function starterQuestions(personaCode, DATA) {
  var persona = DATA.personas.personas[personaCode];
  var byId = {};
  DATA.catalog.agents.forEach(function (a) { byId[a.agent_id] = a; });
  var agents = (persona.agents || []).map(function (id) { return byId[id]; }).filter(Boolean);

  // Round-robin over the agents so three starters do not all come from one.
  var pools = agents.map(function (agent) { return _candidateQuestions(agent, agents); });
  var queue = [];
  for (var depth = 0; depth < 30; depth++) {
    pools.forEach(function (pool) { if (pool[depth]) queue.push(pool[depth]); });
  }

  var chosen = [];
  var seen = {};
  queue.forEach(function (item) {
    if (chosen.length >= 3 || seen[item.q]) return;
    if (route(item.q, personaCode, DATA).agent_id !== item.agent.agent_id) return;
    seen[item.q] = true;
    chosen.push(item.q);
  });

  // Backstop, for a persona whose agents share every capability: a question that
  // names no capability at all routes to the persona's lead agent by the same
  // tie-break every empty question uses, so it is honest by construction.
  var generic = [
    "What should I look at first?",
    "What changed since yesterday?",
    "What needs my attention?",
  ];
  generic.forEach(function (q) {
    if (chosen.length >= 3 || seen[q]) return;
    seen[q] = true;
    chosen.push(q);
  });
  return chosen.slice(0, 3);
}

if (typeof module !== "undefined") {
  module.exports = { route, starterQuestions, branchesOf, tokens, scoreAgent };
}
