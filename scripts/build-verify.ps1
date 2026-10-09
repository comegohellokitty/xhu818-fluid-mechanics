# build-verify.ps1 — rebuild every document and report RELIABLE error counts.
#
# Why this script exists:
#   xelatex with -file-line-error rewrites an error line's leading "!" into a
#   "./parts/xxx.tex:NNN:" prefix, so a naive `Select-String '^!'` sees ZERO
#   errors even when the document is full of `Undefined control sequence`.
#   This script therefore (a) does NOT pass -file-line-error and (b) counts the
#   raw "!" lines plus the other fatal markers.
#
# Usage:
#   Invoke-Expression (Get-Content -Raw .\build-verify.ps1)
#   (the local execution policy forbids running .ps1 files directly)

$ErrorActionPreference = "Continue"

$root = "C:\Users\mate book D14\Documents\deepseek-harness\default-workspace\xhu818"
$latex = Join-Path $root "latex"
$pdfOut = Join-Path $root "pdf"
$env:PATH = "D:\latex\texlive\2024\bin\windows;" + $env:PATH
New-Item -ItemType Directory -Force -Path $pdfOut | Out-Null

$docs = [ordered]@{
  "01-textbook" = "XHU818-01-教材精讲"
  "02-exercises" = "XHU818-02-课后习题"
  "03-exams"    = "XHU818-03-历年真题与答案"
  "04-bank"     = "XHU818-04-题库汇编"
  "05-konglong" = "XHU818-05-孔珑题选"
}

$summary = @()

foreach ($doc in $docs.Keys) {
  $dir = Join-Path $latex $doc
  if (-not (Test-Path $dir)) { $summary += [pscustomobject]@{ Doc = $doc; Status = "MISSING DIR" }; continue }
  Set-Location $dir
  Copy-Item (Join-Path $latex "common\xhu818.sty") ".\xhu818.sty" -Force

  # -g forces a full rebuild: latexmk does not notice InputIfFileExists targets.
  latexmk -xelatex -g -interaction=nonstopmode main.tex *> (Join-Path $env:TEMP "$doc-mk.log") | Out-Null
  $mkExit = $LASTEXITCODE

  $log = Get-Content ".\main.log"
  $bang      = ($log | Select-String -Pattern '^\s*!' -CaseSensitive).Count
  $undef     = ($log | Select-String -Pattern 'Undefined control sequence').Count
  $missing   = ($log | Select-String -Pattern 'Missing character').Count
  $emergency = ($log | Select-String -Pattern 'Emergency stop').Count
  $overfull  = ($log | Select-String -Pattern 'Overfull \\hbox').Count

  $pages = ""
  if (Test-Path ".\main.pdf") {
    $pages = (pdfinfo ".\main.pdf" | Select-String "^Pages:\s+(\d+)").Matches.Groups[1].Value
    Copy-Item ".\main.pdf" (Join-Path $pdfOut ($docs[$doc] + ".pdf")) -Force
  }

  $status = if ($bang + $undef + $emergency -gt 0) { "FAIL" } else { "OK" }
  $summary += [pscustomobject]@{
    Doc = $doc; Status = $status; mk = $mkExit; Bang = $bang; Undef = $undef
    Missing = $missing; Emergency = $emergency; Overfull = $overfull; Pages = $pages
  }
}

Set-Location $root
$summary | Format-Table -AutoSize
"--- published ---"
Get-ChildItem $pdfOut -Filter "*.pdf" | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
