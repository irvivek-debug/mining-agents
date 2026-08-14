/* The handover sheet, loaded the way a browser loads it.
 *
 * Two claims are worth pinning here and neither can be pinned from source text.
 * The first is that no block on the page states anything about the connection
 * before /api/runtime has answered — the bug this replaces printed NOT
 * CONNECTED from a constant baked into bundle.js, and read as a working system
 * reporting itself broken. The second is the stream lifecycle behind the Run
 * button: EventSource reconnects by itself whenever a connection closes, so an
 * abandoned stream re-asks a question measured at a little under two minutes of
 * real model time, over and over, and bills for every repeat.
 *
 * So the page scripts are run in a vm against a document small enough to reason
 * about. It is not a browser and does not pretend to be: it resolves ids, keeps
 * text, and forgets the ids belonging to a node whose innerHTML was replaced —
 * which is exactly the fault that would occur if the run control and the sheet
 * were mounted on the same element.
 *
 * The cockpit rides along in one test because it is the other page that says
 * something about the connection in two places at once.
 */
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const ROOT = path.join(__dirname, "..", "..");
const app = (...parts) => path.join(ROOT, "apps", ...parts);

const DATA = (() => {
  const text = fs.readFileSync(app("shared", "data", "bundle.js"), "utf8");
  return JSON.parse(text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1));
})();

const ENTRYPOINTS = DATA.catalog.counts.entrypoints;

/* Every id the real markup carries. Reading them from the file rather than
 * listing them here is what makes a missing mount point a failure: el() throws
 * on an id the page does not hold, and a harness that invented ids would not
 * notice one had gone. */
function idsIn(html) {
  return [...html.matchAll(/id="([^"]+)"/g)].map((m) => m[1]);
}

function makeDom(pageHtml) {
  const registry = new Map();
  const owned = new Map();

  function node(id) {
    const self = {
      id,
      className: "",
      tagName: "DIV",
      _html: "",
      _text: "",
      children: [],
      handlers: {},
      get innerHTML() {
        return self._html;
      },
      set innerHTML(value) {
        // Replacing a node's contents destroys whatever ids were in them. A
        // real DOM does this; a harness that did not would let two mounts share
        // one element and call it working.
        (owned.get(self) || []).forEach((id_) => registry.delete(id_));
        const ids = idsIn(String(value));
        owned.set(self, ids);
        ids.forEach(ensure);
        self._html = String(value);
        self.children = [];
      },
      get textContent() {
        return self._text;
      },
      set textContent(value) {
        self._text = String(value);
      },
      appendChild(child) {
        self.children.push(child);
        return child;
      },
      prepend(child) {
        self.children.unshift(child);
        return child;
      },
      addEventListener(type, fn) {
        (self.handlers[type] = self.handlers[type] || []).push(fn);
      },
      click() {
        (self.handlers.click || []).forEach((fn) => fn({}));
      },
      querySelector: () => null,
      querySelectorAll: () => [],
    };
    return self;
  }

  function ensure(id) {
    if (!registry.has(id)) registry.set(id, node(id));
    return registry.get(id);
  }

  idsIn(pageHtml).forEach(ensure);

  const body = node("body");
  const document = {
    title: "",
    body,
    getElementById: (id) => registry.get(id) || null,
    createElement: () => node(null),
    querySelectorAll: () => [],
    addEventListener: () => {},
  };
  return { document, registry };
}

/* The script tags a page carries, read off the page rather than listed here, so
 * a file added to the markup is a file the harness loads. */
function scriptsOf(pageHtml) {
  return [...pageHtml.matchAll(/<script src="([^"]+)"><\/script>/g)].map((m) =>
    path.join(ROOT, "apps", "workspace", m[1])
  );
}

/** Load a workspace page the way a browser loads it: its own script tags, in
 *  their own order. */
