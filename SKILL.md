---
name: magpie-docs
description: Magpie (usemagpie.ai) 本地模型网关的官方中文文档离线镜像。当需要为 Magpie 编写/调试插件(供应商插件、OpenCode 兼容、Bun 宿主),或配置意图路由/路由组、供应商管理、Docker 部署、远程共享、Add to magpie、接入任意 Agent(Claude Code / Codex / Gemini CLI / OpenCode),或询问 Magpie 的 API、钩子(config/auth/loader/provider.models/chat.headers)、网关中间件、MCP 工具、页面/面板、测试与发布时使用。即使用户没说"文档/skill",只要涉及 magpie 插件或配置就应触发。
---

# Magpie 文档 Skill

本 skill 携带 **usemagpie.ai 全部中文文档的离线 Markdown 镜像**(自动同步生成)。写 Magpie 插件或做配置时,**先读本地文档,不要凭记忆猜 API**——Magpie 的钩子签名、字段名、生命周期都以文档为准。

## 核心事实(速查,细节看 docs/)

Magpie 是跑在 `127.0.0.1:3425` 的本地模型网关,同时支持 OpenAI / Anthropic / Gemini 三种 API 并互相转换,为多个 Agent 统一选模型/路由。

**插件**基于 **OpenCode 供应商插件兼容层**,运行在 **Bun 宿主进程**中。一个插件是 npm 包 / git 仓库 / 文件夹,模块导出一个 **async 函数**,返回一组钩子:

- `config` — 声明供应商 id、名称、npm 包、API 地址、默认模型
- `auth` — 含 `provider`、`methods`(api/oauth)、`loader`、`usage`、`refresh`
- `loader` — 为每个账号生成 fetch 配置
- `provider.models` — 按账号动态返回模型列表
- `chat.headers` — 为每个请求注入自定义头

生命周期:加载 → `config` 声明供应商 → `auth` 提供登录 → `loader` 生成 fetch → `provider.models` 列模型 → `auth.usage`/`refresh` 上报用量/续期。增删改开关插件会**重启宿主**。

除供应商外还支持:网关中间件(moejs 运行,改写请求/事件)、Agent 插件(接外部 CLI)、页面/面板(沙盒 iframe)、工具(经 MCP 暴露给任意 agent)、异步请求钩子、路由策略与用量记录。

## 工作流程

1. 读 `docs/zh/index.md` 定位相关页面。
2. **写/改插件** → 读 `docs/zh/plugins.md`(含完整 Acme 供应商示例、包结构、测试沙箱、npm 发布、社区仓库 `magpie-community/plugins` 的 `registry.json`)。
3. **路由/选模型** → `docs/zh/intent.md`;**接入某 Agent** → `docs/zh/integrate.md`;**部署** → `docs/zh/docker.md` / `docs/zh/remote.md`;**隐私** → `docs/zh/privacy.md`;**添加供应商** → `docs/zh/start.md`。
4. 按文档的钩子签名和字段名编写,示例优先照抄文档结构再改。

## 维护

文档改版后重新同步(需联网,只用 Python 标准库):

```bash
python scripts/sync.py            # 抓最新, 重新生成 docs/
python scripts/sync.py --langs zh,en,ja
```
