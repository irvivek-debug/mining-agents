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

test("a successful response is the same step, not a new one", () => {
  const steps = S.eventToSteps({
    content: { parts: [{ functionResponse: { id: "1", name: "bq_query",
      response: { success: true, data: [] } } }] },
  });
  assert.equal(steps.length, 1);
  assert.equal(steps[0].kind, "step");
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