function loadPage(options) {
  const opts = options || {};
  const page = app("workspace", opts.page || "handover.html");
  const pageHtml = fs.readFileSync(page, "utf8");
  const dom = makeDom(pageHtml);

  const fetches = [];
  const sources = [];
  const windowHandlers = {};

  class FakeSource {
    constructor(url) {
      this.url = url;
      this.closed = false;
      this.handlers = {};
      sources.push(this);
    }
    addEventListener(type, fn) {
      (this.handlers[type] = this.handlers[type] || []).push(fn);
    }
    close() {
      this.closed = true;
    }
    emit(type, data) {
      const message = { data: data === undefined ? "" : data };
      if (type === "message" && this.onmessage) this.onmessage(message);
      if (type === "error" && this.onerror) this.onerror(message);
      (this.handlers[type] || []).forEach((fn) => fn(message));
    }
  }

  const sandbox = {
    console,
    URLSearchParams,
    EventSource: FakeSource,
    document: dom.document,
    location: { search: "" },
    addEventListener(type, fn) {
      (windowHandlers[type] = windowHandlers[type] || []).push(fn);
    },
    fetch(url) {
      fetches.push(url);
      if (opts.runtime === "offline") {
        return Promise.reject(new TypeError("Failed to fetch"));
      }
      return Promise.resolve({
        status: 200,
        json: () => Promise.resolve(opts.runtime),
      });
    },
  };

  const context = vm.createContext(sandbox);
  vm.runInContext("var window = globalThis;", context);
  for (const file of scriptsOf(pageHtml)) {
    vm.runInContext(fs.readFileSync(file, "utf8"), context, { filename: file });
  }

  return {
    context,
    dom,
    fetches,
    sources,
    fire: (type) => (windowHandlers[type] || []).forEach((fn) => fn({})),
    el: (id) => dom.registry.get(id),
    // Every block that renders where an agent's words would go.
    blocks: () =>
      [...dom.registry.values()].filter((n) => String(n.id).startsWith("nc-")),
    runtimeLine: () =>
      [...dom.registry.values()].filter((n) => String(n.id).startsWith("rt-")),
  };
}

const CONNECTED = {
  connected: true,
  expected: ENTRYPOINTS,
  deployed: Array.from({ length: ENTRYPOINTS }, (_, i) => `A${i}`),
  missing: [],
};

// A microtask drain: runtimeState() resolves through two chained thens.
const settled = () => new Promise((resolve) => setImmediate(resolve));

test("nothing on the page states the connection before the wire answers", () => {
  const page = loadPage({ runtime: CONNECTED });
  const sheet = page.el("brief").innerHTML;
  assert.ok(page.blocks().length >= 3, `only ${page.blocks().length} blocks asked`);
  assert.match(sheet, /CHECKING/);
  assert.doesNotMatch(sheet, /NOT CONNECTED/);
  assert.doesNotMatch(sheet, /READY/);
  // And the sheet is not quietly carrying the build's opinion either.
  assert.ok(!sheet.includes(DATA.workspace.runtime.reason.slice(0, 40)));
});

test("a connected runtime turns every block over to READY, counting from the wire", async () => {
  const page = loadPage({ runtime: CONNECTED });
  await settled();
  const blocks = page.blocks();
  assert.ok(blocks.length >= 3);
  for (const block of blocks) {
    assert.match(block.innerHTML, /READY/);
    assert.doesNotMatch(block.innerHTML, /NOT CONNECTED/);
    assert.ok(
      block.innerHTML.includes(`${ENTRYPOINTS} of ${ENTRYPOINTS}`),
      `the block did not report the wire's count: ${block.innerHTML}`
    );
  }
  const lines = page.runtimeLine();
  assert.ok(lines.length >= 2, "the sheet lost a runtime line it used to carry");
  for (const line of lines) {
    assert.ok(
      line.textContent.includes(`${ENTRYPOINTS} of ${ENTRYPOINTS}`),
      `a runtime line ignored the wire: ${line.textContent}`
    );
    assert.ok(!line.textContent.includes(DATA.workspace.runtime.reason.slice(0, 40)));
  }
});

test("one page asks /api/runtime once, however many blocks want the answer", async () => {
  const page = loadPage({ runtime: CONNECTED });
  await settled();
  assert.ok(page.blocks().length + page.runtimeLine().length > 1);
  assert.deepEqual(page.fetches, ["/api/runtime"]);
});

/* The cockpit is the other page with more than one thing to say about the
 * connection: a Runtime card at the top and a provenance row at the foot. Two
 * fetches would let one screen print two different answers to one question. */
test("the cockpit asks once too, and its card agrees with its footer", async () => {
  const page = loadPage({ page: "index.html", runtime: CONNECTED });
  await settled();
  assert.deepEqual(page.fetches, ["/api/runtime"]);
  assert.match(page.el("runtime").innerHTML, /DEPLOYED/);
  assert.doesNotMatch(page.el("runtime").innerHTML, /NOT CONNECTED/);
  assert.equal(page.runtimeLine().length, 1);
  assert.ok(page.runtimeLine()[0].textContent.includes(`${ENTRYPOINTS} of ${ENTRYPOINTS}`));
});

