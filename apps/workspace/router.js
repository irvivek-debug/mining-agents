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
  /* A value branch is a business area, not a tool, and reads as one in the
   * reason. It keeps the tool weight: naming a branch is as weak a signal. */
  branchesOf(agent.value_branch).forEach(function (b) {
    terms.push({ kind: "branch", id: b, plain: b.replace(/_/g, " "), weight: WEIGHT.tool });
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

/* The clause after "Asking <agent>." — and it carries no agent name of its own.
 * The caller frames the name once; a reason that named it again produced
 * "Asking Cascading Failure Impact & Recovery Coordinator. Nothing in the
 * question named a capability, so it goes to Cascading Failure Impact &
 * Recovery Coordinator, the agent this role leads with."
 *
 * Each matched term becomes a verb and an object, kept apart so that two
 * matches sharing a verb read as "It reads the work orders and the parts on
 * hand" rather than "It reads work orders and reads parts on hand".
 */
function _clause(m) {
  var kind = m.term.kind;
  var plain = m.term.plain;
  // Table phrases carry no article of their own — the frame that uses them
  // owns it, and whether one is wanted depends on the phrase.
  if (kind === "table") return { verb: "reads", object: PLAIN.articleFor(plain) + plain };
  if (kind === "traversal") return { verb: "traces", object: plain };
  if (kind === "tool") return { verb: "can", object: PLAIN.plainToolAbility(m.term.id) };
  if (kind === "branch") return { verb: "covers", object: plain };
  if (kind === "apqc") return { verb: "covers", object: plain.toLowerCase() };
  // kind "name": the question echoed the agent's own name back. "It covers
  // fatigue risk scorer" tells a reader who typed those words nothing, so the
  // term yields no clause and another match speaks instead.
  return null;
}

function _reason(scored) {
  var named = false;
  var parts = [];
  scored.matched.forEach(function (m) {
    if (parts.length >= 2) return;
    var clause = _clause(m);
    if (!clause) { named = true; return; }
    parts.push(clause);
  });

  if (parts.length === 2 && parts[0].verb === parts[1].verb) {
    return "It " + parts[0].verb + " " + parts[0].object + " and " +
      parts[1].object + ".";
  }
  if (parts.length) {
    return "It " + parts.map(function (p) {
      return p.verb + " " + p.object;
    }).join(" and ") + ".";
  }
  // Only the agent's own name matched. Saying so is both the reason and a
  // warning that the pick is a weak one, which is what the buttons beside it
  // are for.
  if (named) return "Your question matched its name and nothing more specific.";
  return "Nothing in the question named a capability, so it goes to the agent " +
    "this role leads with.";
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
    reason: _reason(winner.detail),
    runners_up: runners,
  };
}

/* Turn a table phrase into a question. Table phrases that are relative clauses
 * — the ones articleFor gives no article to — compose as "Show me …" because
 * they are already a complete clause and the container frame would be redundant.
 * All other phrases use "What's in the … right now?" — this frame works for
 * both singular and plural nouns without any number-agreement logic, and it
 * never reintroduces an article into the phrase itself. */
function _tableQuestion(phrase) {
  if (!PLAIN.articleFor(phrase)) return "Show me " + phrase + ".";
  return "What's in the " + phrase + " right now?";
}

/* Cold start. No example questions exist anywhere in the catalogue, so these are
 * derived rather than authored: each is built from one capability an agent
 * actually declares, and then checked by routing it back. A starter that did not
 * route to the agent it came from would teach the reader the wrong thing about
 * what the page does, so it is discarded rather than shipped.
 *
 * Tier 1: capabilities unique to a single agent within the persona — cannot name
 * a phrase that belongs to a sibling, so round-trip is strongest here.
 * Tier 2: shared capabilities — still checked by routing back, so a question that
 * routes ambiguously is discarded automatically rather than shipped wrong.
 */
function _candidateQuestions(agent, allAgents) {
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

  var tier1 = [];
  var tier2 = [];

  /* Prefer traversals first (highest weight) */
  (agent.traversals || []).forEach(function (t) {
    var q = "Show me " + PLAIN.plainTraversal(t) + ".";
    if (traversalCount[t] === 1) {
      tier1.push({ agent: agent, q: q });
    } else {
      tier2.push({ agent: agent, q: q });
    }
  });

  /* Then tables */
  (agent.source_tables || []).forEach(function (t) {
    var bare = PLAIN.bareTable(t);
    var q = _tableQuestion(PLAIN.plainTable(t));
    if (tableCount[bare] === 1) {
      tier1.push({ agent: agent, q: q });
    } else {
      tier2.push({ agent: agent, q: q });
    }
  });

  return { tier1: tier1, tier2: tier2 };
}

/* Internal: returns [{q, agent, isGeneric}] of exactly 3 items. The agent field
 * is the specific agent the question was derived from (null for generic
 * backstops). Exposed for testing via _starterItems; the public starterQuestions
 * returns only the strings, keeping the external contract stable. */
function _starterItems(personaCode, DATA) {
  var persona = DATA.personas.personas[personaCode];
  var byId = {};
  DATA.catalog.agents.forEach(function (a) { byId[a.agent_id] = a; });
  var agents = (persona.agents || []).map(function (id) { return byId[id]; }).filter(Boolean);

  var pools1 = agents.map(function (agent) {
    return _candidateQuestions(agent, agents).tier1;
  });
  var pools2 = agents.map(function (agent) {
    return _candidateQuestions(agent, agents).tier2;
  });

  /* Round-robin pass: tier-1 (unique capabilities) first, then tier-2 (shared
   * capabilities). The round-trip check inside the loop is what keeps shared
   * candidates honest — a question that routes to the wrong agent is discarded. */
  var chosen = [];
  var seen = {};

  function tryPool(pools) {
    for (var depth = 0; depth < 30; depth++) {
      pools.forEach(function (pool) {
        if (!pool[depth]) return;
        var item = pool[depth];
        if (chosen.length >= 3 || seen[item.q]) return;
        if (route(item.q, personaCode, DATA).agent_id !== item.agent.agent_id) return;
        seen[item.q] = true;
        chosen.push({ q: item.q, agent: item.agent, isGeneric: false });
      });
    }
  }

  tryPool(pools1);
  tryPool(pools2);

  // Backstop: a question that names no capability routes to the persona's lead
  // agent by the same tie-break every empty question uses, so it is honest.
  var generic = [
    "What should I look at first?",
    "What changed since yesterday?",
    "What needs my attention?",
  ];
  generic.forEach(function (q) {
    if (chosen.length >= 3 || seen[q]) return;
    seen[q] = true;
    chosen.push({ q: q, agent: null, isGeneric: true });
  });

  return chosen.slice(0, 3);
}

function starterQuestions(personaCode, DATA) {
  return _starterItems(personaCode, DATA).map(function (item) { return item.q; });
}

if (typeof module !== "undefined") {
  module.exports = { route, starterQuestions, _starterItems, branchesOf, tokens, scoreAgent };
}
