/* The sidecar: the part of the workspace that is not a document.
 *
 * Everything else on the page states what is already recorded. This asks a
 * deployed agent a question and shows the answer arriving. A real question was
 * measured at a little under two minutes, so the wait is real and cannot be
 * designed away — what can be designed is whether those seconds read as work
 * happening or as a spinner that cannot be told from a hang. Hence the activity
 * log, which fills steadily from the first few seconds onward.
 *
 * The router's pick is printed, not hidden, with its reason and a one-click
 * change. Deterministic string matching over catalogue metadata is not
 * comprehension and will sometimes be wrong; being wrong in the open with a
 * one-click fix is the recovery path.
 */
var CHAT_ROUTER = typeof require !== "undefined" ? require("./router.js") : window;
var CHAT_STREAM = typeof require !== "undefined" ? require("./agent-stream.js") : window;

/* esc comes from shell.js. In the browser it is a global, because classic script
 * tags share one scope and persona.html loads shell.js first. Node gives every
 * module its own scope, so the same name is resolved through require and
 * published where the function bodies below already look for it. Guarded on the
 * absence of a window so the browser path is untouched. */
if (typeof require !== "undefined" && typeof window === "undefined") {
  Object.assign(globalThis, require("../shared/shell.js"));
}

function _agentsById(DATA) {
  var byId = {};
  DATA.catalog.agents.forEach(function (a) { byId[a.agent_id] = a; });
  return byId;
}

function _name(agentId, DATA) {
  var agent = _agentsById(DATA)[agentId];
  return agent ? agent.display_name : agentId;
}

function pickLine(decision, DATA) {
  return "Asking " + _name(decision.agent_id, DATA) + ". " + decision.reason;
}

/* The buttons offered instead of the pick. Empty for a persona with one agent:
 * a control with nothing to change to is worse than no control. */
function alternatives(decision, DATA) {
  return (decision.runners_up || []).map(function (up) {
    return { agent_id: up.agent_id, label: _name(up.agent_id, DATA) };
  });
}

function opening(personaCode, DATA) {
  return {
    title: DATA.personas.personas[personaCode].title,
    starters: CHAT_ROUTER.starterQuestions(personaCode, DATA),
  };
}

/* Everything below touches the DOM. The stream lifecycle inside it is checked
 * from Node through the injectable `deps.streamAgent`; the markup is checked in
 * a browser. */
