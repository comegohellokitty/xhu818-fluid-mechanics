// dsh-xhu818-skills — a skill-only DeepSeek Harness plugin bundle.
//
// It contributes two runtime skills:
//
//   1. `exam-prep-latex`  — the production pipeline used to turn scanned
//      textbooks + past exam papers + question banks into a set of Chinese
//      exam-prep LaTeX documents in which every "importance" star rating is
//      backed by a traceable file-level evidence label (E1–E6).
//
//   2. `xhu818-fluid-tutor` — the study-time answering coach. The student hands
//      over a problem he cannot do (photo / scanned PDF / typed text) or a topic
//      he does not understand, and the skill drives the model to answer it out
//      of the already-built knowledge base instead of deriving everything from
//      scratch: worked solution, textbook page + formula numbers, pitfalls, and
//      the 818 importance star with its E1–E6 file evidence.
//
// Mirror of the registration shape used by @wxg-prc-cpg/browser-skill-dsh-plugin:
// the catalog entry (name + description) is resident, and the body is only
// materialised when the model invokes the `skill` tool.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const name = "dsh-xhu818-skills";

// Every skill that lives under ./skills/<dir>/SKILL.md.
const SKILL_DIRS = ["exam-prep-latex", "xhu818-fluid-tutor"];

function skillDirUrl(dirName) {
  return new URL("../skills/" + dirName + "/", import.meta.url);
}

function frontmatterValue(front, key) {
  const re = new RegExp("^" + key + ":[ \\t]*([\\s\\S]*?)(?=\\n[a-zA-Z][a-zA-Z0-9_-]*:|$)", "m");
  const m = front.match(re);
  if (!m) return "";
  return m[1].trim().replace(/^["']/, "").replace(/["']$/, "");
}

function loadSkill(dirUrl, dirName) {
  const skillMd = fileURLToPath(new URL("SKILL.md", dirUrl));
  const raw = readFileSync(skillMd, "utf8");
  let front = "";
  let body = raw;
  if (raw.startsWith("---")) {
    const end = raw.indexOf("\n---", 3);
    if (end !== -1) {
      front = raw.slice(3, end);
      const nl = raw.indexOf("\n", end + 1);
      body = nl === -1 ? "" : raw.slice(nl + 1);
    }
  }
  return {
    name: frontmatterValue(front, "name") || dirName,
    description: frontmatterValue(front, "description") || dirName,
    content: body.replace(/^\s*\n/, ""),
  };
}

function registerSkills(ctx) {
  const skills = ctx.get("skills");
  if (skills == null || typeof skills.register !== "function") return () => {};
  const unregisterAll = [];
  for (const dirName of SKILL_DIRS) {
    const dirUrl = skillDirUrl(dirName);
    let skill;
    try {
      skill = loadSkill(dirUrl, dirName);
    } catch (error) {
      console.warn(
        "[dsh-xhu818-skills] could not read " +
          dirName +
          "/SKILL.md: " +
          (error instanceof Error ? error.message : String(error)),
      );
      continue;
    }
    unregisterAll.push(
      skills.register({
        name: skill.name,
        description: skill.description,
        content: skill.content,
        source: "bundled",
        resourceBase: { kind: "directory", path: fileURLToPath(dirUrl) },
      }),
    );
  }
  return () => {
    for (const unregister of unregisterAll.reverse()) {
      if (typeof unregister === "function") unregister();
    }
  };
}

/**
 * Register the skills into every exact agent scope.
 *
 * DSH merges skill layers nearest-first (`agent -> preset -> global`), so a
 * plugin-level registration on the agent context is authoritative and cannot be
 * shadowed by a filesystem provider. New agents are handled at `agent/created`;
 * agents that already exist are registered immediately so a plugin reload takes
 * effect without recreating the conversation.
 */
function armAgentScopedSkills(ctx) {
  const registrations = new Map();
  let active = true;

  const registerForAgent = (agent) => {
    if (!active || registrations.has(agent)) return;
    registrations.set(agent, registerSkills(agent.ctx));
  };

  let stopCreated = () => {};
  let stopDisposed = () => {};
  if (typeof ctx.on === "function") {
    stopCreated = ctx.on("agent/created", ({ agent }) => registerForAgent(agent));
    stopDisposed = ctx.on("agent/disposed", ({ agent }) => registrations.delete(agent));
  }

  const agents = ctx.get("agents");
  if (agents != null && typeof agents.list === "function") {
    for (const agent of agents.list()) registerForAgent(agent);
  }

  return () => {
    if (!active) return;
    active = false;
    stopDisposed();
    stopCreated();
    for (const unregister of [...registrations.values()].reverse()) unregister();
    registrations.clear();
  };
}

export function apply(ctx) {
  const dispose = armAgentScopedSkills(ctx);
  if (typeof ctx.on === "function") ctx.on("dispose", dispose);
  return dispose;
}

export default { name, apply };
