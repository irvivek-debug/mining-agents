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

/* esc comes from shell.js: a global in the browser, where classic script tags
 * share one scope and persona.html loads shell.js first, and a require under
 * Node. Same shape as every sibling module, so nothing here writes into a scope
 * it does not own. */
var CHAT_SHELL = typeof require !== "undefined" ? require("../shared/shell.js") : window;

/* plainAnswer comes from plain.js, which every page loads after shell.js and
 * before this file. The transformation lives there, not here, because it is the
 * one file the activity log and the six screens already share: an answer that
 * named the machinery differently from the log two lines above it would be
 * worse than either wording alone. */
var CHAT_PLAIN = typeof require !== "undefined" ? require("../shared/plain.js") : window;

/* One agent lookup per bundle, not one per name. alternatives() asks for a name
 * per runner-up and the catalogue holds every agent in the estate, so building
 * the map inside _name made a 52-entry object three times to print one line. */
var CHAT_AGENTS = null;
var CHAT_AGENTS_OF = null;

function _agentsById(DATA) {
  if (CHAT_AGENTS_OF === DATA) return CHAT_AGENTS;
  var byId = {};
  DATA.catalog.agents.forEach(function (a) { byId[a.agent_id] = a; });
  CHAT_AGENTS_OF = DATA;
  CHAT_AGENTS = byId;
  return byId;
}

function _name(agentId, DATA) {
  var agent = _agentsById(DATA)[agentId];
  return agent ? agent.display_name : agentId;
}

/* The one place the agent's name is framed. router.js returns a name-free
 * reason so that this prefix is not repeated inside it. */
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
    '<p class="pnote">These agents belong to the ' + CHAT_SHELL.esc(start.title) +
    " role. Start with one of the questions below, or write your own. A real " +
    "answer takes a minute or two; every step the agent takes appears here as " +
    "it happens.</p></div>" +
    '<div class="starters">' +
    start.starters.map(function (q) {
      return '<button class="starter" type="button">' + CHAT_SHELL.esc(q) + "</button>";
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

  // Scroll the transcript, never the page. A stream that ran scrollIntoView on
  // every step would yank the document out from under a reader who is halfway
  // down the left-hand panel, once every few seconds, for the whole minute or
  // two the answer takes.
  function pin() {
    transcript.scrollTop = transcript.scrollHeight;
  }

  function block(html, cls) {
    var div = document.createElement("div");
    div.className = cls;
    div.innerHTML = html;
    transcript.appendChild(div);
    pin();
    return div;
  }

  /* One line per thing the agent is doing — not one per frame on the wire.
   *
   * A tool call arrives twice, as the call and as its response, and both render
   * to the same sentence because the response frame carries no arguments of its
   * own to say anything more with. Printed as they come, a successful call reads
   * as the same line twice in a row, which reads as a rendering fault. A call
   * that fails does not repeat itself: its second line is the failure, and that
   * one is worth every bit of the room it takes.
   *
   * So a line absorbs one repeat and no more. Several tools render a constant
   * sentence whatever their arguments — working out the numbers, running a
   * prediction, asking for your sign-off — and an agent that works out the
   * numbers four times in a row is doing four things, not one. Suppressing all
   * repeats turned a measured ten-call run into a handful of lines, which is
   * under-reporting the only evidence the reader has that the wait is work. */
  function line(log, text, cls) {
    var previous = log.children[log.children.length - 1];
    if (previous && previous.textContent === text && !previous.absorbedRepeat) {
      previous.absorbedRepeat = true;   // its response; the next one is a new call
      return previous;
    }
    var p = document.createElement("p");
    p.className = cls;
    p.textContent = text;
    log.appendChild(p);
    pin();
    return p;
  }

  function run(question, forcedAgentId) {
    stop("Stopped — you asked something else.");

    var decision = forcedAgentId
      ? { agent_id: forcedAgentId, reason: "You picked this one.", runners_up: [] }
      : CHAT_ROUTER.route(question, personaCode, DATA);

    block("<p>" + CHAT_SHELL.esc(question) + "</p>", "you");
    var head = block("<p>" + CHAT_SHELL.esc(pickLine(decision, DATA)) + "</p>", "pick");

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

    /* The answer as the agent wrote it, kept whole.
     *
     * The pane used to append each frame to textContent, which is why a live
     * run printed ### and ** at a shift supervisor: there was no step at which
     * anything looked at the answer. It cannot be an append now either. A frame
     * boundary falls wherever the model put it — mid-word, mid-`**bold**`, mid
     * code span — so the only text it is safe to render is all of it, every
     * time. An 8,239-character answer re-rendered per frame is nothing next to
     * the hundred seconds the reader is already waiting. */
    var wrote = "";

    function say() {
      var said = CHAT_PLAIN.plainAnswer(wrote);
      answer.innerHTML =
        said.html +
        (said.technical
          ? CHAT_SHELL.technicalDrawer(
              '<pre class="mono">' + CHAT_SHELL.esc(said.technical) + "</pre>",
              "the agent's own words for the steps that failed"
            )
          : "");
      pin();
    }

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
          wrote += step.text;
          say();
          return;
        }
        line(log, step.text, step.kind === "step-failed" ? "step failed" : "step");
      },
      onError: function (detail) {
        if (mine.abandoned) return;
        mine.failed = true;
        block("<p>" + CHAT_SHELL.esc(detail) + "</p>", "error");
      },
      onDone: function () {
        if (mine.abandoned) return;
        if (live === mine) live = null;
        // Only when the stream ran to its end with nothing to show. A stream
        // that broke did not finish, and saying it did next to the error that
        // says otherwise is the page contradicting itself.
        // Asked of the text the agent sent, not of the pane it was rendered
        // into. Those are the same fact, and reading it at the source is what
        // keeps this check honest if the rendering ever drops a passage.
        if (!mine.failed && !wrote.trim()) {
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
