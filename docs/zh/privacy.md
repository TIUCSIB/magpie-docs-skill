<!-- 来源: https://usemagpie.ai/docs/zh/privacy | 自动同步, 勿手改 -->

# 隐私

你的提示词、回复、密钥和账号只发给你用的供应商，中间没有 magpie 自己的服务器。这一页列出 magpie 在这些请求之外自己发出的所有内容，以及关掉它们的每个开关。内容按代码写成，每一节都附了代码链接。

| 内容 | 发往 | 默认 | 怎么关 |
| --- | --- | --- | --- |
| [每日计数](#count) | PostHog（`us.i.posthog.com`） | 正式版开启；源码构建从不发送 | 设置 → 隐私，`DO_NOT_TRACK=1` |
| [更新检查](#site)、更新说明、合作伙伴列表、图标 | `usemagpie.ai` | 开启 | 更新检查用 `noAutoUpdate`；其余是应用运行所需 |
| [模型目录和汇率](#lists) | `models.dev`、`open.er-api.com` | 开启 | 不可关；不发送任何你的信息 |
| [OTLP 导出](#otel) | 你指定的收集器 | 关闭 | 保持关闭即可 |

## 每日计数

正在运行的正式版 magpie（应用或 `magpie serve`）每天（UTC）向 PostHog 发送一批事件，好让我们知道有多少人在用、该先照顾哪些 agent、供应商和模型。启动时发送，之后每小时看一次，当天已发过就跳过。从源码构建的版本从不发送。

这批事件里有一个 `magpie active`，包含：

- 本机随机生成的 ID（32 位十六进制，与你和这台电脑无关），作为 `distinct_id`；
- magpie 版本、`kind`（`app` 或 `serve`）、系统（`$os`）和架构；
- 用了几个 agent、供应商和模型，以及几个路由组（关掉“分享我用的”后不发送）。

除非你关掉这一部分，后面还有每个 agent、供应商和模型各一个 `magpie uses` 事件，只用 magpie 自己的 ID（每类最多 50 个）：

- **agent**：接入 magpie 的 agent，如 `claude`、`codex`。WSL 发行版名和 omp 配置名会去掉（只记 `omp`）。
- **供应商**：开启的供应商。预设的 ID（`deepseek`）、订阅的（`codex`、`copilot`）、已知社区插件的（`plugin:kiro`）。你自己添加的供应商只记作 `custom`，其他插件只记作 `plugin`。
- **模型**：接入的 agent 设定的模型，记为供应商 ID 加厂商模型 ID（`deepseek/deepseek-v4`）。密钥类供应商上 [models.dev](https://models.dev) 没收录的模型 ID（本地模型、微调模型）只记作 `<供应商>/other`；你自己供应商上的模型记作 `custom`；路由组记作 `group`。

同时发送 `magpie partner` 事件：添加供应商页里排在最前的每个合作伙伴，按它的 ID，在已结束的某一天里被展示、行被打开、Key 页面被打开、从它添加供应商的次数（`what`：`shown`、`opened`、`keys`、`added`；每天每项最多 20 次，添加最多 5 次）。只有次数，从不包含你自己的供应商。

每个事件都带 `$process_person_profile: false`，PostHog 不为这个 ID 建用户档案。不发送名称、Base URL、账号、密钥、提示词、回复和用量。一整批大致如下：

POST https://us.i.posthog.com/batch/

```
{
  "api_key": "phc_nyDyYyrUTRGvNq5U7FBesCyM2j4GdKeqGp8ko7DBerTC",
  "batch": [
    {
      "event": "magpie active",
      "distinct_id": "3f9c…(32 hex)",
      "timestamp": "2026-10-13T08:00:00Z",
      "properties": {
        "version": "0.1.1190", "kind": "app", "$os": "Mac OS X", "arch": "arm64",
        "agents": 2, "providers": 3, "models": 2, "groups": 1,
        "$process_person_profile": false, "distinct_id": "3f9c…"
      }
    },
    { "event": "magpie uses", "distinct_id": "3f9c…", "timestamp": "2026-10-13T08:00:00Z",
      "properties": { "kind": "agent", "id": "claude", "$process_person_profile": false, "distinct_id": "3f9c…" } },
    { "event": "magpie uses", "properties": { "kind": "provider", "id": "custom", … } },
    { "event": "magpie uses", "properties": { "kind": "model", "id": "deepseek/deepseek-v4", … } },
    { "event": "magpie partner", "timestamp": "2026-10-12T12:00:00Z",
      "properties": { "id": "<partner id>", "what": "shown", "count": 3, "day": "2026-10-12", … } }
  ]
}
```

`api_key` 是项目的 PostHog 密钥，只能发送事件，不能读取。代码见 [internal/stats](https://github.com/yetone/magpie/blob/main/internal/stats/stats.go) 和 [partner_events.go](https://github.com/yetone/magpie/blob/main/internal/provider/partner_events.go)。

## 关闭

下面每个开关关掉其中一部分或全部：

- 关掉 设置 → 隐私 → 计入用户数，或在 `settings.json` 里写 `"noStats": true`：整个每日计数。
- 在 magpie 的环境变量里设 `DO_NOT_TRACK=1` 或 `MAGPIE_NO_STATS=1`（除空、`0`、`false` 之外的任何值）：整个每日计数，不管设置里怎么选。
- 关掉 设置 → 隐私 → 分享我用的 agent、provider 和模型，或 `"noUsageStats": true`：`magpie uses`、`magpie partner` 事件和 `magpie active` 里的数量；ID、版本和系统仍会发送。合作伙伴次数也不再记录。
- 关掉 设置 → 关于 → 自动更新，或 `"noAutoUpdate": true`：magpie 自己向 `usemagpie.ai` 询问新版本（否则每 6 小时一次）。这不属于计数。

设置里的改动在下一次每小时检查时生效，不用重启。`settings.json` 在 magpie 的文件夹里（见[下文](#files)）：

settings.json

```
{
  "noStats": true,
  "noUsageStats": true,
  "noAutoUpdate": true
}
```

`MAGPIE_STATS_HOST` 会把计数发到另一个主机（用于测试，设置后源码构建也会发送）。

## 本机上的文件

| 文件 | 用途 |
| --- | --- |
| `install-id` | 随机 ID，第一次发送计数时生成 |
| `stats-sent` | 上次发送的日期（UTC），保证每天只发一次 |
| `partner-counts.json`（缓存文件夹） | 还没发送的合作伙伴次数，最多保留 14 天 |

`install-id` 和 `stats-sent` 在 magpie 的文件夹里：macOS 和 Linux 上是 `~/.config/magpie`，Windows 上是 `%USERPROFILE%\.config\magpie`，设置了 `$XDG_CONFIG_HOME` 时是 `$XDG_CONFIG_HOME/magpie`，便携版则在它的数据文件夹里。`partner-counts.json` 在 `~/.cache/magpie`（或 `$XDG_CACHE_HOME/magpie`，便携版数据文件夹里的 `cache`）。这些文件都可以删：删掉 `install-id` 后，下次发送会生成新的随机 ID，你会被算作新用户；关掉计数后，它们都不会再写入。

## usemagpie.ai 能看到什么

magpie 会向自己的网站请求几样东西，不受隐私设置影响，就像任何应用访问自己的更新服务器。这些请求都不带安装 ID 或账号。

- `/api/latest`：更新信息，每 6 小时一次（开了 `noAutoUpdate` 则不请求），带 `?lang=` 取对应语言的说明。`/api/notes` 在更新后给出“新功能”。
- `/api/partners`：添加供应商页的合作伙伴列表，每 6 小时一次。在有合作伙伴上架时，每十次拉取记一次 `magpie partners fetch` 事件，附 Cloudflare 给出的国家。
- `/go/<合作伙伴>/site` 和 `/go/<合作伙伴>/keys`：在浏览器里打开合作伙伴的官网和 Key 页面链接时，先记一次 `magpie partner go`（哪个合作伙伴、哪个链接、地区、国家），再跳转。
- `/api/icon?url=…`：插件、导入链接和库里的图标经它获取，图标所在的服务器只看到 Cloudflare 的地址，看不到你的。它只转发图片，不计数也不记录。

网站自己的页面（这些文档、首页）带 Cloudflare Web Analytics，不用 Cookie 统计页面访问。应用不加载它。代码见 [site/worker.js](https://github.com/yetone/magpie/blob/main/site/worker.js)。

## magpie 拉取的公开列表

为了给模型定价和命名，magpie 会拉取 [models.dev](https://models.dev) 的模型目录（`models.dev/api.json`）；为了用你的货币显示价格，会从 `open.er-api.com` 拉取美元汇率（缓存 12 小时）。插件及其更新来自 npm 仓库，库里的内容来自 GitHub。这些都是公开数据的普通下载，不发送任何关于你、你的供应商或用量的信息；和任何请求一样，这些主机能看到你的 IP（或代理的 IP）。magpie 还会用你自己的密钥或登录向各个供应商读取额度和模型列表；设置 → 额度 → 额度刷新 → 仅手动 可以只在你要求时才读。

## OTLP 导出

magpie 可以把每个网关请求导出到你自己的 OpenTelemetry 收集器（比如 Langfuse）。它**默认关闭**，只发到你设置的地址，从不发给我们。开启后发送每个请求的 span：agent、供应商、模型、token 数、状态、耗时和估算费用。另有开关可以加上指标、本地 agent 对话，以及请求和回复正文（密钥已遮盖）。在 设置 → 可观测性 里开启，`magpie serve` 也可以用 `MAGPIE_OTEL_ENABLED`、`MAGPIE_OTEL_ENDPOINT`、`MAGPIE_OTEL_HEADERS`、`MAGPIE_OTEL_METRICS`、`MAGPIE_OTEL_SESSIONS`、`MAGPIE_OTEL_BODIES` 和 `MAGPIE_OTEL_BODIES_WHOLE`。只设地址不会开启导出。细节见[参考文档](https://github.com/yetone/magpie/blob/main/docs/reference.md#otlp-export)。

## 为什么计数默认开启

magpie 支持几十个 agent 和供应商，维护的人不多。每日计数让我们知道大家实际在用哪些，好先保证它们能用。正式版默认开启，是因为只靠主动开启的人，数量太少，看不出这些。作为交换，它尽量少：一个随机 ID、内置 ID 和数字；一个开关或 `DO_NOT_TRACK=1` 就能关掉，源码构建从不发送，发送的全部内容都列在这一页。
