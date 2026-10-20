#!/usr/bin/env bash
# 全局登记 magpie-docs: 只放指针, 不复制文档。所有工具共享同一份 docs/。
# 用法: bash install.sh   (Git Bash / Linux / macOS)
set -euo pipefail

# POSIX 路径(软链接用): /f/... 或 /home/...
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Windows 原生路径(写进指针用): Git Bash/MSYS 下转成 F:/..., 真 Linux/macOS 保持原样
if INDEX="$(cd "$REPO" && pwd -W 2>/dev/null)"; then :; else INDEX="$REPO"; fi
INDEX="$INDEX/docs/zh/index.md"
LINE="涉及 magpie 插件/配置时, 先读 $INDEX 及同目录对应页面, 不要凭记忆猜 API。"

link_skill() {  # ZCode / Claude Code: 链接整个 skill(自动触发)
  # 优先 Windows junction(agent 原生可解析), 退回软链接(Linux/macOS)。已存在则跳过。
  # 全程用正斜杠: PS 与文件系统都接受, 免去反斜杠转义。
  make_link() { # $1=link $2=target (均为 POSIX 路径)
    local link="$1" target="$2"
    if [ -e "$link" ] || [ -L "$link" ]; then echo "  skip  $link (已存在)"; return 0; fi
    if [ "${OS:-}" = "Windows_NT" ] && command -v powershell.exe >/dev/null 2>&1; then
      local wl wt
      wl="$(cd "$(dirname "$link")" && pwd -W)/$(basename "$link")"
      wt="$(cd "$target" && pwd -W)"
      powershell.exe -NoProfile -Command "New-Item -ItemType Junction -Path '$wl' -Target '$wt' | Out-Null" \
        && { echo "  jct   $link -> $target"; return 0; }
    fi
    ln -sfn "$target" "$link" && echo "  link  $link -> $target"
  }
  for base in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
    [ -d "$base" ] || continue
    make_link "$base/magpie-docs" "$REPO"
  done
  if [ -d "$HOME/.zcode/skills" ]; then
    make_link "$HOME/.zcode/skills/magpie-docs" "$REPO"
  fi
}

append_pointer() {  # 其余工具: 幂等追加一行指针(目录不存在则跳过, 不瞎猜工具装没装)
  local f="$1"
  [ -d "$(dirname "$f")" ] || { echo "  skip  $(basename "$(dirname "$f")") 未安装"; return 0; }
  [ -f "$f" ] || touch "$f"
  if grep -qF "$INDEX" "$f" 2>/dev/null; then
    echo "  skip  $f (已登记)"
  else
    printf '\n%s\n' "$LINE" >> "$f"
    echo "  add   $f"
  fi
}

echo "magpie-docs 全局登记"
echo "  skill 实体: $REPO"
echo "  指针指向 : $INDEX"
link_skill
append_pointer "$HOME/.codex/AGENTS.md"      # Codex(OpenCode/Cursor/Zed 同理, 见 README)
append_pointer "$HOME/.gemini/AGENTS.md"     # Gemini CLI 全局
# dsh: ~/.dsh/prompt-inject.md 由 dsh 自身生成, 手动追加会被重写覆盖, 因此不写全局;
# 在你要用的 dsh 项目根放一个 AGENTS.md(内容见 AGENTS.md 模板)或自定义 preset 的 persona prefix。
if [ -d "$HOME/.dsh" ]; then
  echo "  note  dsh: prompt-inject.md 会被 dsh 重写, 请改用项目根 AGENTS.md 或 preset persona(见 README)"
fi
echo "完成。文档更新只需跑一次: python scripts/sync.py"
