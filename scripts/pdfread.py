# -*- coding: utf-8 -*-
r"""便宜地读 PDF / 扫描件：把"提取"和"读进上下文"分开。

核心观念（省钱关键）：
  * OCR 是**本机跑**的，不花 token；花 token 的是"把文字读进模型上下文"。
  * 有文字层的 PDF → `pdftotext` 直接抽，本地零成本、1 秒，**能反复用**。
  * 扫描件 → OCR 结果**早已落盘**在 `xhu818/02-ocr/<库>/`，以后**只 grep 命中行**，
    绝不重跑 OCR、绝不整页整本读。
  * merged.txt 里有 `===== page N =====` 页码标记，grep 它能同时拿到出处页码。

用法：
    # 1) 这份 PDF 有没有文字层？（决定走 pdftotext 还是 OCR）
    python pdfread.py which <pdf> [<pdf> ...]

    # 2) 抽取 PDF 的文字（仅对"有文字层"的 PDF 有意义）
    python pdfread.py text <pdf> [--pages 1-3] [--maxchars 4000]

    # 3) 在已落盘的 OCR 缓存里搜关键词，只打印命中行 + 出处页码
    python pdfread.py grep 水击 [--lib zhqin,konglong,exams,bank10] [--ctx 1] [--max 20]

    # 4) 直接取某本书的某一页（书页码，脚本自动 +9 换算成扫描件页码）
    python pdfread.py page zhqin 121

    # 5) 列出某个库的 merged.txt 路径与页数
    python pdfread.py where [库名]

书页码换算：赵琴教材与孔珑辅导书都是 **书页码 = 扫描件页 − 9**。
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OCR = ROOT / "02-ocr"

# 库名 -> (目录, 书页偏移或 None)
LIBS: dict[str, tuple[str, int | None]] = {
    "zhqin": ("zhqin", 9),        # 赵琴《流体力学与流体机械》教材
    "konglong": ("konglong", 9),  # 孔珑《流体力学》配套辅导书
    "bank10": ("bank10", 9),      # 题库
    "exams": ("exams", None),     # 历年真题（拍照片，无书页码）
}

PDFTOTEXT_CANDIDATES = [
    r"D:\latex\texlive\2024\bin\windows\pdftotext.exe",
    r"C:\Program Files\poppler\Library\bin\pdftotext.exe",
]

PAGE_MARK = re.compile(r"^=+\s*page\s+(\d+)\s*=+\s*$")


def find_pdftotext() -> str | None:
    exe = shutil.which("pdftotext")
    if exe:
        return exe
    for c in PDFTOTEXT_CANDIDATES:
        if Path(c).exists():
            return c
    return None


def run_pdftotext(pdf: Path, first: int | None, last: int | None) -> str:
    exe = find_pdftotext()
    if exe is None:
        return ""
    cmd = [exe, "-enc", "UTF-8"]
    if first:
        cmd += ["-f", str(first)]
    if last:
        cmd += ["-l", str(last)]
    cmd += [str(pdf), "-"]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=180)
    except Exception:
        return ""
    return p.stdout.decode("utf-8", "replace")


def cmd_which(pdfs: list[str]) -> int:
    if not pdfs:
        print("用法：pdfread.py which <pdf> [<pdf> ...]")
        return 2
    print(f"{'前3页字符数':>10}  说明  PDF")
    for s in pdfs:
        p = Path(s)
        if not p.exists():
            print(f"{'--':>10}  文件不存在  {p}")
            continue
        txt = run_pdftotext(p, 1, 3)
        n = len(re.sub(r"\s+", "", txt))
        if n > 200:
            note = "有文字层 → 用 text 模式，0 成本"
        elif n > 0:
            note = "文字层很薄 → 主要靠 OCR 缓存"
        else:
            note = "纯扫描件 → 走 02-ocr 缓存 grep"
        print(f"{n:>10}  {note}  {p}")


def cmd_text(pdf: str, pages: str | None, maxchars: int) -> int:
    p = Path(pdf)
    if not p.exists():
        print(f"文件不存在：{p}")
        return 2
    first = last = None
    if pages:
        m = re.match(r"^(\d+)(?:-(\d+))?$", pages.strip())
        if not m:
            print("--pages 形如 1-3 或 5")
            return 2
        first = int(m.group(1))
        last = int(m.group(2) or m.group(1))
    txt = run_pdftotext(p, first, last)
    clean = re.sub(r"\s+", "", txt)
    print(f"# {p.name}  抽取 {len(clean)} 个非空白字符"
          f"（{'第 %s 页' % pages if pages else '全文'}）")
    if not clean:
        print("（空 —— 说明没有文字层，是纯扫描件；请改用："
              "pdfread.py grep <关键词>）")
        return 0
    body = txt.strip()
    if len(body) > maxchars:
        body = body[:maxchars] + f"\n…（已截断，共 {len(body)} 字符；"
        body += "要看更多就缩小 --pages 范围）"
    print(body)
    return 0


def lib_dirs(names: list[str]) -> list[tuple[str, Path, int | None]]:
    out = []
    for n in names:
        if n not in LIBS:
            continue
        sub, off = LIBS[n]
        d = OCR / sub
        if d.exists():
            out.append((n, d, off))
    return out


def iter_text_files(d: Path):
    merged = d / "merged.txt"
    if merged.exists():
        yield merged
        return
    for f in sorted(d.rglob("page-*.txt")):
        yield f


def cmd_grep(kw: str, names: list[str], ctx: int, maxhits: int) -> int:
    dirs = lib_dirs(names)
    if not dirs:
        print(f"没有可搜的库：{names}（可选 {', '.join(LIBS)}）")
        return 2
    pat = re.compile(re.escape(kw))
    total = 0
    for name, d, off in dirs:
        hits = 0
        for f in iter_text_files(d):
            try:
                lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue
            page = None
            rel = f.relative_to(OCR).as_posix()
            for i, line in enumerate(lines):
                m = PAGE_MARK.match(line.strip())
                if m:
                    page = int(m.group(1))
                    continue
                if pat.search(line):
                    hits += 1
                    total += 1
                    where = f"[{rel}" + (f" p{page}]" if page else "]")
                    if off and page:
                        where += f"（书 p{page - off}）"
                    print(f"--- {name} {where}")
                    lo = max(0, i - ctx)
                    hi = min(len(lines), i + ctx + 1)
                    for j in range(lo, hi):
                        mark = ">>" if j == i else "  "
                        print(f"  {mark} {lines[j].strip()}")
                    if total >= maxhits:
                        print(f"（已达 --max {maxhits}，先看这些；"
                              "要用更窄的关键词再搜）")
                        return 0
        if hits == 0:
            print(f"--- {name}: 无命中")
    if total == 0:
        print("一个都没搜到 —— 换个更独特的数字/术语（如具体数值）再试。")
    return 0


def cmd_page(lib: str, book_page: int) -> int:
    if lib not in LIBS:
        print(f"库名必须是 {', '.join(LIBS)}")
        return 2
    sub, off = LIBS[lib]
    if not off:
        print(f"{lib} 没有书页码偏移，请用 grep 或直接看 02-ocr/{sub}/")
        return 2
    pdf_page = book_page + off
    f = OCR / sub / f"page-{pdf_page:04d}.txt"
    if not f.exists():
        print(f"没有 {f}（书 p{book_page} → 扫描件 p{pdf_page}）")
        return 2
    print(f"# {lib} 书 p{book_page} = 扫描件 p{pdf_page}  {f.name}")
    print(f.read_text(encoding="utf-8", errors="replace").strip())
    print("\n（提醒：OCR 公式多半已坏，公式一律不许照抄；"
          "要么按物理反推，要么注『此处 OCR 不可判读』。）")
    return 0


def cmd_where(names: list[str]) -> int:
    dirs = lib_dirs(names or list(LIBS))
    for name, d, off in dirs:
        files = list(iter_text_files(d))
        total = sum(f.stat().st_size for f in files)
        off_s = f"书页 = 页 − {off}" if off else "无书页码"
        print(f"{name:9} {d}  {len(files)} 个文件 / {total} B  {off_s}")
        for f in files:
            print(f"          {f}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="便宜地读 PDF / 扫描件")
    sub = ap.add_subparsers(dest="mode", required=True)

    p1 = sub.add_parser("which", help="看 PDF 有没有文字层")
    p1.add_argument("pdfs", nargs="*")

    p2 = sub.add_parser("text", help="抽取 PDF 文字（0 成本）")
    p2.add_argument("pdf")
    p2.add_argument("--pages", default=None, help="如 1-3 或 5")
    p2.add_argument("--maxchars", type=int, default=4000)

    p3 = sub.add_parser("grep", help="在已落盘的 OCR 缓存里搜")
    p3.add_argument("kw")
    p3.add_argument("--lib", default="zhqin,konglong,bank10,exams")
    p3.add_argument("--ctx", type=int, default=1)
    p3.add_argument("--max", type=int, default=20)

    p4 = sub.add_parser("page", help="取某本书的某一页（书页码）")
    p4.add_argument("lib")
    p4.add_argument("book_page", type=int)

    p5 = sub.add_parser("where", help="列出 OCR 库位置")
    p5.add_argument("lib", nargs="?", default="")

    a = ap.parse_args()
    if a.mode == "which":
        return cmd_which(a.pdfs)
    if a.mode == "text":
        return cmd_text(a.pdf, a.pages, a.maxchars)
    if a.mode == "grep":
        names = [s.strip() for s in a.lib.split(",") if s.strip()]
        return cmd_grep(a.kw, names, a.ctx, a.max)
    if a.mode == "page":
        return cmd_page(a.lib, a.book_page)
    if a.mode == "where":
        names = [s.strip() for s in a.lib.split(",") if s.strip()]
        return cmd_where(names)
    return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
