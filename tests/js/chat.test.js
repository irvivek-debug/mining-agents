/* The sidecar, in two halves.
 *
 * The pure half — which agent is named, which alternatives are offered, what the
 * cold start looks like — is checked directly. The half that touches the DOM is
 * checked through a stub surface, because the one behaviour worth pinning there
 * is not the markup but the stream lifecycle: EventSource reconnects by itself
 * when a connection closes, so a sidecar that abandons a stream without closing
 * it re-asks a hundred-second question forever and bills for every repeat.
 */
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");

const C = require("../../apps/workspace/chat.js");

function loadData() {
  const file = path.join(__dirname, "..", "..", "apps", "shared", "data", "bundle.js");
  const text = fs.readFileSync(file, "utf8");
  return JSON.parse(text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1));
}

const DATA = loadData();

test("the pick line names the agent and gives the reason", () => {
  const line = C.pickLine(
    { agent_id: "S01", reason: "It reads sensor readings.", runners_up: [] },
    DATA
  );
  assert.ok(line.includes("Cascading Failure Impact & Recovery Coordinator"),
    `the line does not name the agent: ${line}`);
  assert.ok(line.includes("It reads sensor readings."));
});

test("the pick line survives an agent id the catalogue does not hold", () => {
  const line = C.pickLine({ agent_id: "NOPE", reason: "because", runners_up: [] }, DATA);
  assert.ok(line.includes("NOPE"));
});

test("the pick line never prints an agent id when a name exists", () => {
  const line = C.pickLine(
    { agent_id: "S01", reason: "It reads sensor readings.", runners_up: [] },
    DATA
  );
  assert.ok(!line.includes("S01"), `the id is jargon and leaked into: ${line}`);
});

test("every persona's sidecar opens with three starters and a valid first pick", () => {
  for (const code of Object.keys(DATA.personas.personas)) {
    const opening = C.opening(code, DATA);
    assert.equal(opening.starters.length, 3, `${code} opened with ${opening.starters.length}`);
    assert.ok(opening.title.length > 0);
  }
});

test("P8 is offered nothing to change to, because it has one agent", () => {
  const R = require("../../apps/workspace/router.js");
  const decision = R.route("what happened last shift?", "P8", DATA);
  assert.deepEqual(C.alternatives(decision, DATA), []);
});

test("a persona with several agents is offered named alternatives", () => {
  const R = require("../../apps/workspace/router.js");
  const decision = R.route("which assets are most at risk?", "P1", DATA);
  const alts = C.alternatives(decision, DATA);
  assert.equal(alts.length, decision.runners_up.length);
  assert.ok(alts.length > 0, "P1 has several agents and offered no alternative at all");
  for (const alt of alts) {
    assert.ok(alt.agent_id && alt.label,
      "an alternative must carry both the id it asks and the name it shows");
    assert.notEqual(alt.label, alt.agent_id,
      "the button shows the agent's name, not its id — the id is jargon");
  }
});

/* ---------- the stream lifecycle ---------- */

/* A surface, not a DOM. mountChat writes its shell with innerHTML and then only
 * ever appends elements it made itself, so a stub that records appends is enough
 * to follow a conversation. Selectors resolve to a stub apiece, remembered, so
 * two lookups of #transcript are the same node — which is the only structural
 * assumption mountChat makes. */
function stubElement(tag) {
  return {
    tagName: tag,
    className: "",
    type: "",
    innerHTML: "",
    children: [],
    listeners: {},
    _text: "",
    get textContent() { return this._text; },
    set textContent(value) { this._text = String(value); },
    appendChild(child) { this.children.push(child); return child; },
    addEventListener(name, fn) {
      (this.listeners[name] = this.listeners[name] || []).push(fn);
    },
  };
}

function stubRoot() {
  const found = {};
  const root = stubElement("aside");
  root.querySelector = function (selector) {
    if (!found[selector]) found[selector] = stubElement("div");
    return found[selector];
  };
  root.querySelectorAll = function () { return []; };
  return root;
}

/* A stream that never finishes on its own, so a test can say when it ends. */
function recorder() {
  const opened = [];
  function streamAgent(options) {
    const handle = {
      options: options,
      closed: false,
      close() { this.closed = true; },
    };
    opened.push(handle);
    return handle;
  }
  return { opened, streamAgent };
}

function mount(code, rec) {
  const root = stubRoot();
  global.document = { createElement: stubElement };
  const chat = C.mountChat(root, code, DATA, { streamAgent: rec.streamAgent });
  return { root, chat, transcript: root.querySelector("#transcript") };
}

test("asking a second question closes the first stream", () => {
  const rec = recorder();
  const { chat } = mount("P1", rec);

  chat.ask("which assets are most at risk?");
  chat.ask("what changed since yesterday?");

  assert.equal(rec.opened.length, 2, "the second question never reached an agent");
  assert.equal(rec.opened[0].closed, true,
    "the first stream is still open — EventSource will keep re-asking it");
  assert.equal(rec.opened[1].closed, false, "the live stream was closed too");
});

