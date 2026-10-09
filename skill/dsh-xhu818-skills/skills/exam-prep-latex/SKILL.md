---
name: exam-prep-latex
description: 从"考纲 + 扫描教材 + 历年真题 + 题库"这些原始资料，产出一整套中文考研/期末复习 LaTeX 文档（教材精讲、课后习题、历年真题与答案、题库汇编、配套辅导书题选），并把"重要程度"星级建立在**可追溯的文件依据**上而不是主观印象。适用于：某门课只有扫描版教材、真题多为拍照件、需要按考纲裁剪内容、需要给每道题标注考频。也适用于任何"把一堆杂乱 PDF/扫描件整理成结构化可打印讲义"的任务。
compatibility: 需要 Windows + TeX Live（XeLaTeX/latexmk）+ Python 3 + RapidOCR(onnxruntime)；中文文档必须用 XeLaTeX。
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# 考研资料 → LaTeX 讲义全集

## 这个技能解决什么

用户手里通常是这样一堆东西：**扫描版教材**（几百页、无文字层）、**手机拍的历年真题与答案**、**几份机构出的考情分析 pptx/docx**、**题库 PDF**，外加一句"帮我整理成能应付考试的资料"。

产出是一套**五份 PDF**（可按需裁剪）：

| 编号 | 文档 | 内容要点 |
|---|---|---|
| 01 | 教材精讲 | 按指定章节缩减教材；重要公式**不证明**但要写"含义 + 适用条件"；每个概念给"是什么／常考什么／考什么题型／多重要／难度／书上没有的方法" |
| 02 | 课后习题 | 教材课后题全文 + 星级；**题目在前、解答统一置后** |
| 03 | 历年真题与答案 | 试题在前、**全部答案统一放到最后一章**；逐年标注当年科目代码 |
| 04 | 题库汇编 | 各题库按来源分章，逐题标星级 |
| 05 | 配套辅导书题选 | 只挑符合考纲的题目；题在前、答案置后 |

## 铁律：星级必须"有文件依据"

用户对这类资料最大的要求（也是唯一会真正被质疑的点）是**"重要程度不能是你主观说的"**。所以：

1. **先列证据清单**，给每份分析类文件编号 `E1…En`，例如
   `E1=考情分析.pptx`（含"题型分值表""逐章重要度表""命题风格"）、
   `E2=考点分析.pptx`、`E3=考研分析.docx`、`E4=历年真题`、`E5=题库`、`E6=指定教材`。
2. **写一张判定表**（落到 `src/star_rubric.md`，并抄进每份 PDF 的前言）：

   | 星级 | 判定条件（满足其一） |
   |---|---|
   | ★★★★★ | 该考点在历年真题中作为**计算题/大题**出现 ≥3 次；或 E1/E2 明写"考试计算题重点" |
   | ★★★★ | 出现 2–3 次；或明写"重点掌握" |
   | ★★★ | 出现 1 次；或写"掌握基本概念与公式套用" |
   | ★★ | 真题未出现，但属考纲核心且题库反复出现 |
   | ★ | 边缘／仅复试范围 |

3. **每题/每考点后面强制附**〔依据：E4 2022 单选 3；E1 slide33"计算题基础入门"〕。
   **禁止编造年份题号**——子代理只能引用它**确实读到过**的证据，否则降星并把依据写成"E6 教材 §x.x"。
4. 星级要**跨文档一致**：同一个考点在 01 和 02/05 里星数必须相同。做法是建一个**考点码表**（如 `K101…K805` 对应"章-考点序"），先在一处定稿，其余文档只引用码。

## 自动化判星（可选的第二遍统一）

第一遍让撰稿人写占位符 `\xstarmark{K403}`，第二遍用一张 Python 字典统一替换成 `\xstarfull{5}\yiju{…}`：

- `scripts/star_table.py`：内含 `STAR: dict[str, tuple[int, str]]`（考点码 → 星级 + 一句话依据）与 `OUT_OF_SCOPE`（超纲码 → 写 `\nandu{超纲}`）。
- 支持 `--check`（只统计，不写）与就地替换；替换后必须**重新编译**并渲染抽查一页。
- **坑**：文件顶部 docstring 必须写 `r"""…"""`，否则 docstring 里的 `\xstarmark` 会被 Python 当成 `\xXX` 转义并抛
  `SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position …: truncated \xXX escape`。

