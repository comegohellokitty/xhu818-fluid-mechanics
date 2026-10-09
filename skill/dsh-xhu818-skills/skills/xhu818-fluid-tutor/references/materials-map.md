# 素材地图：xhu818 项目的所有文件在哪

工作区根目录：`C:\Users\mate book D14\Documents\deepseek-harness\default-workspace`
项目目录：`<工作区>\xhu818\`

---

## 1. 知识库（答疑时**先查这里**，纯文本 LaTeX，可直接 grep）

| 目录 | 内容 | 说明 |
|---|---|---|
| `xhu818\latex\01-textbook\parts\` | **教材精讲正文**：`00-kaoqing.tex`（考情总览）、`ch01.tex`–`ch08.tex`、`apA-evidence.tex`（证据表） | 赵琴教材第 1–8 章的完整改写；**127 个考点框**（`kaodian`）、公式盒（`gongshi`，带教材式号）、**26 道教材例题的完整题目与解答**（`liti`＋`jie`）、真题挂靠（`zhenti`）、易错（`yicuo`）、书上没有的方法（`banfa`）。**问知识点一律从这里答。** |
| `xhu818\latex\02-exercises\parts\` | 课后习题：`q-ch01`–`q-ch08`（题目）、`a-ch01`–`a-ch08`（解答） | 教材课后习题全文＋解答，题在前答案在后 |
| `xhu818\latex\03-exams\parts\` | 历年真题：`q-2014`…`q-2022`、`q-2026recall`；答案：`a-2014`…`a-2022`；`apA-scan.tex`（原卷影印页） | **真题最常被问，答案已有**。2021/2022/2026 的答案是编者自做，不是官方 |
| `xhu818\latex\04-bank\parts\` | 题库：`q-b1`/`q-b2`/`q-b3`＋`a-b1`/`a-b2`/`a-b3` | B1＝《流体力学与流体机械》试题库（四）；B2＝赵琴配套选择题库；B3＝试卷 3（客观题） |
| `xhu818\latex\05-konglong\parts\` | 孔珑配套辅导书题选：`q-ch01`–`q-ch08`＋`a-ch01`–`a-ch08` | 只收 818 考纲内的题；题在前答案在后 |
| `xhu818\latex\common\xhu818.sty` | 样式包（星级/依据/考点/公式/例题/解答等全部盒子） | 要输出 PDF 时用 |
| `xhu818\latex\WRITING-SPEC.md`、`EXAM-SPEC.md` | 写作与真题规范 | 含全部已知踩坑 |
| `xhu818\src\star_table.py` | **考点码 → 星级＋依据 总表**（`STAR` 字典，**56** 个码：第 1–8 章分别 9/7/6/6/12/5/6/5）与超纲码 `OUT_OF_SCOPE` | 判考频的唯一权威表 |
| `xhu818\src\star_rubric.md` | 证据文件 E1–E6 清单与星级判定规则 | |
| `xhu818\src\bank_answers.md` | 题库 B2 的手写答案转录 | |

**证据文件编号**：E1＝`8-1考情分析.pptx`（slide15 题型分值／slide16 各题型考法／slide25 出题风格／slide33 逐章重要度）；E2＝`9-1考点分析.pptx`；E3＝`西华大学 818工程流体力学考研分析.docx`；E4＝历年真题 2014–2022＋2026 回忆版；E5＝题库；E6＝赵琴教材。

---

## 2. 教材原文 OCR（**兜底**用，公式基本全坏）

| 路径 | 内容 |
|---|---|
| `xhu818\02-ocr\zhqin\page-%04d.txt`（＋`merged.txt`） | **赵琴教材全部 334 页** OCR。**书页码 = 文件名页码 − 9**（例：`page-0089.txt` ＝ 书 p80） |
| `xhu818\02-ocr\konglong\page-%04d.txt` | 孔珑教材（`流体力学.pdf`，58.32 MB）OCR，164 页 |
| `xhu818\02-ocr\exams\<年份>\merged.txt` | 历年试题/答案扫描件 OCR |
| `xhu818\02-ocr\bank10\merged.txt` | 题库 B2 的 OCR（赵琴配套选择题库） |
| `xhu818\02-ocr\logs\` | 批处理日志；`_failures.txt` 若存在即代表有页没 OCR 成功（当前全库无） |

**铁律**：OCR 里的分式、下标、根号、希腊字母、指数**全部不可信**（例：例 4.3 的 $F_x$ 被识别成 `F、`、$v_2$ 算成 `2= =1.875（m/s) 0.4`；例 8.4 的一步是 `-24=110.6`）。要么按物理反推，要么写"此处 OCR 不可判读"，**不许照抄、不许猜数**。

---

## 3. 原始素材（学生最初给的，可能会被移动）

- `C:\Users\mate book D14\Downloads\`
  - `11.流体力学与流体机械电子版.pdf`（60.06 MB）＝ **赵琴教材扫描件**
  - `2014年试题.pdf`…`2021年试题.pdf`、`2022-818工程流体力学.pdf`（0.28–6.78 MB）
  - `2014年答案.pdf`…`2020年答案.pdf`（2.72–16.94 MB，手机拍照，**官方答案只有这七年**）
  - `10.pdf`、`17.pdf`、`10.西华选择题题库（精简版）.pdf`
  - `1.工程流体力学各知识点速过.pdf`、`西华大学   818工程流体力学考研分析.pdf`
- `C:\Users\mate book D14\Documents\WeChat Files\wxid_f27188h0yca722\FileStorage\File\2026-10\`
  - `流体力学.pdf`（58.32 MB）＝ **孔珑教材**
  - `孔珑 工程流体力学学习指导及习题解答 978-7-302-37859-4_13803116.pdf`（24.57 MB）＝ **配套辅导书**
- `xhu818\01-extracted\`：`pdftotext` 抽出的文本（29 个）。有实质内容的只有：
  `8-1考情分析.pptx.txt`(13916 B)、`9-1考点分析.pptx.txt`(2485 B)、`西华大学   818工程流体力学考研分析.txt`(3955 B)、`1.工程流体力学各知识点速过.txt`(153765 B)、`10.txt`(5023 B)、`2015年试题.txt`(5757 B)、`26考研 真题回忆.txt`(440 B)、`zhqin_toc.md`（赵琴目录）。
  **其余试题/答案/教材的 txt 都只有 3–5 字节**（纯扫描件，没文字层）。
- `xhu818\00-images\`：我渲染的 64 张 PNG 预览（30.3 MB，**已被 .gitignore 排除**）。

---

## 4. 成品 PDF（五份，可直接给学生）

仓库 `xhu818\pdf\`，同时复制到学生桌面 `C:\Users\mate book D14\Desktop\k\`：

| 文件 | 页数 | 字节 | SHA256 前缀 |
|---|---|---|---|
| `XHU818-01-教材精讲.pdf` | 226 | 1926599 | 4E1F3EFC1B3C71EB |
| `XHU818-02-课后习题.pdf` | 178 | 1349009 | 2CC389713E87BF3A |
| `XHU818-03-历年真题与答案.pdf` | 163 | 1234588 | 5BBC1C837378F671 |
| `XHU818-04-题库汇编.pdf` | 56 | 535986 | 29F46526295F46DE |
| `XHU818-05-孔珑题选.pdf` | 182 | 1310128 | D46DD7090CF43ACB |

- 含原卷影印件的加长版（仅本机、不进仓库）：`xhu818\pdf-local\XHU818-03-历年真题与答案（含原卷影印附录）.pdf`（208 页 / 28.92 MB）。
- 影印扫描件本体：`xhu818\latex\03-exams\figures\q2014.pdf`…`q2022.pdf`（9 个）。

---

## 5. 工具与环境

- Python：`D:\anaconda\python.exe`（3.12）。装了 `rapidocr-onnxruntime 1.4.4`、`onnxruntime 1.31.0`、`PyMuPDF 1.28.2`。
  - 打印中文要先 `$env:PYTHONIOENCODING='utf-8'`。
  - **数行数用 python**：PowerShell 的 `Get-Content` 会丢空行（`.Count` 得非空行数，偏低约 30%）；字节数 `p.stat().st_size` 一直准确。
- OCR 脚本：`python xhu818\scripts\ocr_pdf.py --pdf <文件> --out <目录> [--first N] [--last N] [--px 1800] [--merge]`
- **读 PDF／扫描件脚本**：`python xhu818\scripts\pdfread.py {which|text|grep|page|where} …` —— **优先用它，已落盘的 OCR 结果不要再重跑**（详见 `reading-pdfs.md`）
- 考点码表生成：`python xhu818\scripts\gen_exam_index.py`（由 `xhu818\src\star_table.py` 生成本技能里的 `references/exam-index.md`）
  （单页 3 次重试、单页失败只记 `_failures.txt` 不中断；含 `install_safe_cv2_resize()` 绕开 OpenCV 间歇崩溃）。
- poppler 24.03：`pdftoppm`（只支持 `-png`，大图加 `-scale-to 1700`）、`pdfinfo`、`pdftotext`。
- TeX Live 2024：`D:\latex\texlive\2024\bin\windows`（用 `latexmk -xelatex`）。
- 重编脚本：`xhu818\scripts\rebuild-doc01.ps1`（doc01）、`xhu818\scripts\rebuild-docs.ps1`（doc02/03/04）。
  调用方式（中文脚本不能用 `Get-Content -Raw`，会乱码）：
  `$p='...\rebuild-doc01.ps1'; Invoke-Expression ([IO.File]::ReadAllText($p,[Text.Encoding]::UTF8))`
- `xhu818\scripts\check_examples.py`：把教材 26 道编号例题定位到 OCR 页码/行号（核对用）。
- Git：`https://github.com/comegohellokitty/xhu818-fluid-mechanics`（分支 `main`，公开）。
  **本机直连 github.com:443 被墙**，已配 `http.https://github.com.proxy=http://127.0.0.1:7897`——推送前确认 Clash（`clash-verge`/`verge-mihomo`）在跑。

## 6. 中文路径陷阱（Windows/PowerShell，一贯踩）

- `Get-ChildItem <目录> -Filter "*中文*"` **匹配不到**；用
  `Get-ChildItem -LiteralPath <目录> | Where-Object { $_.Name -match "关键词" }`。
- poppler 直接收中文路径会报 `I/O Error: Couldn't open file '<e5><ad><94>…'`；先
  `Copy-Item -LiteralPath $f.FullName -Destination <纯 ASCII 临时路径>` 再处理。
- `Get-Content` 读 UTF-8 显示乱码只是**显示**问题；用 read 工具读正常。
- `git commit -m` 带多行中文会被 PowerShell 搞坏（全角引号被吞、git 把片段当 pathspec）；把消息写进文件后 `git commit -F <文件>`。