function mountChat(node, personaCode, DATA, deps) {
  var streamAgent = (deps && deps.streamAgent) || function (options) {
    return CHAT_STREAM.streamAgent(options);
  };
  var sessionId = "persona-" + personaCode + "-" + Date.now();
  var start = opening(personaCode, DATA);

  node.innerHTML =
    '<div class="chat-head"><h2>Ask your agents</h2>' +
    '<p class="pnote">These agents belong to the ' + esc(start.title) +
    " role. Start with one of the questions below, or write your own. A real " +
    "answer takes a minute or two; every step the agent takes appears here as " +
    "it happens.</p></div>" +
    '<div class="starters">' +
    start.starters.map(function (q) {
      return '<button class="starter" type="button">' + esc(q) + "</button>";
    }).join("") +
    "</div>" +
    '<div class="transcript" id="transcript" aria-live="polite"></div>' +
    '<form class="composer" id="composer">' +
    '<label class="sr-only" for="question">Your question</label>' +
    '<textarea id="question" rows="3" placeholder="Ask about this role\'s work…"></textarea>' +
    '<button class="ask primary" type="submit">Ask</button>' +
    "</form>";

  var transcript = node.querySelector("#transcript");

  /* The one stream that may be open, or null. Two open EventSources would
   * interleave two agents' text into one answer body — and, because
   * EventSource reconnects by itself when a connection closes, an abandoned one
   * keeps re-asking a question that takes a minute or two of real model time.
   * Every path that starts a stream goes through stop() first. */
  var live = null;

  function stop(note) {
    var was = live;
    live = null;
    if (!was) return;
    was.abandoned = true;          // so its own onDone stays out of the transcript
    if (was.note) was.note(note);
    if (was.handle) was.handle.close();
  }

  function block(html, cls) {
    var div = document.createElement("div");
    div.className = cls;
    div.innerHTML = html;
    transcript.appendChild(div);
    // Scroll the transcript, never the page. A stream that ran scrollIntoView
    // on every step would yank the document out from under a reader who is
    // halfway down the left-hand panel, once every few seconds, for the whole
    // minute or two the answer takes.
    transcript.scrollTop = transcript.scrollHeight;
    return div;
  }

  /* One line per thing the agent is doing — not one per frame on the wire.
   *
   * A tool call arrives twice, as the call and as its response, and both render
   * to the same sentence because the response frame carries no arguments of its
   * own to say anything more with. Printed as they come, a successful call reads
   * as the same line twice in a row, which reads as a rendering fault. A call
   * that fails does not repeat itself: its second line is the failure, and that
   * one is worth every bit of the room it takes. */
  function line(log, text, cls) {
    var previous = log.children[log.children.length - 1];
    if (previous && previous.textContent === text) return previous;
    var p = document.createElement("p");
    p.className = cls;
    p.textContent = text;
    log.appendChild(p);
    transcript.scrollTop = transcript.scrollHeight;
    return p;
  }

  function run(question, forcedAgentId) {
    stop("Stopped — you asked something else.");

    var decision = forcedAgentId
      ? { agent_id: forcedAgentId, reason: "You picked this one.", runners_up: [] }
      : CHAT_ROUTER.route(question, personaCode, DATA);

    block("<p>" + esc(question) + "</p>", "you");
    var head = block("<p>" + esc(pickLine(decision, DATA)) + "</p>", "pick");

    alternatives(decision, DATA).forEach(function (alt) {
      var button = document.createElement("button");
      button.type = "button";
      button.className = "ask alt";
      button.textContent = "Ask " + alt.label + " instead";
      button.addEventListener("click", function () { run(question, alt.agent_id); });
      head.appendChild(button);
    });

    var log = block("", "log");
    var answer = block("", "answer");

    var mine = {
      abandoned: false,
      failed: false,
      handle: null,
      note: function (text) { if (text) line(log, text, "step stopped"); },
    };
    live = mine;                   // assigned first: a stream can finish inside
                                   // the call that starts it.
    mine.handle = streamAgent({
      agentId: decision.agent_id,
      prompt: question,
      userId: "workspace",
      sessionId: sessionId,
      onStep: function (step) {
        if (mine.abandoned) return;
        if (step.kind === "text") {
          answer.textContent += step.text;
          transcript.scrollTop = transcript.scrollHeight;
          return;
        }
        line(log, step.text, step.kind === "step-failed" ? "step failed" : "step");
      },
      onError: function (detail) {
        if (mine.abandoned) return;
        mine.failed = true;
        block("<p>" + esc(detail) + "</p>", "error");
      },
      onDone: function () {
        if (mine.abandoned) return;
        if (live === mine) live = null;
        // Only when the stream ran to its end with nothing to show. A stream
        // that broke did not finish, and saying it did next to the error that
        // says otherwise is the page contradicting itself.
        if (!mine.failed && !answer.textContent.trim()) {
          answer.textContent = "The agent finished without writing an answer.";
        }
      },
    });
    if (mine.abandoned && mine.handle) mine.handle.close();
  }

  node.querySelectorAll(".starter").forEach(function (button) {
    button.addEventListener("click", function () { run(button.textContent); });
  });
  node.querySelector("#composer").addEventListener("submit", function (event) {
    event.preventDefault();
    var field = node.querySelector("#question");
    var question = field.value.trim();
    if (!question) return;
    field.value = "";
    run(question);
  });

  return {
    ask: function (question) { run(question); },
    pick: function (agentId) {
      run("What should I know about this before I sign it off?", agentId);
    },
    /* For whoever tears this page down. An EventSource left open reconnects. */
    close: function () { stop("Stopped."); },
  };
}

if (typeof module !== "undefined") {
  module.exports = { pickLine, alternatives, opening, mountChat };
}
