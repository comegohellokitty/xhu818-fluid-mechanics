# -*- coding: utf-8 -*-
r"""
西华大学 818 工程流体力学 —— 考点码 → 重要度星级 总表 + 第二遍判星替换脚本

用法：
    python star_table.py            # 就地替换 03-exams/parts/*.tex 里的 \xstarmark{Kxxx}
    python star_table.py --check    # 只统计，不写文件
    python star_table.py --dir <目录> --glob "*.tex"

设计说明（用户硬要求：重要程度必须有文件依据，不能凭主观印象）：
    第一遍由撰稿子代理在每道题后只写 \xstarmark{Kxxx} 占位；
    第二遍由本脚本用下面的 STAR 表统一替换成 \xstarfull{n}\yiju{依据}。
    每条依据都指向 E1–E6 六份证据文件里的具体页/题号，可逐条回查。
"""

from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 证据文件编号
#   E1 = 8-1考情分析.pptx（slide15 题型分值 / slide16 各题型考法 /
#                         slide25 出题风格 / slide33 逐章重要度）
#   E2 = 9-1考点分析.pptx（slide4 分值分布与章节分层 / slide5 章节分层）
#   E3 = 西华大学 818 工程流体力学考研分析.docx（范围与"真题源于课后习题改编"）
#   E4 = 历年真题 2014–2022 原卷 + 2026 回忆版
#   E5 = 题库（《流体力学与流体机械》试题库（四）等）
#   E6 = 赵琴《流体力学与流体机械》教材第 1–8 章
#
# 星级判定规则（写入 EXAM-SPEC.md 与 src/star_rubric.md）
#   ★★★★★ 计算题出现 >=3 次，或 E1/E2 明写"考试计算题重点"
#   ★★★★  出现 2–3 次，或 E1/E2 明写"重点掌握"
#   ★★★   出现 1 次，或 E1/E2 写"掌握基本概念与公式套用"
#   ★★    真题未出现但属考纲核心/题库常客
#   ★     边缘/复试内容
# ---------------------------------------------------------------------------

STAR: dict[str, tuple[int, str]] = {
    # ---------------- 第 1 章 绪论 ----------------
    "K101": (2, "概念题素材；E6 教材 1.1"),
    "K102": (4, "E4 2022 单选 1（连续介质假设的含义）；E5 题库选择 1"),
    "K103": (3, "E4 2015 填空 1（由 $\\rho=851$ kg/m$^3$ 求重度与动力黏度）"),
    "K104": (3, "E5 题库选择（工程概念）；E6 教材 1.3.2"),
    "K105": (5, "E4 2026 计算 1（牛顿流体斜板静压强）；E5 题库选择 2（汽油＝牛顿流体）"),
    "K106": (4, "E5 题库选择 2（汽油＝牛顿流体）"),
    "K107": (2, "E6 教材 1.3；真题未出现"),
    "K108": (3, "E4 2018 选择 1（作用于流体的质量力）；E5 题库选择 3（体积力有势）"),
    "K109": (3, "E4 2026 简答 2（理想流体）；E6 教材 1.3"),
    # ---------------- 第 2 章 流体静力学 ----------------
    "K201": (4, "E2 slide4；E5 概念题高频"),
    "K202": (4, "E4 2022 单选 5（$dp$ 形式）；E5 题库选择 3（体积力有势）"),
    "K203": (5, "E4 2022 单选 3（测压管水头线坡度）、单选 7（虹吸管）；E1 slide33\"计算题基础入门\""),
    "K204": (4, "E4 2018 选择 3（U 形水银测压计）；E4 2015 填空（U 形压差计）"),
    "K205": (3, "E6 教材 2.4；E5 题库"),
    "K206": (5, "E4 2015 计算（圆柱闸门）；E1 slide33"),
    "K207": (5, "E5 题库计算 1（弧形闸门 $F_x,F_z$ 与力矩）；E1 slide33"),
    # ---------------- 第 3 章 流体运动学 ----------------
    "K301": (5, "E4 各年选择/填空（质点导数与加速度）；E1 slide33\"公式较多，重点记忆\""),
    "K302": (3, "E1 slide16 简答（均匀流的特点）"),
    "K303": (5, "E4 2015 计算 1（流线方程、流动方向判断）"),
    "K304": (4, "E4 2022 单选 4（方管进压缩机求出口密度与质量流量）"),
    "K305": (5, "E4 2022 单选 4；E5 题库"),
    "K306": (4, "E5 题库选择 13（涡量为零）；E6 教材 3.4"),
    # ---------------- 第 4 章 流体动力学基本方程 ----------------
    "K401": (3, "E6 教材 4.1；概念题"),
    "K402": (5, "E1 slide16\"计算题：伯努利方程\"；E1 slide33 与 E2 slide4\"第四章＝考试计算题重点\""),
    "K403": (5, "E4 2022 单选 6（计算点选取）；E4 2026 计算 2（文丘里流量证明）"),
    "K404": (4, "E5 题库计算 4（水泵工况点与节流调节）；E6 教材 4.2"),
    "K405": (5, "E4 2015 计算（水平弯管求 $F_x,F_y$）；E4 2026 计算 3（教材例题 4.12）；E1 slide16"),
    "K406": (2, "E6 教材 4.4"),
    # ---------------- 第 5 章 管路、孔口、管嘴的水力计算 ----------------
    "K501": (5, "E1 slide16 简答\"水头损失的分类及定义\"；E1 slide33；E2 slide5"),
    "K502": (5, "E4 2022 单选 9（两圆管流态判别）；E4 2026 简答 3（层流与雷诺数关系）"),
    "K503": (5, "E4 2022 单选 10（管径减半压强损失 16 倍）；E4 2015 填空（层流平均速度＝0.5 倍最大速度）"),
    "K504": (5, "E4 2022 单选 3；E5 题库选择 10（圆管与方管沿程损失比 0.886）"),
    "K505": (3, "E6 教材 5.4；E2 slide5"),
    "K506": (4, "E4 2015 计算 3（突然缩小水头损失）；E1 slide16"),
    "K507": (5, "E1 slide33；E2 slide5；E4 多卷计算"),
    "K508": (5, "E4 2022 单选 8（圆柱形直角外管嘴 $H_0\\le 9$ m、$l=(3\\sim4)d$）；E4 2026 计算 5"),
    "K509": (5, "E5 题库计算 2（水箱垂直管道出流 $Q$ 与管长 $l$）；E1 slide33"),
    "K510": (4, "E1 slide33；E6 教材 5.7"),
    "K511": (4, "E4 2022 单选 7（虹吸管）；E5 题库选择 8、14"),
    "K512": (4, "E4 2026 简答 1（水击现象）；E6 教材 5.8"),
    # ---------------- 第 6 章 相似理论与量纲分析 ----------------
    "K601": (3, "E4 2020 判断 8（动力相似是流动相似的主导因素）；E1 slide33"),
    "K602": (4, "E4 2014 选择 10；E4 2016 填空 4；E4 2019 判断 2；E4 2022 单选 9；E5 题库选择 12"),
    "K603": (4, "E1 slide33（量纲转化）；E2 slide5"),
    "K604": (4, "E4 2016 填空 3；E4 2018 选择 5；E4 2019 选择 5；E4 2020 选择 7"),
    "K605": (3, "E4 2014 计算 8（溢流坝模型相似）；E5 题库选择 15"),
    # ---------------- 第 7 章 理想流体动力学 ----------------
    "K701": (5, "E4 2015 计算（流函数求速度与流线）；E4 2026 计算 4（证明势函数存在性）"),
    "K702": (4, "E4 2015 计算 8（均匀流＋点源叠加）；E1 slide33\"概念为主\""),
    "K703": (4, "E4 2015 计算 8（求驻点与流线）；E2 slide5"),
    "K704": (3, "E1 slide33\"概念为主\""),
    "K705": (3, "概念题；E6 教材 7.7"),
    "K706": (2, "概念题；E6 教材 7.8"),
    # ---------------- 第 8 章 黏性流体动力学基础 ----------------
    "K801": (3, "E6 教材 8.1；E1 slide33\"会涉及选择题和填空题考点\""),
    "K802": (3, "E6 教材 8.2；E1 slide33"),
    "K803": (3, "E6 教材 8.3、8.7；E1 slide33"),
    "K804": (2, "E4 2015 计算 9（平板摩擦阻力比 $F_1/F_2$）"),
    "K805": (2, "E6 教材 8.8、8.9"),
}