test("a server that says no is reported as no, in the server's own words", async () => {
  const page = loadPage({
    runtime: {
      connected: false,
      stage: "cloud run services.list",
      detail: "HTTP 403: caller lacks run.services.list",
      expected: ENTRYPOINTS,
    },
  });
  await settled();
  for (const block of page.blocks()) {
    assert.match(block.innerHTML, /NOT CONNECTED/);
    assert.ok(block.innerHTML.includes("run.services.list"));
    assert.doesNotMatch(block.innerHTML, /READY/);
  }
  assert.match(page.runtimeLine()[0].textContent, /^Not connected/);
});

test("off disk, with no server to ask, the baked constant is the fallback", async () => {
  const page = loadPage({ runtime: "offline" });
  await settled();
  const first = page.blocks()[0].innerHTML;
  assert.match(first, /NOT CONNECTED/);
  assert.ok(
    first.includes(DATA.workspace.runtime.reason.slice(0, 40)),
    "the off-disk case lost the one explanation it does have"
  );
});

test("the run control and the sheet are mounted on different elements", async () => {
  const page = loadPage({ runtime: CONNECTED });
  assert.ok(page.el("run-brief"), "the Run button is not on the page");
  assert.match(page.el("brief").innerHTML, /OMISSION CRITIC/);
  assert.ok(page.el("run").innerHTML.includes("Write this brief now"));
});

test("the run button asks the one agent the catalogue permits, once", () => {
  const page = loadPage({ runtime: CONNECTED });
  page.el("run-brief").click();
  assert.equal(page.sources.length, 1);
  assert.ok(
    page.sources[0].url.startsWith("/api/stream/S12?"),
    `the brief was asked of ${page.sources[0].url}`
  );
  for (const internal of ["S12-SP1", "S12-SP2", "S12-SP3", "S12-CRITIC"]) {
    assert.ok(!page.sources[0].url.includes(internal));
  }
});

test("the agent's steps and prose land in different places", () => {
  const page = loadPage({ runtime: CONNECTED });
  page.el("run-brief").click();
  const source = page.sources[0];
  source.emit(
    "message",
    JSON.stringify({
      content: { parts: [{ functionCall: { id: "1", name: "bq_query", args: {} } }] },
    })
  );
  source.emit("message", JSON.stringify({ content: { parts: [{ text: "Crusher 2 " }] } }));
  source.emit("message", JSON.stringify({ content: { parts: [{ text: "tripped." }] } }));
  assert.equal(page.el("brief-answer").textContent, "Crusher 2 tripped.");
  assert.equal(page.el("brief-log").children.length, 1);
  assert.equal(page.el("brief-log").children[0].className, "step");
});

test("a second run closes the first, rather than leaving it to reconnect", () => {
  const page = loadPage({ runtime: CONNECTED });
  page.el("run-brief").click();
  page.el("run-brief").click();
  assert.equal(page.sources.length, 2);
  assert.equal(page.sources[0].closed, true, "the abandoned stream was left open");
  assert.equal(page.sources[1].closed, false);
});

test("the stream closes when the agent finishes", () => {
  const page = loadPage({ runtime: CONNECTED });
  page.el("run-brief").click();
  page.sources[0].emit("proxy-done");
  assert.equal(page.sources[0].closed, true);
});

test("the stream closes when the connection breaks", () => {
  const page = loadPage({ runtime: CONNECTED });
  page.el("run-brief").click();
  page.sources[0].emit("error");
  assert.equal(page.sources[0].closed, true);
  assert.equal(page.el("brief-log").children[0].className, "step failed");
});

test("the stream closes when the reader leaves the page", () => {
  const page = loadPage({ runtime: CONNECTED });
  page.el("run-brief").click();
  page.fire("pagehide");
  assert.equal(page.sources[0].closed, true);
});

test("a late frame from an abandoned stream does not write into the new answer", () => {
  const page = loadPage({ runtime: CONNECTED });
  page.el("run-brief").click();
  const first = page.sources[0];
  page.el("run-brief").click();
  first.emit("message", JSON.stringify({ content: { parts: [{ text: "stale" }] } }));
  assert.equal(page.el("brief-answer").textContent, "");
});
