# 便宜地读 PDF / 扫描件（省 token 铁律）

> 一句话：**OCR 是本地跑的，不花 token；花 token 的是「把文字读进上下文」。**
> 所以省钱不是"换个 OCR 引擎"，而是"**只读命中的那几行**"。

---

## 1. 先判有没有文字层（决定走哪条路）

```powershell
python xhu818\scripts\pdfread.py which <pdf> [<pdf> ...]
```

实测（本项目自己的资料，2026-10 复测）：

| 文件 | `pdftotext` 前 3 页字符数 | 结论 |
| --- | --- | --- |
| `xhu818\pdf\XHU818-01..05-*.pdf`（五份成品） | 900–3200 | **有文字层** → 直接抽，0 成本 |
| `03-exams\figures\q2015.pdf` | 1544 | 部分有文字层 |
| `q2014.pdf`、`q2016..q2022.pdf` | **0** | 纯图片，必须 OCR |
| 赵琴教材、孔珑辅导书扫描件 | **0** | 纯图片，必须 OCR |

**我做的五份成品 PDF 全都有文字层**——以后要引用里面的题，用 `text` 模式抽，不要截图、不要 OCR。

```powershell
python xhu818\scripts\pdfread.py text <pdf> --pages 1-3 --maxchars 4000
```

---

## 2. 扫描件：OCR 结果**已经在硬盘上**，只 grep，不重跑

| 库 | 目录 | 文件数 | 大小 | 书页换算 |
| --- | --- | --- | --- | --- |
| 赵琴教材 | `xhu818\02-ocr\zhqin` | 335 个 txt | 1.14 MB | 书页 = 页 − 9 |
| 孔珑辅导书 | `xhu818\02-ocr\konglong` | 165 个 txt | 0.39 MB | 书页 = 页 − 9 |
| 历年真题 | `xhu818\02-ocr\exams` | 87 个 txt | 0.18 MB | 按年份子目录，无书页码 |
| 题库 | `xhu818\02-ocr\bank10` | 7 个 txt | 0.02 MB | 书页 = 页 − 9 |

合计 **≈1.73 MB 中文**；整包读进上下文约 **60 万 token 量级**——但按关键词命中读，通常只花几十到几百 token。

- 每个库都有 `merged.txt`，里面按 `===== page N =====` 分页；**grep 它就能同时拿到出处页码**。
- `exams` 没有总 `merged.txt`，是按年份子目录存的：`17`、`2014年答案`、`2014年试题`、`2015年答案`、`2016年答案`…`2022-818工程流体力学`（`17` 与 `2022-*` 是独有目录名，按名字判断年份）。

```powershell
# 搜关键词，只打印命中行 + 出处（--ctx 1 够用，别贪多）
python xhu818\scripts\pdfread.py grep 水击 --lib zhqin --max 5
python xhu818\scripts\pdfread.py grep 0.236 --lib exams,zhqin,konglong --max 8
# 精读某一页（写书页码，脚本自动 +9 换算成扫描件页码）
python xhu818\scripts\pdfread.py page zhqin 121
# 看库里都有什么
python xhu818\scripts\pdfread.py where
```

命中行长这样：`--- zhqin [zhqin/merged.txt p100]（书 p91）`，可直接回查原书页。

---

## 3. 铁律

1. **不许重跑 OCR。** 只有**新拿到**的扫描件才需要 OCR：
   `python xhu818\scripts\ocr_pdf.py --pdf <新文件> --out xhu818\02-ocr\<新库名> --px 1700 --merge`
2. **不许整页、整本读** OCR 文本。先 `grep` 定位，再 `--ctx 1` 读命中行；确实要精读就 `page` 取单页。
3. **OCR 里的公式一律不许照抄**（分式、下标、根号、希腊字母基本全坏）。要么按物理反推并写明依据，要么注「教材此处 OCR 不可判读」。
4. **图片才用视觉工具**：学生拍的照片用 `read_image`（多模态读题最准）；大面积扫描件先用第 2 条的路子，别一张张看图。
5. 分析 PDF 时，**有文字层就一定先 `pdftotext`**——这是本项目 token 账上唯一"不要钱"的抽取方式。

---

## 4. 插件备查（当前未安装）

查过本机插件市场缓存（`C:\Users\mate book D14\.dsh\profiles\desktop\.dsh-market\discovery-compatibility-v1.json`，753 个插件）：

| 插件 | 版本 | 与 DSH 0.2.0-rc.2 的兼容性 |
| --- | --- | --- |
| `dsh-pdf-mineru` | 0.2.0 | ✅ 兼容（要求 DSH ≥0.2.0-rc.2）。MinerU 驱动的 PDF→Markdown 文档解析 |
| `dsh-windows-ocr` | 0.7.0 | ❌ 要求 DSH `^0.1.5-rc.2` |
| `dsh-ocr-local` | 0.5.0 | ❌ 要求 dsh-tools `<0.2.0` |
| `dsh-tool-vision` | 0.10.1 | ✅ 兼容 |
| `@liustack/modlens` 3.26.6 | 已安装 | 即 `modlens_read_image`（视觉读取，返回结构化文本证据） |

**结论**：只有 `dsh-pdf-mineru` 值得在"又来新扫描件"时装；当前靠 `pdfread.py` + 已落盘的 OCR 缓存就够，**不必安装任何插件**。
