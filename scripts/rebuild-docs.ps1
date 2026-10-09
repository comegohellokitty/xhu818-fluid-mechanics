# 重编并发布 02/03/04 —— 这三份的源码被「教材例 4.12 → 教材习题 4.12」全局订正改过，
# 所以当时已发布的 PDF 相对源码是旧的，必须重编，否则仓库里源码与成品不一致。
# 01 由 rebuild-doc01.ps1 单独负责（硬闸门相同）；05 源码本轮未变动，无需重编。
#
# 【重要陷阱】03-exams 有「干净版」与「含原卷影印版」两种产物：
#   parts/apA-scan.tex 用 \IfFileExists{figures/<year>.pdf} 判断，figures\ 目录在就在、不在就退化成提示框。
#   figures\*.pdf 是扫描件，已被 .gitignore 排除、不随仓库分发 —— 所以「仓库干净版」必须在
#   figures\ 被挪走的情况下编译。本脚本对 03 自动临时改名 figures\ → figures__local_off，编译完再改回。
#   若在本机直接编译 03，会得到 208 页 / 约 29MB 的含影印版（应放进 pdf-local\，绝不能进 pdf\ 或仓库）。
#
# 用法（执行策略禁直接跑 .ps1）：
#   $env:XHU818_ONLY = ''            # 留空=全部；可填 '03-exams' 只编一份
#   $p = '.\scripts\rebuild-docs.ps1'
#   Invoke-Expression ([IO.File]::ReadAllText($p,[Text.Encoding]::UTF8))   # 勿用 Get-Content -Raw：中文会乱码
param([string]$Only = $env:XHU818_ONLY)

$ErrorActionPreference = 'Continue'
$env:PATH = "D:\latex\texlive\2024\bin\windows;" + $env:PATH

$root = 'C:\Users\mate book D14\Documents\deepseek-harness\default-workspace\xhu818'
$pdfd = Join-Path $root 'pdf'
New-Item -ItemType Directory -Force -Path $pdfd | Out-Null

$targets = @(
  @{ dir = '02-exercises'; out = 'XHU818-02-课后习题.pdf';       hideScan = $false },
  @{ dir = '03-exams';     out = 'XHU818-03-历年真题与答案.pdf'; hideScan = $true  },
  @{ dir = '04-bank';      out = 'XHU818-04-题库汇编.pdf';       hideScan = $false }
)

foreach ($t in $targets) {
  if ($Only -ne '' -and $Only -ne $null -and $t.dir -ne $Only) { continue }
  $doc = Join-Path $root ('latex\' + $t.dir)
  Write-Host ('===== ' + $t.dir + ' =====')
  Set-Location $doc
  Copy-Item (Join-Path $root 'latex\common\xhu818.sty') .\xhu818.sty -Force

  # 03 专用：临时把扫描影印件目录挪开，才能编出「仓库干净版」
  $fig = Join-Path $doc 'figures'
  $figOff = Join-Path $doc 'figures__local_off'
  $moved = $false
  if ($t.hideScan -and (Test-Path -LiteralPath $fig)) {
    if (Test-Path -LiteralPath $figOff) { Remove-Item -LiteralPath $figOff -Recurse -Force }
    Rename-Item -LiteralPath $fig -NewName 'figures__local_off'
    $moved = $true
    Write-Host '[rebuild] figures\ 已临时改名为 figures__local_off（编「干净版」）'
  }

  try {
    # 与 rebuild-doc01.ps1 同样的两条教训：
    #  ① 加 -f：hyperref/rerunfilecheck 会让首遍 xelatex 以退出码 1 收尾，latexmk 会误判中止；
    #  ② 绝不加 -file-line-error：它把行首 ! 改写成 './file:NNN:'，使 ^\s*! 恒为 0 而误判通过。
    #  ③ 03 必须再加 -g：figures\ 改名不会被 latexmk 记成依赖变化（\IfFileExists 不进 .fdb_latexmk），
    #     实测它会判定「无事可做」而把上一次 208 页的含影印版 main.pdf 原样留下，制造静默错发布。
    $lmArgs = @('-xelatex', '-f', '-interaction=nonstopmode')
    if ($t.hideScan) { $lmArgs += '-g' }
    $lmArgs += 'main.tex'
    & latexmk @lmArgs *> .\rebuild-run.log

    $log = Join-Path $doc 'main.log'
    $pdf = Join-Path $doc 'main.pdf'
    if (-not (Test-Path $log) -or -not (Test-Path $pdf)) { Write-Host '[rebuild] 缺 main.log/main.pdf，跳过'; continue }

    $L = Get-Content -LiteralPath $log
    $bang     = ($L | Select-String -Pattern '^\s*!').Count
    $undef    = ($L | Select-String -Pattern 'Undefined control sequence').Count
    $missing  = ($L | Select-String -Pattern 'Missing character').Count
    $emerg    = ($L | Select-String -Pattern 'Emergency stop').Count
    $overfull = ($L | Select-String -Pattern 'Overfull \\hbox').Count
    $pages    = (& pdfinfo $pdf 2>&1 | Select-String -Pattern '^Pages').ToString().Trim()
    $size     = (Get-Item -LiteralPath $pdf).Length
    Write-Host ("[rebuild] BANG=$bang  UNDEF=$undef  MISSING=$missing  EMERGENCY=$emerg  OVERFULL_HBOX=$overfull")
    Write-Host ("[rebuild] $pages   size=$size B")
    $L | Select-String -Pattern '^\s*!' | Select-Object -First 8 | ForEach-Object { '   ' + $_.Line }

    $newest = Get-ChildItem -LiteralPath (Join-Path $doc 'parts') -Filter '*.tex' |
              Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $pdfTime = (Get-Item -LiteralPath $pdf).LastWriteTime
    Write-Host ("[rebuild] main.pdf={0:HH:mm:ss}  最新 part={1}({2:HH:mm:ss})" -f $pdfTime, $newest.Name, $newest.LastWriteTime)

    if ($pdfTime -lt $newest.LastWriteTime) {
      Write-Host '[publish] main.pdf 比最新 part 还旧 —— 构建没真正完成，拒绝发布。'
    } elseif ($bang -eq 0 -and $undef -eq 0 -and $missing -eq 0) {
      $dest = Join-Path $pdfd $t.out
      Copy-Item -LiteralPath $pdf -Destination $dest -Force
      Write-Host ('[publish] -> ' + $dest + '  (' + (Get-Item -LiteralPath $dest).Length + ' B)')
      Write-Host ('[publish] SHA256=' + (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash)
    } else {
      Write-Host '[publish] 有错误或欠缺字符，未发布。'
    }
  } finally {
    if ($moved -and (Test-Path -LiteralPath $figOff)) {
      Rename-Item -LiteralPath $figOff -NewName 'figures'
      Write-Host '[rebuild] figures__local_off 已改回 figures'
    }
  }
  Write-Host ''
}
Write-Host '全部完成。'
