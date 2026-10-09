# 编译全部五份 PDF：  powershell -ExecutionPolicy Bypass -File .\build-all.ps1
# 可选参数：-Only 03-exams  只编译某一份
param([string]$Only = "")

$ErrorActionPreference = "Stop"
$env:PATH = "D:\latex\texlive\2024\bin\windows;$env:PATH"
$root = $PSScriptRoot

$docs = @(
    @{ dir = "01-textbook";  out = "XHU818-01-教材精讲.pdf" },
    @{ dir = "02-exercises"; out = "XHU818-02-课后习题.pdf" },
    @{ dir = "03-exams";     out = "XHU818-03-历年真题与答案.pdf" },
    @{ dir = "04-bank";      out = "XHU818-04-题库汇编.pdf" },
    @{ dir = "05-konglong";  out = "XHU818-05-孔珑题选.pdf" }
)

foreach ($d in $docs) {
    if ($Only -ne "" -and $d.dir -ne $Only) { continue }
    $p = Join-Path $root $d.dir
    if (-not (Test-Path (Join-Path $p "main.tex"))) { Write-Host "[skip] $($d.dir) 无 main.tex"; continue }
    Write-Host "===== 编译 $($d.dir) =====" -ForegroundColor Cyan
    Copy-Item (Join-Path $root "common\xhu818.sty") $p -Force
    Push-Location $p
    try {
        latexmk -xelatex -interaction=nonstopmode -file-line-error main.tex | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[FAIL] $($d.dir) —— 见 main.log" -ForegroundColor Red
            Get-Content "main.log" -Tail 40 | Select-String -Pattern "^!|Error|Undefined" | Select-Object -First 15
        } else {
            Copy-Item "main.pdf" (Join-Path $root "..\pdf\$($d.out)") -Force -ErrorAction SilentlyContinue
            Write-Host "[OK] $($d.dir) -> $($d.out)" -ForegroundColor Green
        }
    } finally { Pop-Location }
}
Write-Host "全部完成。"
