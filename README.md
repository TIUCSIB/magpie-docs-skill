# magpie-docs — Magpie 文档离线镜像(给 AI Agent 用)

每次让 AI 写 Magpie 插件都要重新粘贴文档?这个项目把 [usemagpie.ai 中文文档](https://usemagpie.ai/docs/zh/start) 整站抓成干净的 Markdown,配一次,让**各种 Agent 都能本地读取**,不再重复投喂。

- **零第三方依赖**:同步脚本只用 Python 标准库,`docs/` 是静态文件。
- **全量**:`start / intent / plugins / remote / docker / privacy / import / integrate` 八页,代码块与表格保真。
- **跨工具**:同时提供 `SKILL.md`(Claude Code / ZCode)、`AGENTS.md`(Codex / OpenCode / Cursor / Zed)、`GEMINI.md`(Gemini CLI)三种入口,内容一致。

## 目录结构

```
magpie-docs/
├── SKILL.md          # Claude Code / ZCode 技能入口(带触发 frontmatter)
├── AGENTS.md         # 通用 agent 指令(Codex/OpenCode/Cursor/Zed 自动读)
├── GEMINI.md         # Gemini CLI 入口
├── docs/zh/          # 八页正文 + index.md 总览(自动生成, 勿手改)
└── scripts/sync.py   # 抓取 + HTML→Markdown, 文档改版时重新同步
```

## 一次安装,全局共用(推荐给所有 Agent)

**不用每个 agent 各放一份。** 把仓库克隆到固定位置一次,让所有工具都指向这同一份 `docs/`。skill 目录用软链接,其余工具只追加一行"去哪读"的指针——零复制、共享同一份、`sync.py` 一刷新全员同步。

```bash
# 1) 克隆到固定位置(全局共用一份)
git clone https://github.com/TIUCSIB/magpie-docs-skill.git ~/magpie-docs
cd ~/magpie-docs

# 2) 一键登记到所有已装的工具(脚本只加指针, 不复制文档)
bash install.sh            # Git Bash / Linux / macOS
# 或 Windows PowerShell:  .\install.ps1
```

脚本对每个工具做的事:

| 工具 | 做法 | 位置 |
|------|------|------|
| **ZCode / Claude Code** | 软链接整个 skill(自动触发) | `~/.agents/skills/magpie-docs` → `~/magpie-docs` |
| **Codex / OpenCode / Cursor / Zed** | 追加一行指针 | `~/.codex/AGENTS.md`(等) |
| **Gemini CLI** | 追加一行指针 | `~/.gemini/AGENTS.md` |
| **dsh** | 项目根 `AGENTS.md`,或自定义 preset 的 persona prefix | 见下方说明 |

> dsh 的 `~/.dsh/prompt-inject.md` 由 dsh 自己生成/重写, 手动追加的内容会被覆盖, 因此脚本不写它。推荐在需要用 magpie 的项目根放一个 `AGENTS.md`(直接复制本仓库的), 或在 dsh 的 agent preset(`agent.cordis.yml` 的 persona `prefix`)里加一句指向本仓库。

指针内容都一样,只有安装路径不同:

```
涉及 magpie 插件/配置时, 先读 <仓库绝对路径>/docs/zh/index.md 及对应页面, 不要凭记忆猜 API。
```

> 关键:入口文件都让 AI **先读 `docs/zh/index.md` 再按需打开具体页**,而不是把全文塞进上下文——省 token 又准确。所有工具共享同一份 `docs/`,只有一处需要 `sync.py` 更新。

### 手动接法(不想跑脚本时)

```bash
# ZCode/Claude Code 全局 skill
ln -s ~/magpie-docs ~/.agents/skills/magpie-docs
ln -s ~/.agents/skills/magpie-docs ~/.zcode/skills/magpie-docs   # 重开会话生效

# 其余工具: 各加一行指针(路径换成你的)
echo "涉及 magpie 插件/配置时, 先读 ~/magpie-docs/docs/zh/index.md 及对应页面。" >> ~/.codex/AGENTS.md
echo "涉及 magpie 插件/配置时, 先读 ~/magpie-docs/docs/zh/index.md 及对应页面。" >> ~/.gemini/AGENTS.md
```

**dsh**:在需要的项目根放 `AGENTS.md`(复制本仓库的即可), 或改 dsh agent preset 的 persona prefix 指向本仓库——全局 `prompt-inject.md` 会被 dsh 重写, 别写它。

## 更新文档

```bash
python scripts/sync.py                 # 抓最新 zh, 重新生成 docs/
python scripts/sync.py --langs zh,en,ja
python scripts/sync.py --local         # 用 _raw/ 缓存离线调试
```
需要联网;生成的 `docs/**/*.md` 顶部带来源注释,请勿手改(会被下次同步覆盖)。