# 旧大纲超纲题（现行 818 初试不考）
OUT_OF_SCOPE: dict[str, str] = {
    "X1": "旧大纲超纲题（明渠流／堰流），现行 818 初试不考",
    "X2": "旧大纲超纲题（气体动力学，教材第 9 章），现行 818 初试不考",
    "X3": "旧大纲超纲题（流体机械／泵与风机，教材第 11--14 章），现行 818 初试不考",
}

MARK_RE = re.compile(r"\\xstarmark\s*\{\s*([A-Za-z]\d{3})\s*\}")


def replacement(code: str) -> str:
    if code in OUT_OF_SCOPE:
        return "\\nandu{超纲}\\yiju{%s}" % OUT_OF_SCOPE[code]
    if code not in STAR:
        raise KeyError(code)
    stars, why = STAR[code]
    return "\\xstarfull{%d}\\yiju{%s}" % (stars, why)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None, help="要处理的目录（默认项目下 latex/03-exams/parts）")
    ap.add_argument("--glob", default="*.tex")
    ap.add_argument("--check", action="store_true", help="只统计不写文件")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]          # xhu818/
    target = Path(args.dir) if args.dir else root / "latex" / "03-exams" / "parts"
    if not target.exists():
        print("目录不存在: %s" % target, file=sys.stderr)
        return 2

    seen: dict[str, int] = {}
    unknown: set[str] = set()
    total_files = 0
    total_marks = 0

    for f in sorted(target.glob(args.glob)):
        text = f.read_text(encoding="utf-8")
        hits = MARK_RE.findall(text)
        if not hits:
            continue
        total_files += 1
        total_marks += len(hits)
        for c in hits:
            seen[c] = seen.get(c, 0) + 1
            if c not in STAR and c not in OUT_OF_SCOPE:
                unknown.add(c)

        def sub(m: re.Match) -> str:
            code = m.group(1)
            try:
                return replacement(code)
            except KeyError:
                return m.group(0)

        new = MARK_RE.sub(sub, text)
        if not args.check and new != text:
            f.write_text(new, encoding="utf-8")

    print("文件数 %d，占位符 %d" % (total_files, total_marks))
    print("涉及的考点码 %d 个：%s" % (len(seen), " ".join(sorted(seen))))
    if unknown:
        print("!! 未在 STAR 表中定义的考点码：%s" % " ".join(sorted(unknown)), file=sys.stderr)
        return 1
    print("剩余未替换的 \\xstarmark 出现次数：%d" % len(MARK_RE.findall(
        "\n".join(f.read_text(encoding="utf-8") for f in target.glob(args.glob)))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
