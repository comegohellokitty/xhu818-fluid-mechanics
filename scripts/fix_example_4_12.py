# -*- coding: utf-8 -*-
"""
统一订正"教材例题 4.12" → "教材习题 4.12"。

背景（由 ch04 补强子代理逐页核对得出）：
    赵琴《流体力学与流体机械》第 4 章的【例题】只编到「例 4.5」（书 p64，离心风机叶轮），
    全书第 4 章根本没有「例 4.12」；"4.12"是【课后习题】的编号。
    教材习题 4.12 原文（书 p63）：
        "4.12 水流经水平弯管流入大气，已知 d1=100 mm，d2=75 mm，v1=1.5 m/s，θ=30°，
          如习题 4.12 图所示。若不计水头损失，试求水流对弯管的作用力 Fx、Fy。"
    该参数与 2026 考研回忆版计算题第 3 题完全一致 → 命中的是【习题 4.12】。

本脚本只做字面替换，不改动任何其它文字；每处替换都断言命中数，不符即报错退出。
刻意【不动】两处：
  · q-2026recall.tex 中回忆版原话的引号内引文「书上例题 4.12」——那是考生的原话，属引用；
  · ch04.tex 里那段"核对结果"说明——它正是在说明别人把它记作例题是误记。
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (相对路径, 旧串, 新串, 期望命中数)
JOBS = [
    # ---- doc03 历年真题：同一句依据在 8 份试题里重复出现 ----
    ("latex/03-exams/parts/q-2014.tex", "E4 2026 计算 3（教材例题 4.12）", "E4 2026 计算 3（教材习题 4.12）", 2),
    ("latex/03-exams/parts/q-2015.tex", "E4 2026 计算 3（教材例题 4.12）", "E4 2026 计算 3（教材习题 4.12）", 1),
    ("latex/03-exams/parts/q-2016.tex", "E4 2026 计算 3（教材例题 4.12）", "E4 2026 计算 3（教材习题 4.12）", 1),
    ("latex/03-exams/parts/q-2017.tex", "E4 2026 计算 3（教材例题 4.12）", "E4 2026 计算 3（教材习题 4.12）", 2),
    ("latex/03-exams/parts/q-2018.tex", "E4 2026 计算 3（教材例题 4.12）", "E4 2026 计算 3（教材习题 4.12）", 2),
    ("latex/03-exams/parts/q-2019.tex", "E4 2026 计算 3（教材例题 4.12）", "E4 2026 计算 3（教材习题 4.12）", 1),
    ("latex/03-exams/parts/q-2021.tex", "E4 2026 计算 3（教材例题 4.12）", "E4 2026 计算 3（教材习题 4.12）", 4),
    ("latex/03-exams/parts/q-2022.tex", "E4 2026 计算 3（教材例题 4.12）", "E4 2026 计算 3（教材习题 4.12）", 1),

    # ---- doc01 教材精讲 ----
    ("latex/01-textbook/parts/apA-evidence.tex", "E4 2026 计算 3（教材例题 4.12）", "E4 2026 计算 3（教材习题 4.12）", 1),
    ("latex/01-textbook/parts/ch04.tex", "书上动量方程例题 4.12", "书上动量方程习题 4.12", 2),

    # ---- doc02 课后习题册前言 ----
    ("latex/02-exercises/parts/00-front.tex", "教材动量方程例题 4.12", "教材动量方程习题 4.12", 1),

    # ---- doc04 题库册 ----
    ("latex/04-bank/parts/q-b2.tex", "（书上动量方程例题 4.12）", "（书上动量方程习题 4.12）", 2),
    ("latex/04-bank/parts/q-b3.tex", "（教材动量方程例题 4.12）", "（教材动量方程习题 4.12）", 1),
    ("latex/04-bank/parts/a-b3.tex", "（教材例题 4.12）", "（教材习题 4.12）", 1),

    # ---- doc03 2026 回忆版（引号内的考生原话不动，只改我们自己的表述）----
    ("latex/03-exams/parts/q-2026recall.tex", "动量方程（教材例题 4.12 原题）", "动量方程（教材习题 4.12 原题）", 1),
    ("latex/03-exams/parts/q-2026recall.tex", "\\textbf{2 题直接是教材例题}（动量方程 4.12、管嘴）",
                                              "\\textbf{2 题直接是教材例题／习题}（动量方程 4.12、管嘴）", 1),

    # ---- 判星表与写作规范 ----
    ("src/star_table.py", "E4 2026 计算 3（教材例题 4.12）", "E4 2026 计算 3（教材习题 4.12）", 1),
    ("latex/WRITING-SPEC.md", "③**书上动量方程例题 4.12**", "③**书上动量方程习题 4.12**", 1),

    # ---- 技能包里的两份副本 ----
    ("skill/dsh-xhu818-skills/skills/exam-prep-latex/scripts/star_table.py",
     "E4 2026 计算 3（教材例题 4.12）", "E4 2026 计算 3（教材习题 4.12）", 1),
    ("skill/dsh-xhu818-skills/skills/exam-prep-latex/references/WRITING-SPEC.md",
     "③**书上动量方程例题 4.12**", "③**书上动量方程习题 4.12**", 1),
]


def main():
    bad = []
    changed = []
    for rel, old, new, want in JOBS:
        path = os.path.join(ROOT, rel.replace("/", os.sep))
        if not os.path.exists(path):
            bad.append((rel, "文件不存在"))
            continue
        with io.open(path, "r", encoding="utf-8", newline="") as f:
            text = f.read()
        got = text.count(old)
        if got != want:
            bad.append((rel, "命中 %d 处，期望 %d 处：%s" % (got, want, old)))
            continue
        if got == 0:
            continue
        text = text.replace(old, new)
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        changed.append((rel, got))

    print("=" * 72)
    for rel, n in changed:
        print("[改] %-58s %d 处" % (rel, n))
    print("-" * 72)
    print("已修改 %d 个替换项，涉及 %d 个文件" % (len(changed), len(set(r for r, _ in changed))))
    if bad:
        print("=" * 72)
        for rel, why in bad:
            print("[!! ] %s -> %s" % (rel, why))
        print("有 %d 项未按预期完成，退出码 1" % len(bad))
        return 1
    print("全部按预期完成，退出码 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