## 阶段 0：环境侦察（不要跳过）

1. **先判每份文件的"有无文字层"**：`pdftotext` 一下，输出只有几字节的就是纯扫描件。
   - 有文字层 → 直接 `pdftotext` 得到全文，别去 OCR。
   - 扫描件 → 必须 OCR（见阶段 1）。
2. **确定版式事实**：`pdfinfo` 看页数；对超大页面（手机拍照常见 4608×3456 pts）渲染时用
   `pdftoppm -png -scale-to 1700`；注意有些 poppler 构建**不支持 `-jpeg`**，只能用 `-png`。
3. **确认教材的章页对应**：先把封面/版权页/目录 OCR 或直接看图，得到"书页→PDF 页"的偏移量
   （例如"书页 + 9 = PDF 页"）。**这一步做错，后面全线错位**。
4. **中文文件名陷阱（Windows/PowerShell）**：
   - `Get-ChildItem <目录> -Filter "*中文*.pdf"` **匹配不到**，要用
     `Get-ChildItem -LiteralPath <目录> | Where-Object { $_.Name -match "关键词" }`。
   - poppler 直接接收中文路径会报 `I/O Error: Couldn't open file '<e5><ad><94>…'`（终端把 UTF-8 字节转义了）。
     **对策**：先 `Copy-Item -LiteralPath $f.FullName -Destination <纯 ASCII 临时路径>`，再对 ASCII 路径调用 poppler。
   - PowerShell 的 `Get-Content` 读 UTF-8 文本会显示乱码，这是**显示**问题不是编码问题；用 read 工具读正常。

## 阶段 1：OCR 流水线

用 **RapidOCR(onnxruntime)**，无需联网、中文识别质量足够。

- `scripts/ocr_pdf.py`：单文件 OCR，含 **`install_safe_cv2_resize()`** 猴子补丁——
  把 `cv2.resize` 包成"失败→`cv2.setNumThreads(1)` 重试→仍失败则用 PIL `Image.BILINEAR` 等价替代"。
  这是为了绕开高负载下 OpenCV 抛
  `cv2.error: Unknown C++ exception from OpenCV code`（见 `rapidocr_onnxruntime/ch_ppocr_det/utils.py`）的**间歇性**崩溃。
- `scripts/ocr_batch.py`：从 JSON 清单读条目，**只加载一次模型**，逐条目写 `page-%04d.txt` 与 `merged.txt`，
  单页 3 次重试，**单页失败只记进 `_failures.txt`，绝不中断整批**。
- `scripts/make_manifest.py`：生成清单，条目形如
  `{"pdf","out","px","first","last","tag","skip"}`。

**并发策略（实测很重要）**：onnxruntime 每个进程默认开满线程，3 个进程并发会让每个进程掉到 35–45 s/页，
而**单进程独占只要 ~5–10 s/页**。所以：
- 总量大时用**单进程顺序批处理**（562 页 ≈ 45 min，远快于并发 3 小时）；
- 只有当"某一份后续文档的关键区间很短、想让它先开工"时，才起**第二个**进程
  （设 `$env:OMP_NUM_THREADS="8"` 限制线程），并按优先级把该文档需要的页**排到清单最前面**。
- 清单顺序 ＝ 产出顺序，**把最下游阻塞的页排最前**。

## 阶段 2：LaTeX 样式包

不要直接用现成模板（ElegantBook 等）——五份文档要统一样式、还要自定义星级/依据/考点盒子，
自建一个 `common/<project>.sty` 最可控，也不依赖外部 `.cls`，便于分享。

骨架：`ctexbook` + `geometry` + `amsmath/amssymb/bm` + `booktabs/tabularx/multirow` +
`enumitem/caption/xcolor/tcolorbox(skins,breakable)/titlesec/fancyhdr/hyperref`。

本项目可复用的自定义件（见 `assets/xhu818.sty`）：