test("closing the sidecar closes the stream it left running", () => {
  const rec = recorder();
  const { chat } = mount("P1", rec);
  chat.ask("which assets are most at risk?");
  chat.close();
  assert.equal(rec.opened[0].closed, true);
});

test("an abandoned stream does not write into the transcript it left behind", () => {
  const rec = recorder();
  const { chat, transcript } = mount("P1", rec);

  chat.ask("which assets are most at risk?");
  chat.ask("what changed since yesterday?");
  // agent-stream's close() calls onDone, and a late frame can do the same.
  rec.opened[0].options.onDone();
  rec.opened[0].options.onStep({ kind: "text", text: "half an answer" });

  const answers = transcript.children.filter((c) => c.className === "answer");
  assert.equal(answers.length, 2);
  assert.equal(answers[0].textContent, "",
    "the abandoned answer took text from a stream the reader stopped");

  chat.ask("a third question");
  assert.equal(rec.opened[1].closed, true,
    "a late onDone from the abandoned stream lost track of the live one");
});

test("the abandoned question says it was stopped rather than trailing off", () => {
  const rec = recorder();
  const { chat, transcript } = mount("P1", rec);
  chat.ask("which assets are most at risk?");
  chat.ask("what changed since yesterday?");

  const logs = transcript.children.filter((c) => c.className === "log");
  const stopped = logs[0].children.map((line) => line.textContent);
  assert.ok(stopped.some((t) => t.includes("Stopped")),
    `the abandoned log ends without saying why: ${JSON.stringify(stopped)}`);
});

test("a question reaches the agent the router picked, with the reader's words", () => {
  const R = require("../../apps/workspace/router.js");
  const rec = recorder();
  const { chat } = mount("P1", rec);
  const question = "which assets are most at risk?";

  chat.ask(question);

  assert.equal(rec.opened[0].options.agentId, R.route(question, "P1", DATA).agent_id);
  assert.equal(rec.opened[0].options.prompt, question);
});

test("picking an agent from the panel overrides the router", () => {
  const rec = recorder();
  const { chat } = mount("P1", rec);
  chat.pick("S01");
  assert.equal(rec.opened[0].options.agentId, "S01");
});

test("a finished stream leaves nothing open and says the answer was empty", () => {
  const rec = recorder();
  const { chat, transcript } = mount("P8", rec);
  chat.ask("what happened last shift?");
  rec.opened[0].options.onDone();

  const answers = transcript.children.filter((c) => c.className === "answer");
  assert.ok(answers[0].textContent.length > 0,
    "an agent that wrote nothing leaves the reader with an empty box");

  chat.close();
  assert.equal(rec.opened[0].closed, false,
    "close() re-closed a stream that had already finished");
});

test("one tool call is one line, though it crosses the wire twice", () => {
  const rec = recorder();
  const { chat, transcript } = mount("P1", rec);
  chat.ask("which assets are most at risk?");
  const on = rec.opened[0].options.onStep;
  // A call and its response render to the same sentence: the response frame
  // carries no arguments, so there is nothing more for it to say.
  on({ kind: "step", text: "Reading the sensor readings." });
  on({ kind: "step", text: "Reading the sensor readings." });
  on({ kind: "step", text: "Tracing what else stops if this stops." });
  on({ kind: "step-failed", text: "Couldn't trace what else stops if this stops." });

  const log = transcript.children.filter((c) => c.className === "log")[0];
  assert.deepEqual(log.children.map((p) => p.textContent), [
    "Reading the sensor readings.",
    "Tracing what else stops if this stops.",
    "Couldn't trace what else stops if this stops.",
  ]);
});

test("a stream that broke is not also reported as having finished", () => {
  // agent-stream reports the error and then closes, so onDone always follows
  // onError. Both messages on screen at once contradict each other.
  const rec = recorder();
  const { chat, transcript } = mount("P1", rec);
  chat.ask("which assets are most at risk?");
  rec.opened[0].options.onError("The connection to the agent dropped.");
  rec.opened[0].options.onDone();

  const answer = transcript.children.filter((c) => c.className === "answer")[0];
  assert.equal(answer.textContent, "",
    "the page says the agent finished next to the error saying it did not");
  assert.equal(transcript.children.filter((c) => c.className === "error").length, 1);
});

test("a failed step is marked as failed, and answer text is not logged as a step", () => {
  const rec = recorder();
  const { chat, transcript } = mount("P1", rec);
  chat.ask("which assets are most at risk?");
  const on = rec.opened[0].options.onStep;
  on({ kind: "step", text: "Reading the sensor readings." });
  on({ kind: "step-failed", text: "Couldn't trace what else stops if this stops." });
  on({ kind: "text", text: "Three assets are at risk." });

  const log = transcript.children.filter((c) => c.className === "log")[0];
  assert.equal(log.children.length, 2, "answer text was appended to the activity log");
  assert.ok(log.children[1].className.includes("failed"));

  const answer = transcript.children.filter((c) => c.className === "answer")[0];
  assert.equal(answer.textContent, "Three assets are at risk.");
});
