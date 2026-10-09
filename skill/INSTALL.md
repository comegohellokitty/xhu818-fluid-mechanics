# 安装 `exam-prep-latex` 技能

本目录 `dsh-xhu818-skills/` 就是一个自包含的 **DeepSeek Harness 插件包**（skill-only bundle），
它只做一件事：通过 `ctx.get("skills").register(...)` 把 `skills/exam-prep-latex/SKILL.md`
注册成运行时技能。不需要注册表、不需要发布到 npm。

```
dsh-xhu818-skills/
├── package.json          name=dsh-xhu818-skills、main/exports → lib/index.mjs、dsh.bundle.patch
├── cordis.patch.yml      insert 一条 id=xhu818-exam-prep-latex 的 loader 条目
├── lib/index.mjs         真正的注册逻辑（读 SKILL.md、剥 frontmatter、注册进每个 agent 作用域）
└── skills/exam-prep-latex/
    ├── SKILL.md          技能正文
    ├── assets/           可直接复用的 xhu818.sty
    ├── references/       WRITING-SPEC / EXAM-SPEC / star_rubric
    └── scripts/          OCR 与判星脚本
```

## 安装步骤（Windows 上的 DSH 桌面版实测路径）

```powershell
# 1) 把整个包拷进 profile 的 node_modules
$prof = "C:\Users\<你>\.dsh\profiles\desktop"
Copy-Item -Recurse -Force ".\dsh-xhu818-skills" "$prof\node_modules\dsh-xhu818-skills"

# 2) 在 profile 的 package.json 里，把包名加进 dsh.profile.bundles
#    （注意：**不要**加进 dependencies——它是本地包，加了会让包管理器去 registry 找）
#    dsh.profile.bundles 末尾加一行：  "dsh-xhu818-skills"

# 3) 让 harness 重新加载 profile
```

重新加载后，技能目录里就会出现 `exam-prep-latex`。本机实测**不需要重启程序**：改完
`package.json` 后技能目录在一次工具调用内就被刷新了；若没出现，重启一次即可。

## 原理

DSH 的技能按 `agent → preset → global` 就近合并。文件系统 provider 发现的同名技能会遮蔽
插件级注册，因此 `lib/index.mjs` 用 `agent.ctx` 精确注册到每个 agent 作用域：

- `ctx.on("agent/created")` → 新 agent 建立时注册；
- `ctx.get("agents").list()` → 让**已经存在**的会话在插件热重载后立即生效，无需重开对话；
- 返回的 disposer 在插件卸载 / agent 销毁时反注册。

注册的形状（与官方 `@wxg-prc-cpg/browser-skill-dsh-plugin` 一致）：

```js
ctx.get("skills").register({
  name, description, content,          // content = SKILL.md 去掉 YAML frontmatter 的正文
  source: "bundled",
  resourceBase: { kind: "directory", path: <技能目录> },   // 让技能里的 assets/ scripts/ 可寻址
});
```

## 只想要技能正文？

不装插件也行：直接把 `skills/exam-prep-latex/` 整个目录放进你惯用的技能目录，
或干脆把 `SKILL.md` 当文档读——它本身已经写清了从"扫描教材 + 历年真题 + 题库"到
五份中文 LaTeX 复习资料的完整流程。
