# 全局登记 magpie-docs (PowerShell 版): 只放指针, 不复制文档。
# 用法: powershell -ExecutionPolicy Bypass -File install.ps1
$ErrorActionPreference = "Stop"
$REPO  = (Get-Location).Path # 建议先 cd 到仓库目录再运行
if (-not (Test-Path "$REPO\docs\zh\index.md")) {
  $REPO = Split-Path -Parent $MyInvocation.MyCommand.Path
  $REPO = (Get-Item $REPO).Directory.Parent.FullName
}
$INDEX = Join-Path $REPO "docs\zh\index.md"
$LINE  = "涉及 magpie 插件/配置时, 先读 $INDEX 及同目录对应页面, 不要凭记忆猜 API。"
$HOME_ = $env:USERPROFILE

function Add-Pointer($file) {
  $dir = Split-Path -Parent $file
  if (-not (Test-Path $dir)) { Write-Host "  skip  $(Split-Path -Leaf $dir) 未安装"; return }
  if ((Test-Path $file) -and (Select-String -Quiet -SimpleMatch -Path $file -Pattern $INDEX)) {
    Write-Host "  skip  $file (已登记)"; return
  }
  Add-Content -Path $file -Value "`n$LINE" -Encoding utf8
  Write-Host "  add   $file"
}

Write-Host "magpie-docs 全局登记 -> $REPO"
foreach ($base in @("$HOME_\.agents\skills", "$HOME_\.claude\skills")) {
  if (Test-Path $base) {
    $link = Join-Path $base "magpie-docs"
    if (-not (Test-Path $link)) { New-Item -ItemType Junction -Path $link -Target $REPO | Out-Null }
    Write-Host "  link  $link"
  }
}
Add-Pointer "$HOME_\.codex\AGENTS.md"
Add-Pointer "$HOME_\.gemini\AGENTS.md"
if (Test-Path "$HOME_\.dsh") {
  Write-Host "  note  dsh: prompt-inject.md 会被 dsh 重写, 请改用项目根 AGENTS.md 或 preset persona(见 README)"
}
Write-Host "完成。文档更新只需跑一次: python scripts\sync.py"
