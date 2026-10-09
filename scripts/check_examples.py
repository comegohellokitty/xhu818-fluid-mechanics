# -*- coding: utf-8 -*-
"""列出赵琴教材 26 道编号例题在 OCR 页面里的出现情况与篇幅。

用途：主代理核对 7 个子代理插入的《教材精讲》例题是否与教材原文对得上，
并一眼看出哪道例题的题目或解答在扫描页里缺失（缺失就不许代答）。

书页码 = PDF 页码 - 9；OCR 文件为 02-ocr\\zhqin\\page-%04d.txt。
"""
import pathlib
import re

OCR = pathlib.Path(
    r"C:\Users\mate book D14\Documents\deepseek-harness\default-workspace\xhu818\02-ocr\zhqin"
)

# (例题号, 书页, 预期 PDF 页)  预期页只是起点，实际会在 ±2 页内搜索
EXAMPLES = [
    ("2.1", "p15", 24), ("2.2", "p17", 26), ("2.3", "p21", 30),
    ("2.4", "p23", 32), ("2.5", "p24", 33),
    ("3.1", "p34", 43), ("3.2", "p37", 47),
    ("4.1", "p58", 67), ("4.2", "p58-59", 67), ("4.3", "p61", 70),
    ("4.4", "p62", 71), ("4.5", "p63-64", 73),
    ("5.1", "p80-81", 89), ("5.2", "p81", 90), ("5.3", "p88-89", 97),
    ("6.1", "p105-106", 114), ("6.2", "p108-109", 117), ("6.3", "p110-111", 119),
    ("7.1", "p121", 130), ("7.2", "p123", 132), ("7.3", "p123", 132), ("7.4", "p146", 155),
    ("8.1", "p156-157", 165), ("8.2", "p171-172", 180), ("8.3", "p171-172", 180),
    ("8.4", "p175", 184),
]

# 例题本体可能跨页，向后多看两页
SPAN = range(-2, 4)

# 一道例题的正文在遇到下一个「例 N.M」或节标题时终止
STOP = re.compile(r"^\s*(例\s*\d+\.\d+|习题\s*\d+\.\d+|\d+\.\d+(\.\d+)?\s+\S)")


def load(page: int):
    f = OCR / ("page-%04d.txt" % page)
    if not f.exists():
        return None
    return f.read_text(encoding="utf-8", errors="replace").splitlines()


def main() -> None:
    known = {e[0]: e for e in EXAMPLES}
    for num, bookpage, guess in EXAMPLES:
        pat = re.compile(r"例\s*%s\b" % re.escape(num))
        hits = []
        for p in range(guess - 2, guess + 5):
            lines = load(p)
            if lines is None:
                continue
            for i, ln in enumerate(lines):
                if pat.search(ln):
                    hits.append((p, i, lines))
        if not hits:
            print("例%-5s 书 %-9s  !! OCR 中未找到（预期 PDF 第 %d 页附近）" % (num, bookpage, guess))
            continue
        for page, idx, lines in hits:
            # 统计从这条到下一个例题/节标题之间的行数 = 本体粗略篇幅
            body = 0
            for ln in lines[idx + 1:]:
                if STOP.match(ln):
                    break
                if ln.strip():
                    body += 1
            # 是否含「解」= 有解答
            tail = lines[idx:idx + body + 1]
            has_solve = any(re.search(r"^\s*解\s*[:：]?", l) for l in tail)
            nxt = ""
            for ln in lines[idx + 1:]:
                if STOP.match(ln):
                    nxt = ln.strip()[:34]
                    break
            print(
                "例%-5s 书 %-9s PDF %-4d 行 %-4d 正文 %-3d 行  解答%s  下一段: %s"
                % (num, bookpage, page, idx + 1, body, "有" if has_solve else "无", nxt)
            )


if __name__ == "__main__":
    main()
