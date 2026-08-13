const test = require("node:test");
const assert = require("node:assert");

const S = require("../../apps/workspace/agent-stream.js");

test("a text part becomes answer text, not a step", () => {
  const steps = S.eventToSteps({ content: { parts: [{ text: "Hello." }] } });
  assert.deepEqual(steps, [{ kind: "text", text: "Hello." }]);
});

test("a function call becomes one named step", () => {
  const steps = S.eventToSteps({
    content: { parts: [{ functionCall: { id: "1", name: "bq_query",
      args: { sql: "SELECT * FROM `mining_data.telemetry_stream` LIMIT 10" } } }] },
  });
  assert.deepEqual(steps, [{ kind: "step", text: "Reading the sensor readings" }]);
});

test("a response with no matching call degrades gracefully to the tool's doing line", () => {
  // When a functionResponse arrives whose functionCall was never seen (e.g. the
  // stream started mid-conversation), the calls map is empty and recalled is {}.
  // callLine falls through to TOOL_DOING, which is the most honest fallback: the
  // reader still sees what the agent was doing, even without the specific noun.
  const steps = S.eventToSteps({
    content: { parts: [{ functionResponse: { id: "1", name: "bq_query",
      response: { success: true, data: [] } } }] },
  });
  assert.equal(steps.length, 1);
  assert.equal(steps[0].kind, "step");
  assert.equal(steps[0].text, "Looking up records");
});

test("a failed response is named, not hidden", () => {
  // success is nested under response. At the top level it would read as
  // undefined, which is not false, and the failure would never be reported.
  const steps = S.eventToSteps({
    content: { parts: [{ functionResponse: { id: "9", name: "graph_traverse",
      response: { success: false } } }] },
  });
  assert.equal(steps.length, 1);
  assert.equal(steps[0].kind, "step-failed");
  assert.match(steps[0].text, /Couldn't/);
});

test("a failure names what failed, recalled from the matching call", () => {
  // A functionResponse carries only {id, name, response} — no arguments. The
  // noun has to come from the functionCall that shares its id, or every failure
  // degrades to the tool's verb and the reader learns nothing.
  const calls = {};
  S.eventToSteps({
    content: { parts: [{ functionCall: { id: "7", name: "graph_traverse",
      args: { traversal: "blast_radius" } } }] },
  }, calls);
  const steps = S.eventToSteps({
    content: { parts: [{ functionResponse: { id: "7", name: "graph_traverse",
      response: { success: false } } }] },
  }, calls);
  assert.equal(
    steps[0].text,
    "Couldn't trace what else stops if this stops — that lookup failed."
  );
});

test("a successful response repeats the call's own line, not a generic one", () => {
  const calls = {};
  S.eventToSteps({
    content: { parts: [{ functionCall: { id: "3", name: "bq_query",
      args: { sql: "SELECT 1 FROM `mining_data.assets`" } } }] },
  }, calls);
  const steps = S.eventToSteps({
    content: { parts: [{ functionResponse: { id: "3", name: "bq_query",
      response: { success: true, data: [] } } }] },
  }, calls);
  assert.equal(steps[0].text, "Reading the machine register");
});

test("a thoughtSignature is not a step", () => {
  const steps = S.eventToSteps({
    content: { parts: [{ thoughtSignature: "abc" }, { text: "Right." }] },
  });
  assert.deepEqual(steps, [{ kind: "text", text: "Right." }]);
});

test("an event with no content yields nothing rather than throwing", () => {
  assert.deepEqual(S.eventToSteps({}), []);
  assert.deepEqual(S.eventToSteps({ content: {} }), []);
  assert.deepEqual(S.eventToSteps(null), []);
});

test("the model's own prose is passed through unaltered", () => {
  const leak = "The tool call `graph_traverse` failed with `success=false`";
  const steps = S.eventToSteps({ content: { parts: [{ text: leak }] } });
  assert.equal(steps[0].text, leak);
});

test("the stream url carries the prompt and the session as query parameters", () => {
  const url = S.streamUrl({
    agentId: "S01", prompt: "what now?", userId: "u", sessionId: "s",
  });
  assert.ok(url.startsWith("/api/stream/S01?"));
  assert.ok(url.includes("prompt=what+now%3F") || url.includes("prompt=what%20now%3F"));
  assert.ok(url.includes("user_id=u"));
  assert.ok(url.includes("session_id=s"));
});

/* Minimal fake EventSource — just enough to exercise the lifecycle.
 * close() records that it was called; _emit() drives the registered handlers;
 * onerror is the slot the module assigns directly. Assertions stay on
 * observable effects: was the source closed, did the callbacks fire. */
class FakeEventSource {
  constructor() {
    this._listeners = {};
    this._closed = false;
    this.onerror = null;
  }
  addEventListener(type, fn) {
    if (!this._listeners[type]) this._listeners[type] = [];
    this._listeners[type].push(fn);
  }
  close() { this._closed = true; }
  _emit(type, data) {
    const msg = { data: typeof data === "string" ? data : JSON.stringify(data) };
    (this._listeners[type] || []).forEach(function (fn) { fn(msg); });
  }
}

test("proxy-done closes the source and fires onDone exactly once", () => {
  const src = new FakeEventSource();
  let doneCount = 0;
  S._streamAgentWithSource(src, { onDone: () => { doneCount++; } });

  src._emit("proxy-done", "");
  assert.equal(src._closed, true, "source should be closed after proxy-done");
  assert.equal(doneCount, 1, "onDone should fire exactly once");

  // A second proxy-done must be a no-op — finished flag guards re-entry.
  src._closed = false; // reset sentinel to detect any spurious second close
  src._emit("proxy-done", "");
  assert.equal(src._closed, false, "second proxy-done should not re-close");
  assert.equal(doneCount, 1, "onDone should still have fired exactly once");
});

test("onerror before any event closes the source and fires onError", () => {
  const src = new FakeEventSource();
  let errorMsg = null;
  S._streamAgentWithSource(src, { onError: (msg) => { errorMsg = msg; } });

  src.onerror();
  assert.equal(src._closed, true, "source should be closed after onerror");
  assert.ok(errorMsg && errorMsg.length > 0, "onError should receive a message");
});

test("proxy-error then proxy-done fires onDone exactly once; proxy-error alone does not close", () => {
  // proxy-error must not close the source — proxy-done is guaranteed to follow
  // and the error detail would otherwise be the last thing the user sees.
  const src = new FakeEventSource();
  let errorMsg = null;
  let doneCount = 0;
  S._streamAgentWithSource(src, {
    onError: (msg) => { errorMsg = msg; },
    onDone: () => { doneCount++; },
  });

  src._emit("proxy-error", JSON.stringify({ detail: "quota exceeded" }));
  assert.equal(src._closed, false, "proxy-error alone must not close the source");
  assert.equal(errorMsg, "quota exceeded", "onError should receive the detail text");
  assert.equal(doneCount, 0, "onDone must not fire from proxy-error");

  src._emit("proxy-done", "");
  assert.equal(src._closed, true, "source should be closed after proxy-done");
  assert.equal(doneCount, 1, "onDone should fire exactly once after proxy-done");
});
