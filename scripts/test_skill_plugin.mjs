// Smoke test for the installed dsh-xhu818-skills plugin bundle.
//
// It imports the *installed* copy (the one the running DSH host would load) and
// drives it with a fake cordis ctx, mimicking what DSH does: call apply(), then
// fire `agent/created` with an agent whose ctx exposes the `skills` service.
// Asserts that BOTH skills register and that each resourceBase directory exists.
//
// Run:  node xhu818\scripts\test_skill_plugin.mjs

import { existsSync } from "node:fs";
import { pathToFileURL } from "node:url";

const PKG =
  "C:/Users/mate book D14/.dsh/profiles/desktop/node_modules/dsh-xhu818-skills/lib/index.mjs";

const mod = await import(pathToFileURL(PKG).href);

const registered = [];
const registry = {
  register(skill) {
    registered.push(skill);
    return () => {};
  },
};

const handlers = new Map();
const agentCtx = { get: (k) => (k === "skills" ? registry : undefined) };
const rootCtx = {
  get: (k) => {
    if (k === "skills") return registry;
    if (k === "agents") return { list: () => [] };
    return undefined;
  },
  on(event, cb) {
    handlers.set(event, cb);
    return () => {};
  },
};

mod.apply(rootCtx);
handlers.get("agent/created")({ agent: { ctx: agentCtx } });

console.log("plugin name :", mod.name);
console.log("registered  :", registered.length);
for (const s of registered) {
  console.log(
    "-",
    s.name,
    "| source:", s.source,
    "| desc chars:", s.description.length,
    "| body chars:", s.content.length,
    "| dir exists:", existsSync(s.resourceBase.path),
    "|", s.resourceBase.path,
  );
}

const names = registered.map((s) => s.name).sort();
const want = ["exam-prep-latex", "xhu818-fluid-tutor"];
if (JSON.stringify(names) !== JSON.stringify(want)) {
  console.error("FAIL: expected", want.join(", "), "got", names.join(", "));
  process.exit(1);
}
if (registered.some((s) => !existsSync(s.resourceBase.path))) {
  console.error("FAIL: a resourceBase directory does not exist");
  process.exit(1);
}
if (registered.some((s) => s.content.trim().length < 200)) {
  console.error("FAIL: a skill body looks empty");
  process.exit(1);
}
console.log("OK");
