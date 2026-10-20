<!-- 来源: https://usemagpie.ai/docs/zh/integrate | 自动同步, 勿手改 -->

# 接入你的应用

写给 AI 应用、Agent 或客户端的开发者：想让自己的应用和 magpie 配合好，有三个层次，从 magpie 这边什么都不用改，到在 Agents 页面拥有自己的一行。

| 你想要 | 做法 | magpie 需要改动 |
| --- | --- | --- |
| 应用的请求由 magpie 提供服务，并在用量里以自己的名字统计 | [直接调用网关](#gateway) | 无 |
| Agents 页面上的一行：自动检测、在那里选模型、断开时还原 | [Agent 适配器](#agent) | 一个 PR |
| 新的模型来源（订阅、厂商），或改写请求 | [插件](#plugins) | 无 |

## 1. 直接调用网关

magpie 在本机运行一个 LLM 网关。用户在 magpie 里有的所有模型（订阅、API key、本地模型、路由组）都以各自的 id 在那里提供，所以你的应用只需要一个供应商条目，而不是每个厂商一个。

### 找到它

网关监听 `127.0.0.1:3425`，或 magpie 的 `settings.json` 里 `port` 指定的端口（`~/.config/magpie/settings.json`，Windows 上是用户目录下的同一路径；设置了 `$XDG_CONFIG_HOME` 时为 `$XDG_CONFIG_HOME/magpie`）。`GET /api/hello` 在是 magpie 时返回 `{"name":"magpie","version":"…"}`。这个文件只读、不要写。magpie 需要在运行（应用本身或 `magpie serve`）；找不到时，你的应用照常提供它自己的供应商即可。

Shell

```
curl -s http://127.0.0.1:3425/api/hello
curl -s http://127.0.0.1:3425/v1/models -H "Authorization: Bearer magpie-acme"
```

### 端点

厂商本身支持你的 API 时请求原样转发，否则会被转换，流式、工具调用、图片和推理都包括在内。OpenAI 客户端的 base URL 是 `http://127.0.0.1:<port>/v1`，Anthropic 或 Gemini 客户端是 `http://127.0.0.1:<port>`。

| 路径 | API |
| --- | --- |
| `/v1/chat/completions` | OpenAI Chat Completions |
| `/v1/responses` | OpenAI Responses |
| `/v1/messages`、`/v1/messages/count_tokens` | Anthropic Messages |
| `/v1beta/models/{model}:generateContent`（以及 `:streamGenerateContent`） | Google Gemini |
| `/v1/models` | 模型目录 |

### 用 key 标明你的应用

在本机，网关接受任意 key。发送 `magpie-<你的应用 id>`（`Authorization: Bearer magpie-acme`，或 `x-api-key`），每次调用都会在用量、请求记录以及按 Agent 匹配的路由规则里记为 `acme`。不带它时，magpie 按 `User-Agent` 的第一个词统计（`Acme/1.4 (darwin)` 记为 `Acme`）；SDK 自带的 User-Agent（`OpenAI/JS …`、`ai-sdk/…`）会被记成那个 SDK。从另一台电脑访问时（设置 → 局域网共享），key 必须是用户的网关密钥之一，应用名就靠 User-Agent。

### 模型

`GET /v1/models` 列出用户打开的模型：`id`（`provider/model`，或路由组的名字，原样发送即可）、`display_name`、`owned_by`（供应商）、`reasoning` 与 `supported_reasoning_levels`（`[{"effort":"low"},…]`；同样的档位以纯名字列在 `reasoning_levels`），已知时还有 `context_window`、`max_output_tokens`，以及 magpie 知道是否支持图片时的 `modalities`。请从这里读取，而不是内置一份列表：用户会在 magpie 里增删供应商。推理强度用你所用 API 自己的字段传（`reasoning_effort`、`reasoning.effort`、Anthropic 的 `thinking` 或 `output_config.effort`）。`?format=text` 每行一个 id。

### 可选

在同一会话的请求里带上 `X-Magpie-Session: <id>`，`GET /v1/magpie/route?session=<id>` 就能在第一个 token 之前告诉你路由组为这一轮选了哪个模型、尝试过哪些后备（用 `after=<seq>&wait=<s>` 长轮询）。`GET /v1/magpie/quotas` 列出用户各订阅的额度，`GET /v1/magpie/usage` 和 `/v1/magpie/usage/requests` 给出用量页的统计和逐条请求（带 `session`；Claude Code 子代理的调用还有 `subagent`/`parent_agent`）。它们只回答本机，或带网关密钥的其他机器；限了额度、模型或账号的密钥只看得到自己的调用和路由，额度不告诉它，除非它的主人允许它看自己可用部分的额度（`magpie gateway-key quotas <id> on`；它自己的限额见 `GET /v1/magpie/limit`）。你的应用直接发给厂商、不经过 magpie 的调用，可以用 `POST /v1/magpie/usage/requests` 上报（每次一条，或最多 5000 条，格式同 `usage.jsonl` 的一行，每条带 `rid`；过去的时间照原样保留，所以可以补录历史）。它们在用量页上标为上报，且从不计入密钥的限额。细节见[参考文档](https://github.com/yetone/magpie/blob/main/docs/reference.md#connecting-anything-else)。

**保留用户自己的供应商。**把 magpie 作为又一个供应商（名为 Magpie）加在用户已有的供应商旁边，而不是替换它们，这样关掉 magpie 就只是换选另一个供应商。

## 2. 在 Agents 页面占一行

magpie 列出的 Agent（Claude Code、Codex、OpenCode、dsh、Alma、Cindy……）都是 [`internal/agent`](https://github.com/yetone/magpie/tree/main/internal/agent) 里的适配器，每个一个文件。有了这一行，你的应用会显示自己的名字和图标，安装后自动出现，用户可以从 magpie 的目录里为它选模型（和推理强度），供应商变化时跟着更新，断开时还原你的应用原来的设置。目前没有运行时注册：这一行通过给 magpie 提 PR 加入，随下一个版本发布。

适配器是一个 [`Agent`](https://github.com/yetone/magpie/blob/main/internal/agent/agent.go) 值，形态取决于你的应用提供什么：

- **magpie 编辑你的配置文件**（大多数适配器，如 [`fx.go`](https://github.com/yetone/magpie/blob/main/internal/agent/fx.go)、[`empryo.go`](https://github.com/yetone/magpie/blob/main/internal/agent/empryo.go)）。`Dir`、`Path`、`Bin` 用来检测应用；每个 `Field`（`model`、`effort`……）有 `Get`、`Set`、`Options`。连接时加入一个指向网关、key 为 `magpie-<id>` 的 `magpie` 供应商，并把模型设为 magpie 的模型；选回默认或 `Unwire` 会移除 magpie 的条目并还原原值。只动 magpie 设置的那些键。`Notice` 提示何时需要重启应用；`Sync` 更新你的应用保存在文件里的模型列表。
- **你的应用只通过自己的导入链接接收供应商，由用户在你的应用里确认**（[`cindy.go`](https://github.com/yetone/magpie/blob/main/internal/agent/cindy.go)）。`Import` 返回这个链接（`yourapp://provider/import?…`，带网关地址、key `magpie-<id>` 和各端点），这一行的按钮会打开它，用户在你的应用里确认一次即可。`Added` 只读地检查你的应用是否已经有 magpie。magpie 不写你的任何文件。适合把供应商存在数据库里或加密保存的应用——这也最接近“检测到 magpie → 用户确认一次 → 完成接入”。
- **你的应用运行时有本地 API**（如 Alma）：magpie 通过它把自己加为供应商并设置默认模型。

一个 PR 需要：适配器及其在 `agents.go` 里的注册；`UA`（你的 User-Agent 开头，小写），让用量认得你的调用；`internal/gui/assets/icons` 里的图标；在临时 `HOME` 下运行的测试（连接、切换、断开后原文件还原）；参考文档 Agents 表里的一行。最有帮助的是一个稳定、有文档的配置格式或导入链接，以及它在各系统上的位置。

## 3. 插件

插件是 magpie 运行的 npm 包，由用户在 设置 → 插件 里或用 `magpie plugin add <package>` 安装。**供应商插件**（OpenCode 的 `auth` 钩子或 pi 扩展包）添加一个模型来源，比如 magpie 自己不登录的订阅。**网关中间件**在请求和回复经过时改写它们。见[插件开发](https://usemagpie.ai/docs/zh/plugins)。插件不能在 Agents 页面加一行，也不能写别的应用的配置，所以它不是应用注册自己的方式。

## 目前没有的

- 没有让别的应用不经用户就把自己注册为 Agent、或安装插件的 API 或链接：插件由用户在 magpie 里安装，Agent 行来自 magpie 源码里的适配器。
- `magpie://import` 链接添加的是*供应商*（模型来源及其 key），不是 Agent 或应用：见 [Add to magpie](https://usemagpie.ai/docs/zh/import)。

有问题，或想先讨论一个适配器：提一个 [issue](https://github.com/yetone/magpie/issues)，或来 [Discord](https://discord.gg/vGSnD3ZKQF) 聊。
