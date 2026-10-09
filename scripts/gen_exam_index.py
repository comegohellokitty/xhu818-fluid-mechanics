# -*- coding: utf-8 -*-
r"""由 src/star_table.py 生成答疑技能用的考点码表 exam-index.md。

用法：
    python gen_exam_index.py                 # 写到默认位置（技能包 references/）
    python gen_exam_index.py --out <文件>
    python gen_exam_index.py --check         # 只统计码数与星数分布，不写文件

设计原则：星数与依据**全部取自 star_table.py**，本脚本不新增任何判断，
避免"两处表各自漂移"。技能 SKILL.md 里引用的 references/exam-index.md
就是本脚本的产物。
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # xhu818/scripts
ROOT = HERE.parent                              # xhu818
STAR_TABLE = ROOT / "src" / "star_table.py"
DEFAULT_OUT = (ROOT / "skill" / "dsh-xhu818-skills" / "skills"
               / "xhu818-fluid-tutor" / "references" / "exam-index.md")

CHAPTERS = {
    "1": "绪论",
    "2": "流体静力学",
    "3": "流体运动学",
    "4": "流体动力学基本方程",
    "5": "管路、孔口、管嘴的水力计算",
    "6": "相似理论与量纲分析",
    "7": "理想流体动力学",
    "8": "黏性流体动力学基础",
}

EVIDENCE = [
    ("E1", "8-1考情分析.pptx（slide15 题型分值 / slide16 各题型考法 / "
           "slide25 出题风格 / slide33 逐章重要度）"),
    ("E2", "9-1考点分析.pptx（slide4 分值分布与章节分层 / slide5 章节分层）"),
    ("E3", "西华大学 818 工程流体力学考研分析.docx（范围与"
           "「真题源于课后习题改编」）"),
    ("E4", "历年真题 2014--2022 原卷 + 2026 回忆版"),
    ("E5", "题库（《流体力学与流体机械》试题库（四）等）"),
    ("E6", "赵琴《流体力学与流体机械》教材第 1--8 章"),
]

SUBJECT_CODES = ("2014=818、2015=819、2016=817、2017=819、2018=819、"
                 "2019=821、2020=818、2021=818、2022=818")


def load_star_table():
    spec = importlib.util.spec_from_file_location("star_table", STAR_TABLE)
    if spec is None or spec.loader is None:
        raise SystemExit(f"无法加载 {STAR_TABLE}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.STAR, mod.OUT_OF_SCOPE


def stars(n: int) -> str:
    n = max(0, min(5, int(n)))
    return "★" * n + "☆" * (5 - n)


def build(star: dict, out_of_scope: dict) -> str:
    lines: list[str] = []
    lines.append("# 考点码表（K101–K805）与星级依据\n")
    lines.append("> 本表由 `xhu818/scripts/gen_exam_index.py` 从 "
                 "`xhu818/src/star_table.py` **自动生成，请勿手改**；"
                 "要改星数请改那张表后重新生成。\n")
    lines.append("## 星级判定规则\n")
    lines.append("| 星级 | 判据 |")
    lines.append("| --- | --- |")
    lines.append("| ★★★★★ | 计算题出现 ≥3 次，或 E1/E2 明写"
                 "「考试计算题重点」 |")
    lines.append("| ★★★★ | 出现 2–3 次，或 E1/E2 明写「重点掌握」 |")
    lines.append("| ★★★ | 出现 1 次，或 E1/E2 写「掌握基本概念与公式套用」 |")
    lines.append("| ★★ | 真题未出现，但属考纲核心／题库常客 |")
    lines.append("| ★ | 边缘／复试内容 |\n")
    lines.append("## 证据文件（E1–E6）\n")
    for code, desc in EVIDENCE:
        lines.append(f"- **{code}** = {desc}")
    lines.append("")

    by_chapter: dict[str, list[tuple[str, int, str]]] = {}
    for code, (n, why) in star.items():
        ch = code[1] if len(code) > 1 else "?"
        by_chapter.setdefault(ch, []).append((code, n, why))

    for ch in sorted(by_chapter):
        rows = sorted(by_chapter[ch], key=lambda r: r[0])
        title = CHAPTERS.get(ch, f"第 {ch} 章")
        lines.append(f"## 第 {ch} 章　{title}\n")
        lines.append("| 考点码 | 重要度 | 依据 |")
        lines.append("| --- | --- | --- |")
        for code, n, why in rows:
            lines.append(f"| `{code}` | {stars(n)} | {why} |")
        lines.append("")

    lines.append("## 超纲码（现行 818 初试考纲外）\n")
    lines.append("| 码 | 含义 |")
    lines.append("| --- | --- |")
    for code, desc in out_of_scope.items():
        lines.append(f"| `{code}` | {desc} |")
    lines.append("")
    lines.append("## 速查\n")
    lines.append(f"- **科目代码逐年（不得归一化）**：{SUBJECT_CODES}")
    lines.append("- **历年真题结构、2026 回忆版题目、题库来源（B1/B2/B3）**："
                 "见同插件另一技能的 `../../exam-prep-latex/references/"
                 "EXAM-SPEC.md`")
    lines.append("- **考点名与逐章编排（127 个考点，含各章已知教材订正）**："
                 "见同目录 `topic-index.md`")
    lines.append("- **素材路径、页码偏移、OCR 目录、脚本用法**："
                 "见同目录 `materials-map.md`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    star, oos = load_star_table()
    dist: dict[int, int] = {}
    for _, (n, _why) in star.items():
        dist[n] = dist.get(n, 0) + 1

    print(f"考点码 {len(star)} 个；星数分布 "
          + "、".join(f"{k}★={dist[k]}" for k in sorted(dist, reverse=True)))
    print(f"超纲码 {len(oos)} 个：" + "、".join(oos))
    if args.check:
        return 0

    text = build(star, oos)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"已写入 {out}（{len(text)} 字符）")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
