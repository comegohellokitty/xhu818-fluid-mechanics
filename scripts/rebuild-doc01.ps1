# 重编《XHU818-01 教材精讲》整册并发布到 xhu818\pdf\
# 用法（执行策略禁直接跑 .ps1）：
#   $p = '.\scripts\rebuild-doc01.ps1'
#   Invoke-Expression ([IO.File]::ReadAllText($p,[Text.Encoding]::UTF8))   # 勿用 Get-Content -Raw：中文会乱码
# 或在同目录用：
#   Invoke-Expression (Get-Content -Raw .\scripts\rebuild-doc01.ps1)
param([switch]$ForceFull)

$ErrorActionPreference = 'Continue'
$env:PATH = "D:\latex\texlive\2024\bin\windows;" + $env:PATH

$root = 'C:\Users\mate book D14\Documents\deepseek-harness\default-workspace\xhu818'
$doc  = Join-Path $root 'latex\01-textbook'
$pdfd = Join-Path $root 'pdf'
New-Item -ItemType Directory -Force -Path $pdfd | Out-Null

Set-Location $doc
Copy-Item (Join-Path $root 'latex\common\xhu818.sty') .\xhu818.sty -Force

if ($ForceFull) {
  Write-Host '[rebuild] 强制全量：清掉 aux/toc/out'
  Get-ChildItem -LiteralPath $doc -Filter 'main.*' |
    Where-Object { $_.Extension -in '.aux', '.toc', '.out', '.lof', '.lot', '.fls', '.fdb_latexmk', '.xdv' } |
    Remove-Item -Force -ErrorAction SilentlyContinue
}

Write-Host '[rebuild] latexmk -xelatex ...（就地构建，产物 main.pdf 所在目录已被 .gitignore 排除）'
# 注意：本册用 rerunfilecheck/hyperref，首遍 xelatex 会以「Rerun to get /PageLabels entry」
# 的退出码 1 收尾，latexmk 会误判为出错而中止（实测 EXIT=12、main.pdf 仍是旧文件）。
# 必须加 -f 让 latexmk 走完后续遍次；真实错误改由下面读 main.log 统计。
$sw = [Diagnostics.Stopwatch]::StartNew()
# 绝不加 -file-line-error：它把「行首 !」改写成「./file:NNN:」前缀，
# 使下面 ^! 的统计恒为 0，任何真实错误都会被误判为通过（本脚本早期版本即栽在此）。
& latexmk -xelatex -f -interaction=nonstopmode main.tex *> .\rebuild-run.log
$code = $LASTEXITCODE
$sw.Stop()
Write-Host ("[rebuild] latexmk EXIT=$code  用时 {0:N0} s" -f $sw.Elapsed.TotalSeconds)

$log = Join-Path $doc 'main.log'
$pdf = Join-Path $doc 'main.pdf'
if (-not (Test-Path $log)) { Write-Host '[rebuild] 找不到 main.log，中止'; return }
if (-not (Test-Path $pdf)) { Write-Host '[rebuild] 找不到 main.pdf，中止'; return }

$L = Get-Content -LiteralPath $log
$bang    = ($L | Select-String -Pattern '^\s*!').Count
$undef   = ($L | Select-String -Pattern 'Undefined control sequence').Count
$missing = ($L | Select-String -Pattern 'Missing character').Count
$emerg   = ($L | Select-String -Pattern 'Emergency stop').Count
$overfull= ($L | Select-String -Pattern 'Overfull \\hbox').Count

$pages = (& pdfinfo $pdf 2>&1 | Select-String -Pattern '^Pages' ).ToString().Trim()
$size  = (Get-Item $pdf).Length
Write-Host "[rebuild] BANG=$bang  UNDEF=$undef  MISSING=$missing  EMERGENCY=$emerg  OVERFULL_HBOX=$overfull"
Write-Host "[rebuild] $pages   size=$size B"
$L | Select-String -Pattern '^!' | Select-Object -First 10

$newest = Get-ChildItem -LiteralPath (Join-Path $doc 'parts') -Filter '*.tex' |
          Sort-Object LastWriteTime -Descending | Select-Object -First 1
$pdfTime = (Get-Item -LiteralPath $pdf).LastWriteTime
Write-Host ("[rebuild] main.pdf={0:HH:mm:ss}  最新 part={1}({2:HH:mm:ss})" -f $pdfTime, $newest.Name, $newest.LastWriteTime)

if ($pdfTime -lt $newest.LastWriteTime) {
  Write-Host '[publish] main.pdf 比最新 part 还旧 —— 构建没真正完成，拒绝发布。'
} elseif ($bang -eq 0 -and $undef -eq 0 -and $missing -eq 0) {
  $dest = Join-Path $pdfd 'XHU818-01-教材精讲.pdf'
  Copy-Item -LiteralPath $pdf -Destination $dest -Force
  Write-Host ("[publish] -> " + $dest + "  (" + (Get-Item $dest).Length + " B)")
  (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash | ForEach-Object { Write-Host ("[publish] SHA256=" + $_) }
} else {
  Write-Host '[publish] 有错误或欠缺字符，未发布。'
}