- `\xstarfull{n}`：按 `\ifcase` 输出 n 颗金星（**正文绝不能直接写字面 `★`**，lmroman 缺字）。
- `\yiju{…}` → 〔依据：…〕；`\nandu{易|中|难}`。
- 环境：`kaodian{星数}{标题}`、`gongshi{标题}`、`tishi`、`yicuo`、`jielun`、`banfa`、
  `zhenti{出处}{题型}`、`jie`（解答）、`ti`（题目 list）、`xiaowen`、`choices`。
- `\xhucover{主标题}{副标题}{说明}` 封面；`\anstitle{…}` 答案章标题。

**踩过的坑（务必照抄处理）**：

1. **tcolorbox 环境绝对不能放进 `\item` 内部**，也不能跨 `\end{ti}`／`\end{enumerate}`，否则整册报
   `! LaTeX Error: \begin{tcb@savebox} on input line N ended by \end{enumerate}.`
   正确做法：说明框全部提到 `\end{ti}` 之后，按"第 N 题"分条。
   同理**命令式** `\tishi{…}` 会开盒不收尾，必须用 `\begin{tishi}…\end{tishi}`。
2. **字体缺字**：模型/文本里出现 `①②③`、箭头、`★`、`≤ ≥ ≠ √`、全角标点时，要给中文字体加字符类：
   `\RequirePackage{xeCJK}` + `\xeCJKDeclareCharClass{CJK}{"2460-"24FF,"2190-"21FF,"25A0-"25FF,"2600-"26FF,"3000-"303F,"FF00-"FFEF}`。
   否则报 `Missing character: There is no ① (U+2460) in font lmroman10-regular`。
   更稳的约定：**正文不许出现 `★ ≠ ≤ ≥ √ §` 字面**，一律 `\xstarfull{n}` / `$\neq$` / `$\le$` / `$\ge$` / `$\sqrt{}$` / `\S`。
3. **数学模式 `\text{}` 内不能放中文标点（尤其顿号「、」）**，xeCJK 对 `\text` 不生效，会报
   `Missing character: There is no 、(U+3001)`。中文要移到 `\text{}` 外面。
4. 不要 `\newcommand{\Re}`（LaTeX 内建是实部符号），用 `\Rey`；所有自定义宏用 `\providecommand` 防冲突。
5. **每个文档章一律用 `\chapter*{…}` + `\addcontentsline{toc}{chapter}{…}` + `\markboth{…}{}`**，
   不要用 `\chapter{}`——否则计数器自增，后面章节页眉会出现"第 2 章 第 1 章…"的错乱。

## 阶段 3：编译

```powershell
$env:PATH="<texlive>\2024\bin\windows;"+$env:PATH
Copy-Item ..\common\<project>.sty .\<project>.sty -Force
latexmk -xelatex -interaction=nonstopmode -file-line-error "-output-directory=$env:TEMP\chk" main.tex
```

- **`-output-directory` 的值必须放双引号里**，否则 PowerShell 会把它展开成 8.3 短名
  （`C:\Users\MATEBO~1\AppData\Local\Temp`）并报 `I can't write on file 'main.log'` + Emergency stop。
- **不要用 `Set-Content` 复制 `.sty`**（会把 `#` 等转义搞坏，报 `You can't use 'macro parameter character #'`），
  必须用 `Copy-Item`。
- `\InputIfFileExists{...}` 让"文件还没写好"时不至于编译失败，但 latexmk **不会**自动发现新出现的文件，
  要么删 aux，要么 `-g` 强制重编。
- 自检：`main.log` 里 `^!` 计数必须为 0、`Missing character` 必须为 0；再 `pdftoppm` 渲一页用视觉抽查版式。
- 批量构建脚本见 `assets/build-all.ps1`（逐文档编译→成功则把 `main.pdf` 拷成 `pdf/<项目>-0N-<名称>.pdf`）。

## 阶段 4：写作规范与"文档骨架"

建 `main.tex` 时用 `\InputIfFileExists` 把每章拆成 `parts/chNN.tex`，这样**多个撰稿人可以并行**且互不阻塞。

