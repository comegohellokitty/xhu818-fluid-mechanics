# -*- coding: utf-8 -*-
"""把 ch06.tex 的 13 个 kaodian 第一参数从「顺序号 1..13」改成真正的星数。
星数取各框自己正文里那句「重要度 \\xstarfull{n}}」的值（文件内有 E1-E6 依据）。
"""
import pathlib

P = pathlib.Path(
    r"C:\Users\mate book D14\Documents\deepseek-harness\default-workspace"
    r"\xhu818\latex\01-textbook\parts\ch06.tex"
)

PAIRS = [
    (1, 3, r"\begin{kaodian}{1}{力学相似的三个层次}"),
    (2, 3, r"\begin{kaodian}{2}{相似三定理（相似正定理、逆定理、$\pi$ 定理）}"),
    (3, 4, r"\begin{kaodian}{3}{三大相似准则：$\Rey$、$\Eu$、$\Fr$}"),
    (4, 3, r"\begin{kaodian}{4}{其他准则：$\mathrm{Ma}$、$\mathrm{St}$、$\mathrm{We}$、$\mathrm{Ca}$（一般了解）}"),
    (5, 3, r"\begin{kaodian}{5}{定性准则与非定性准则——相似准则的选取原则}"),
    (6, 4, r"\begin{kaodian}{6}{量纲与单位：量纲和谐性原理的前提}"),
    (7, 4, r"\begin{kaodian}{7}{量纲和谐原理（教材正式名：量纲和谐性原理，书 p108）}"),
    (8, 4, r"\begin{kaodian}{8}{量纲分析方法一：瑞利法（Rayleigh）}"),
    (9, 4, r"\begin{kaodian}{9}{量纲分析方法二：$\pi$ 定理（布金汉定理）}"),
    (10, 4, r"\begin{kaodian}{10}{典型例题一：圆管沿程压强损失 $\Delta p$（教材例 6.3，书 p110--111）}"),
    (11, 4, r"\begin{kaodian}{11}{典型例题二：绕流阻力与孔口流量}"),
    (12, 2, r"\begin{kaodian}{12}{泵与风机的相似换算公式（教材 6.3.1，书 p112--113）}"),
    (13, 2, r"\begin{kaodian}{13}{比转速 $n_s$ 与标准状态换算（了解）}"),
]

t = P.read_text(encoding="utf-8")
before = t.count(r"\begin{kaodian}{")
changed = 0
for seq, star, old in PAIRS:
    n = t.count(old)
    if n != 1:
        raise SystemExit(f"匹配数 {n} != 1: {old}")
    assert star in (1, 2, 3, 4, 5), star
    new = old.replace(f"{{kaodian}}{{{seq}}}", f"{{kaodian}}{{{star}}}", 1)
    t = t.replace(old, new, 1)
    changed += 1

P.write_text(t, encoding="utf-8", newline="")
print("kaodian 总数(before):", before)
print("已改:", changed)

# 复核：第一参数必须都是 1..5
import re

args = re.findall(r"\\begin\{kaodian\}\{(\d+)\}", P.read_text(encoding="utf-8"))
print("改后第一参数:", args)
assert all(1 <= int(a) <= 5 for a in args), args
assert len(args) == 13, len(args)
print("OK")
