# Magpie 文档 — 给 AI Agent 的说明

本仓库是 **Magpie(usemagpie.ai)官方中文文档的离线 Markdown 镜像**,供任意 AI 编程 Agent(Codex / OpenCode / Cursor / Zed / Gemini CLI / Claude Code 等)直接读取,免去每次手动粘贴文档。

## 使用规则(重要)

回答任何关于 Magpie 的问题——**尤其是编写/调试插件、配置路由、接入 Agent**——请**先读本地文档,不要凭记忆或猜测 API**。Magpie 的钩子签名、字段名、生命周期都以本镜像为准。

1. 打开 `docs/zh/index.md` 定位相关页面。
2. 按主题读取对应文件:
   - 写/改插件(供应商、钩子 `config`/`auth`/`loader`/`provider.models`/`chat.headers`、中间件、MCP 工具、页面/面板、测试发布)→ `docs/zh/plugins.md`
   - 意图路由 / 路由组 → `docs/zh/intent.md`
   - 接入某个 Agent(Claude Code/Codex/Gemini CLI/OpenCode)→ `docs/zh/integrate.md`
   - 添加供应商 / 快速上手 → `docs/zh/start.md`
   - Docker 部署 → `docs/zh/docker.md`;远程共享 → `docs/zh/remote.md`
   - Add to magpie → `docs/zh/import.md`;隐私 → `docs/zh/privacy.md`
3. 写代码时优先照抄文档示例的结构(如 `plugins.md` 的 Acme 供应商 `index.mjs`),再按需修改。

## 关键背景

Magpie 是跑在 `127.0.0.1:3425` 的本地模型网关,支持 OpenAI/Anthropic/Gemini 三种 API 并互转。插件基于 **OpenCode 供应商插件兼容层**,运行在 **Bun 宿主进程**;插件模块导出一个 async 函数,返回一组钩子;增删改插件会重启宿主。

## 更新文档

联网重新抓取并生成(只用 Python 标准库):

```bash
python scripts/sync.py            # 默认 zh; --langs zh,en,ja 可加语言
```