**所有撰稿人共读一份 `<PROJECT>-SPEC.md`**，内容是：
- 只能用哪些宏/环境（附最小示例）；
- 星级三件套与证据清单（`E1…En`）；
- **已知真题清单原文摘录**（让撰稿人不必自己 OCR）；
- 版式约定（禁用字面符号、图一律用 `\tuyi{}` 描述、禁 TikZ）；
- 交付前必须独立编译验证的命令；
- 汇报格式（文件路径 + 行数 + 考点清单/星级/依据 + 读到的 OCR 页 + 编译结果）。

**"一章一个子代理"的并行模式**很有效：每个子代理读同一份 SPEC + 一个"范例章"文件，
产出自己的 `parts/chNN.tex`。范例章（第 1 章）要由主代理亲手写，把结构定死。

另外单独写一份 `<PROJECT>-EXAM-SPEC.md` 给"真题转录 + 答案撰写"这条线，并把
**科目代码逐年变动的事实**写进去（考研科目代码常改，例：2014=818、2015=819、2016=817、2017=819、
2018=819、2019=821、2020=818、2021=818、2022=818）——**不要因为现在考 818 就把早年试卷的代码改掉**。
章标题写成"20XX 年…试题（当年科目代码 8XX）"。

## 阶段 5：交付与分享

- 输出到 `pdf/` 并**用视觉抽查**关键页（封面、考情表、一个考点页、一个答案页）。
- 写 `README.md`：五份成品说明、考试情报表、**星级评审依据（证据清单 + 判定规则表）**、目录结构、
  编译方法、排版约定、**免责声明**（不含教材原文扫描件与原卷 PDF；转录仅供个人复习；答案非官方；不得商用）。
- `.gitignore` 必须排除：原始资料目录、OCR 中间产物、`_chk/`、`_build*/`、LaTeX 中间文件、
  以及**扫描件 `figures/`**（版权）。若正文用 `\includepdf` 收原卷影印页，要包一层
  `\IfFileExists{figures/xxx.pdf}{…}{\begin{tishi}本编译环境缺少原卷影印件…\end{tishi}}`，
  这样 clone 下来也能编过。

## 常见失败模式速查

| 症状 | 根因 | 处置 |
|---|---|---|
| `! LaTeX Error: \begin{tcb@savebox} … ended by \end{enumerate}` | tcolorbox 放进了 `\item` | 把说明框移到 `\end{ti}` 之后 |
| `Missing character: There is no ① (U+2460)` | 字符没交给中文字体 | `\xeCJKDeclareCharClass`；或别写字面符号 |
| `I can't write on file 'main.log'` | `-output-directory` 未加双引号 | 加双引号，用绝对路径 |
| `You can't use 'macro parameter character #'` | 用 `Set-Content` 复制了 `.sty` | 改用 `Copy-Item` |
| `File ended while scanning use of \yiju` | `\yiju{…` 少了右花括号 | 加 `}`；可用脚本按"整文件 `{`/`}` 总数是否相等"快速定位 |
| `cv2.error: Unknown C++ exception from OpenCV code` | 高负载下 OpenCV 间歇失败 | `install_safe_cv2_resize()` + 每页重试 |
| OCR 一律 3–5 字节输出 | 该 PDF 是纯扫描件 | 走 OCR，别指望 `pdftotext` |
| 中文文件名找不到 / poppler 打不开 | Windows 编码 | `Where-Object -match` 取 `FullName` → 复制成 ASCII 名再处理 |

## 附带资源

- `assets/xhu818.sty` —— 完整样式包（可直接改项目名复用）。
- `assets/build-all.ps1` —— 多文档批量编译 + 输出重命名。
- `scripts/ocr_pdf.py`、`scripts/ocr_batch.py`、`scripts/make_manifest.py` —— OCR 流水线（含 cv2 容错补丁）。
- `scripts/star_table.py` —— 证据驱动的星级统一替换引擎（含 `--check`）。
- `references/star-rubric.md` —— 证据清单与星级判定表模板。
- `references/WRITING-SPEC.md`、`references/EXAM-SPEC.md` —— 撰稿规范模板（含上述全部踩坑与真题证据表格式）。
