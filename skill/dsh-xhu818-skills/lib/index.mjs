// dsh-xhu818-skills — a skill-only DeepSeek Harness plugin bundle.
//
// It contributes one runtime skill, `exam-prep-latex`, which documents the
// pipeline used to turn scanned textbooks + past exam papers + question banks
// into a set of Chinese exam-prep LaTeX documents in which every "importance"
// star rating is backed by a traceable file-level evidence label.
//
// Mirror of the registration shape used by @wxg-prc-cpg/browser-skill-dsh-plugin:
// the catalog entry (name + description) is resident, and the body is only
// materialised when the model invokes the `skill` tool.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const name = "dsh-xhu818-skills";

const SKILL_DIR_URL = new URL("../skills/exam-prep-latex/", import.meta.url);
const SKILL_MD = fileURLToPath(new URL("SKILL.md", SKILL_DIR_URL));

function frontmatterValue(front, key) {
  const re = new RegExp("^" + key + ":[ \\t]*([\\s\\S]*?)(?=\\n[a-zA-Z][a-zA-Z0-9_-]*:|$)", "m");
  const m = front.match(re);
  if (!m) return "";
  return m[1].trim().replace(/^["']/, "").replace(/["']$/, "");
}

function loadSkill() {
  const raw = readFileSync(SKILL_MD, "utf8");
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
    name: frontmatterValue(front, "name") || "exam-prep-latex",
    description:
      frontmatterValue(front, "description") ||
      "Produce Chinese exam-prep LaTeX documents from scanned textbooks, past papers and question banks, with every importance rating backed by file-level evidence.",
    content: body.replace(/^\s*\n/, ""),
  };
}

function registerSkill(ctx) {
  const skills = ctx.get("skills");
  if (skills == null || typeof skills.register !== "function") return () => {};
  let skill;
  try {
    skill = loadSkill();
  } catch (error) {
    console.warn(
      "[dsh-xhu818-skills] could not read SKILL.md: " +
        (error instanceof Error ? error.message : String(error)),
    );
    return () => {};
  }
  return skills.register({
    name: skill.name,
    description: skill.description,
    content: skill.content,
    source: "bundled",
    resourceBase: { kind: "directory", path: fileURLToPath(SKILL_DIR_URL) },
  });
}

/**
 * Register the skill into every exact agent scope.
 *
 * DSH merges skill layers nearest-first (`agent -> preset -> global`), so a
 * plugin-level registration on the agent context is authoritative and cannot be
 * shadowed by a filesystem provider. New agents are handled at `agent/created`;
 * agents that already exist are registered immediately so a plugin reload takes
 * effect without recreating the conversation.
 */
function armAgentScopedSkill(ctx) {
  const registrations = new Map();
  let active = true;

  const registerForAgent = (agent) => {
    if (!active || registrations.has(agent)) return;
    registrations.set(agent, registerSkill(agent.ctx));
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
  const dispose = armAgentScopedSkill(ctx);
  if (typeof ctx.on === "function") ctx.on("dispose", dispose);
  return dispose;
}

export default { name, apply };
