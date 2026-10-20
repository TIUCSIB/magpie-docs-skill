<!-- 来源: https://usemagpie.ai/docs/zh/start | 自动同步, 勿手改 -->

# 快速上手

magpie 是给你所有 Agent 统一选模型的地方。先把你有的供应商加进来，再给每个 Agent 选一个模型；magpie 会把它写进那个 Agent 自己的配置文件。

背后是一个跑在你本机 `127.0.0.1:3425` 的小网关。它同时支持 OpenAI、Anthropic 和 Gemini 三种 API，并在它们之间互相转换（流式输出、工具调用都支持），所以任何 Agent 都能用任何供应商的模型：Claude Code 用 ChatGPT 订阅里的 GPT 模型，Codex 用 DeepSeek，OpenCode 用你的 Claude 订阅。

### 供应商

模型从哪里来：登录的订阅、有 API 密钥的厂商、你自己的接口地址。每个模型都写作 `provider/model`。

### Agent

使用模型的工具：Claude Code、Codex、Gemini CLI、OpenCode 等。每个一行，显示它当前用的模型。

### 网关

通过 magpie 选模型时，Agent 指向的本地地址。它把每个请求转给提供该模型的供应商。

### 路由组

可选。把多个模型或账号合成一个给 Agent 选，`group/<id>`，一个额度用完时换下一个。

1. **添加供应商**登录你的订阅，粘贴 API 密钥。只需做一次。
2. **给每个 Agent 选模型**点 Agent 的模型，选一个。magpie 改写那个 Agent 的配置。
3. **开一个新会话**Agent 启动时读取配置，下一个会话就用上新模型。

## 1 · 添加供应商

打开 供应商 标签页，点 ＋ 添加供应商。点选一个卡片，或输入厂商名字查找。

添加供应商：登录订阅、选厂商，或填任意兼容的 URL。

### 订阅 · 登录即可，无需密钥

Claude（Pro、Max、Team）、ChatGPT（Plus、Pro、Business）、Cursor、Grok（SuperGrok）、Copilot 和 Devin。点卡片后 magpie 会在浏览器里打开厂商自己的登录页，登录完成后账号立刻出现（Copilot 会给你一个验证码，在 GitHub 页面上输入）。订阅是在 magpie 里添加的，不需要先去别的 Agent 里登录。

- **多个账号。**再点一次 Claude 或 ChatGPT 卡片即可再加一个；它们都列在这个供应商下面，点一下就能切换使用哪个。
- **已经登录过？**本机上已经登录的 Agent 也会作为供应商出现，显示为 *已登录 …*。
- **所有 Agent 都能用。**订阅里的模型在其他 Agent 的选择列表里写作 `claude/…`、`codex/…`、`copilot/…`。Claude 订阅的请求通过本机安装的 Claude Code 运行，所以请保留 Claude Code。

### 供应商（厂商预设）

Anthropic、OpenAI、Google Gemini、DeepSeek、Kimi、Zhipu GLM、MiniMax、Qwen、Mistral、Groq、xAI 等。选一个，粘贴密钥（获取密钥 ↗ 会打开厂商的密钥页面），保存。magpie 会向厂商询问它提供哪些模型并列出来；展开供应商那一行可以选择给 Agent 暴露哪些模型，或点 测试。

### 本机

Ollama 和 LM Studio，无需密钥。

### 自定义 · 任意兼容的 URL

其他接口都走这里：填 名称、OpenAI 兼容 地址（以 `/v1` 结尾）、Anthropic 兼容 地址（根地址，即 `ANTHROPIC_BASE_URL` 的值），或两个都填，再填密钥。接口支持几种 API 就填几种；每个 Agent 用它原生的那种，其余由 magpie 转换。

**之前在 Claude Code 或 Codex 里配过供应商？**面板顶部的 导入… 会读取 Claude Code 的 `settings.json` 和 Codex 的 `config.toml`，不改动它们，把你勾选的供应商导入进来。

密钥保存在 `~/.config/magpie/providers.json`，只有你自己可读。magpie 从不读取 shell 环境变量里的密钥：你添加什么，它就用什么。

## 2 · 给每个 Agent 选模型

Agent 标签页里，本机装了或配置过的每个 Agent 各占一行。magpie 支持 Claude Code、Codex、Gemini CLI、OpenCode、MiMo Code、DevEco Code、Pi、Goose、Cursor CLI、Copilot CLI、Crush、DeepSeek Harness、Command Code、omp、OmO、Devin、Hermes Agent、MiniMax Code、Grok Build、ZCode、OpenHanako 和 Alma。

每个 Agent 一行，可以选任意供应商的模型；方案一键切换全部设置。

- **点模型**打开选择列表。模型分组显示：Agent 自带的、你的路由组、再是你添加的每个供应商。输入可以筛选，也可以直接输入列表里没有的模型 ID。
- **推理强度**：Agent 有这个选项时（Codex 的 *推理强度*、Pi 的 *思考*），列表下方会出现滑块。
- **Claude Code 通过 magpie 使用模型时**，opus、sonnet、haiku 各档还可以单独指定模型；默认跟随主模型。

选好的模型会写进 Agent 自己的配置文件。只改 magpie 需要的那几个键；注释、顺序、缩进都保留，写入是原子的。

| Agent | 通过 magpie 选模型时写入什么 |
| --- | --- |
| Claude Code | `~/.claude/settings.json`：`env` 里的 `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN` 和模型变量 |
| Codex | `~/.codex/config.toml`：一个 `[model_providers.magpie]` 表和模型，模型列表写在 `magpie-models.json`。你的 ChatGPT 登录不受影响 |
| OpenCode、MiMo Code、DevEco Code、Pi、Crush | 一个 `magpie` 供应商条目，以及 `magpie/provider/model` |
| AtomCode | `~/.atomcode/config.toml`：一个 `magpie` 供应商账号，以及目录中每个模型各自的条目 |
| Snow CLI | `~/.snow/profiles/magpie.json`：一个 `magpie` 配置文件，并设为当前配置（Snow App 用“同步 Snow CLI API 配置”导入） |
| Gemini CLI | `GOOGLE_GEMINI_BASE_URL` 指向网关、API 密钥认证，以及模型 |

**已在运行的会话保持它启动时的模型。**Agent 启动时读取配置，所以改动从下一个会话生效。Codex 也在启动时生成模型列表：切换后请重启 Codex 应用和已打开的 `codex` 会话。

**Paseo、编辑器插件等**替你运行 Claude Code 或 Codex 的前端，启动的是同一个 CLI，读的也是同一份 `~/.claude` 或 `~/.codex` 配置。在 magpie 里设一次模型，它们从下一个会话起也会用上。

## 3 · 可选：路由组

每个供应商只有一个账号时可以跳过这一步。等你有了多个——比如两个 ChatGPT 账号，或者同一个模型既有订阅又有密钥——再来设置。

路由组：多个模型或账号合成一个名字，按智能或顺序切换。

### 一个供应商里的多个账号或密钥

展开供应商那一行，勾选要用的每个账号或密钥。路由 决定请求怎么分给它们：智能（默认）、按顺序、轮流、用量少的优先 或 重置前用完。备用 里列出这个供应商额度用完、被限流或不可用时改用的模型。

### 跨供应商的同一个模型

路由组是几个模型（来自一个或多个供应商），Agent 把它当作一个来选：`group/<id>`，在选择列表的 *路由组* 下面。两个供应商用同一个名字提供的模型会自动成组；在 路由 标签页点 新建组 可以把任意模型组到一起。排第一的模型决定这个组对外的能力。

**不用手动建的组。**再加一个供应商，只要它提供的模型和已有的同名（比如 Claude 订阅和 Copilot 都有 Claude Opus，DeepSeek 官方 API 和 OpenRouter 都有 DeepSeek），magpie 就会自动把它们组成一个路由组：`group/auto-<模型>`，包含所有提供这个模型的供应商。名字按各家不同的写法匹配（`deepseek/deepseek-chat` 和 `deepseek-chat` 算同一个）。给 Agent 选这个组，请求就会分摊到这些供应商上；不想要的可以用 `magpie group rm` 隐藏。

| 路由 | 谁排在前面 |
| --- | --- |
| 智能 `smart` | 默认。把成员的账号和 Key 放在一起排（组里的路由组算一个，见下文）：还有余量的订阅里，额度最先重置的排第一。看周额度的重置时间；只有 5 小时额度、没有周额度的账号（如 Claude Enterprise）看它的 5 小时重置，所以排在所有更晚重置的周额度前面。没有重置时间的积分（WorkBuddy 的积分包，各自到期）按剩余积分最早过期的时间算，所以积分最先过期的 WorkBuddy 账号排第一。失败后在休息的排最后。 |
| 按顺序 `order` | 先用第一个模型，它答不了再换下一个。 |
| 轮流 `rotate` | 会话的每一轮交给下一个成员的账号或 Key，均摊负载。 |
| 最少使用 `usage` | 剩余额度最多的账号或 Key 排第一。 |
| 重置前用完 `pace` | 每周剩余额度除以距重置的小时数，最高的账号排第一——重置时损失最多的那个——少让成员的周额度到重置时作废；只有 5 小时额度、没有周额度的账号（如 Claude Enterprise）按 5 小时窗口的剩余额度除以距它重置的小时数算，所以几乎总排第一。用到 90% 以上的等其他账号都答不了时才用。Key 按最近发给它的 token 数排。 |
| 按权重 `weight` | 每个模型按群组编辑器里它旁边设的权重（1 到 1000，不设为 1）分得请求：权重 3 的模型每拿三个，权重 1 的拿一个，均匀穿插而不是成批。每个模型按它自己提供方的路由用自己的账号或 Key，群组里的群组算一个成员。失败后歇着的那个退出这一轮；一个失败时，下一个模型接上。 |

| 会话保持 | 会话在回答过它的账号或 Key 上留多久 |
| --- | --- |
| 自动 `auto` | 默认。一轮之内总是保持，跨轮则在厂商缓存还值得保留时保持。 |
| 整个会话 `session` | 整个会话，只要它还能回答。 |
| 一轮之内 `turn` | Agent 回传工具结果时不换；你再次发言时，路由重新决定。 |
| 关闭 `off` | 每个请求都重新路由。 |
| 严格 `strict` | 绝不换到别的账号或密钥，即使超过其用量上限也一样：它被限流或额度用完时，错误直接交给 Agent。新会话照常路由。 |

### 规则 · 把某类对话交给指定模型

路由组的 规则 把符合条件的一轮对话交给组里指定的模型：够长（`tokens ≥ N`）、带图片、要求推理（开启，或不低于某个强度）、来自某些 Agent，用户想做的事符合你描述的*意图*、Agent 正在压缩上下文，或者 Agent 在某些文件夹（项目）里工作。一条规则的条件要同时满足，所以可以写“在 ~/work/acme 里，并且够长”。每次你发新消息时从上往下检查，第一条命中的规则把它的模型排在最前，其余成员排在后面做故障转移。没有命中任何规则的一轮照组本来的方式路由，并保持在原来的账号上。

- 规则只在一轮开始时决定；Agent 回传工具结果的过程中一直留在那个模型上，不会半途换掉而丢掉厂商的缓存。唯一例外：这一轮涨到超过所在模型的上下文，会换到装得下的成员。
- token 数取请求大小的估算与厂商对这个会话上一个请求的计数中较大的一个。请留出余量：给 200k 的模型设 150k，而不是 199k。
- 子代理是单独的会话，规则可以把它发到别处，主代理仍留在原处。
- 意图是用几个词描述用户想做什么，例如“写或修测试”“一个简单问题”。每一轮开始时，magpie 会问一次组里指定的意图判断模型：用户这条消息属于哪个可能命中的意图。这个模型可以是 magpie 里的任意模型，建议选小而快、不带推理的。发过去的只有这条消息，不包括整段对话。它出错、超时（8 秒）或给不出答案时，意图条件都不命中，这一轮按其他规则走。如果前面有不带意图的规则已经能决定，就不会去问；同一条消息也不会问两次。它的调用在用量里显示为 magpie 自己的调用。它具体被问了什么、回答怎么用、失败时怎么办，详见[意图路由](https://usemagpie.ai/docs/zh/intent)。
- 压缩上下文时：Agent 压缩对话上下文时命中——Claude Code 的 `/compact` 和自动压缩、Codex、OpenCode、Pi、Gemini CLI、Qwen Code、Kimi Code——让更便宜、更快的模型来写总结，对话本身仍留在原来的模型上。压缩请求单独决定：它所在的这一轮和缓存都留在原处。对话比规则里的模型能装下的还长时，改由下一条命中的规则或组本来的顺序决定。
- **时段和星期。**规则可以只在某些时段、某几天生效，按这台电脑的时钟——比如厂商的高峰期。把这段时间的对话“先发给”别的模型，厂商那个模型仍排在后面做故障转移。要把它完全拿掉，在规则的 ⋯ 菜单里选 改为暂停该模型：规则生效期间（它的时段、星期和 Agent），这个模型移出分组——不排第一、不做备用、也不会因为会话粘性被留住——时段过了自动回来。暂停只按时段、星期和 Agent 判断；组里所有模型都被暂停时，会告诉 Agent。
- **文件夹。**项目文件夹：Agent 的工作目录是你列出的文件夹之一或其子文件夹时命中：`~/work/acme` 包括 `~/work/acme/web`，不包括 `~/work/acme-old`。文件夹以 Agent 在请求里告诉模型的为准——Claude Code、Codex、OpenCode 和 Pi 都会说——不说明工作目录的 Agent 不会命中任何按文件夹的规则。`~` 是你的主目录，`C:\work` 也就是 WSL 里的 `/mnt/c/work`，macOS 和 Windows 上不区分大小写。
- **推理强度。**规则还可以设定它的模型用什么推理强度，让一个意图同时选定模型和推理强度：在规则的 ⋯ 菜单里选 设定推理强度，或在终端用 `use-effort=low`。不管 Agent 要求什么，该模型都按这个推理强度发送，取模型最接近的档位；magpie 不知道档位的模型，以及排在它后面做备用的模型，按 Agent 的要求发送。详见[意图路由](https://usemagpie.ai/docs/zh/intent#effort)。
- 路由标签页会显示每一轮是被哪条规则送到哪里的、意图判断模型给出的答案，以及 Agent 说的工作目录。

### 路由组里放路由组

路由组的成员也可以是另一个路由组：在 添加模型 的 *路由组* 分类里选它，或者在终端里用 `models+=group/<id>`。子组占据它在顺序里的位置，在自己的模型之间按自己的路由方式和规则分配。比如 Coder 可以是 `deepseek-v4-pro`，然后是 *Fast*，而 Fast 是几个便宜模型的顺序。Coder 的规则可以把一轮对话交给 `group/fast`，再由 Fast 自己的规则决定它里面哪个模型排第一。

- **不会无限递归。**一个组不能包含它自己，无论是直接包含，还是经由它里面的组间接包含。Coder 已经包含 Fast 时，再把 Coder 放进 Fast 会被拒绝，选择器里也不会列出这样的组。最多嵌套 8 层。一个组被别的组包含时不能删除，要先从那个组里移除它。
- **每一层按自己的路由。**外层组不管用什么路由，都不会伸进它里面的组：智能、轮流、最少使用、重置前用完都把子组当作一个成员，拿子组自己会先用的那个账号或 Key 来比；排到它时，子组按自己的顺序整体尝试。Coder 设为智能、里面放 Claude（按顺序）和 GPT（按顺序）两个组时，比较的是 Claude 组的第一个和 GPT 组的第一个，不会把两组的账号混在一起排。
- **服务商自己的路由也一样。**一个模型的服务商把账号或 Key 设为按顺序、轮流、用量少的优先、重置前用完或按权重时，在任何路由组里都保持这个路由：组拿它会先用的那个账号或 Key 来比，排到它时按它自己的顺序整体尝试。保持默认“智能”的服务商，它的账号和组里其他账号放在一起排，额度最先重置的排第一，不管属于哪个服务商。
- **故障转移照常。**子组里的模型全部失败时，由外层组的下一个成员接手，和其他成员一样。
- 同一个模型出现两次（单独一次，子组里一次）时只问一次，按它第一次出现的位置。

Coder 的规则把一个简单问题交给路由组 Fast，Fast 自己的规则又把 Kimi 排在组内第一。路由记录会写明每一层的规则和意图判断模型分别做了什么决定。

路由 标签页实时显示网关的决定：每个请求由谁回答、为什么。在终端里也能管理路由组：

终端

```
magpie groups                        # 先列你建的，再列 magpie 自动发现的
magpie group add "Opus anywhere" models=claude/claude-opus-5-5,copilot/claude-opus-5.5 routing=order stays=session
magpie group set opus-anywhere models+=openrouter/anthropic/claude-opus-5.5
magpie group set opus-anywhere routing=weight weight=claude/claude-opus-5-5=3  # 每四个请求有三个给它
magpie group rule add opus-anywhere use=openrouter/anthropic/claude-opus-5.5 tokens=150k  # 长对话优先发给它
magpie group rule add opus-anywhere use=copilot/claude-opus-5.5 intent="一个简单问题" classifier=groq/llama-3.1-8b-instant
magpie group rule add opus-anywhere use=deepseek/deepseek-v4-flash compact  # /compact 的总结交给便宜的模型
magpie group rule add opus-anywhere use=kimi/kimi-k2.6 folders=~/oss,"~/My Project"  # 这些项目里的对话先发给它
magpie group rule add opus-anywhere pause=copilot/claude-opus-5.5 time=14:00-18:00 days=mon-fri  # 这段时间不用它
magpie group rule add opus-anywhere pause=claude/claude-opus-5-5 except-folders=~/big-task  # 只留给 ~/big-task 里的任务：其他文件夹不用它
magpie group set coder models+=group/opus-anywhere  # 路由组里放路由组
magpie group rule opus-anywhere      # 查看规则；rule rm|mv <n>，rule classifier <组> <模型> 换判断模型
magpie group copy opus-anywhere "Opus test"  # 复制一份：模型、路由方式和规则都一样，可单独修改
magpie group rm opus-anywhere        # 自动发现的组会被隐藏；magpie group restore <id> 恢复
magpie claude group/opus-anywhere    # 使用它
```

## 用量与方案

**用量。**用量 标签页按 Agent 和模型统计每次经过网关的调用的 token、缓存命中和费用，可选 今天、7 天、30 天 或 全部；最上面是各订阅已用的额度和重置时间。Agent 直接发给自己厂商的请求不经过 magpie，不会计入。

经过网关的每次调用的余额、token、缓存命中和费用。

**上下文。**用量 里的 上下文 标签页显示每个 Agent 的提示词里装了什么，在请求经过网关时读出：系统提示词、工具定义（一个 MCP 服务器的工具算作一项）、指令文件与 skills、工具读入的文件、工具的其他输出和对话，各占模型上下文窗口的多少。每个 Agent 有一个百分制得分——缓存读到了多少提示词、起步多轻、上下文涨得多快、失败多不多——以及「起步轻」「MCP 偏重」之类的标签，说明得分从何而来。打开一个会话，可以一格一格地看它最近一次请求的窗口；在 路由 页点选任意请求也能看到。点一个部分、一格或一项，可以看到 magpie 发出去的原文，开着遮盖时是遮盖后的。原文只为最近 10 次请求留在内存里，magpie 退出就没了；存下来的只有名称，不保存提示词的文字，也不会发往任何地方。

**方案。**在 Agent 标签页底部点 ＋ 保存当前，把所有 Agent 的设置存成一个方案；之后点这个方案就能一键全部切回。正在使用的方案带 ✓，托盘面板的 方案 按钮也显示它的名字；之后手动改过设置，✓ 就会消失。

## 命令行

`magpie tui` 是终端里的完整界面，上面每一步也都有对应命令。`magpie help` 列出全部命令。

| 命令 | 作用 |
| --- | --- |
| `magpie ls` | 列出找到的每个 Agent 及其设置 |
| `magpie presets` | magpie 内置的厂商预设 |
| `magpie provider add deepseek sk-…` | 用密钥添加一个预设 |
| `magpie accounts add codex` | 再登录一个 Claude 或 ChatGPT 订阅 |
| `magpie accounts discovery off` | 不读取智能体的登录信息（Claude Code 和 Codex 的文件、钥匙串）；`on` 重新读取 |
| `magpie providers` | 你的供应商：地址、密钥、模型、谁在用 |
| `magpie models` | Agent 能选的所有模型，写作 `provider/model` |
| `magpie claude codex/gpt-5.5` | 设置 Agent 的模型 |
| `magpie codex effort high` | 设置其他字段 |
| `magpie codex default` | 恢复 Agent 自己的默认值，移除 magpie 的接入 |
| `magpie save work` · `use work` | 保存、应用方案 |
| `magpie usage 7d` | 按 Agent 和模型统计 token 与费用 |
| `magpie tray` | 只启动菜单栏图标 |

## 常见问题

### 需要自己 export OPENAI_BASE_URL 或 ANTHROPIC_BASE_URL 吗？

不需要。对 magpie 列出的 Agent，它会把网关地址和令牌直接写进 Agent 自己的配置文件。这些环境变量只用于 magpie 不管理的、带 base URL 设置的其他工具：网关 标签页的 接入 部分有一键复制和示例代码。

### magpie 必须一直开着吗？

通过 magpie 使用的模型需要：网关随应用一起运行。关掉窗口后它仍留在菜单栏或托盘里；`magpie tray` 只启动图标（可以放进登录项），`magpie serve` 只运行网关，`magpie daemon install` 把它装成服务（Linux 上是 systemd，Mac 上是 launchd），登录或开机就启动，不需要窗口；`magpie daemon install --web` 让服务同时提供浏览器页面，`magpie daemon status` 会打印页面的链接。Agent 用它自己的模型和自己的登录时，不经过 magpie。

### 怎么把 Agent 恢复原样？

在选择列表里选 Agent 自带的模型，或运行 `magpie <agent> default`。magpie 会删掉它写入的内容，并恢复被它替换掉的值，比如你原来的 `ANTHROPIC_BASE_URL`。

### 换了模型，Agent 还在用旧的？

已在运行的会话保持启动时的模型。开一个新会话；如果是 Codex，也请重启 Codex 应用。

### 手动改 Agent 的配置会冲突吗？

不会。magpie 每次都重新读取文件，只动它设置的那几个键，你的其他设置和注释都会保留。用 导入… 带进来的供应商是一份拷贝：之后在 Agent 里的改动不会再同步过来。

### 没有梯子，安装或更新连不上 GitHub 怎么办？

给安装脚本和 `magpie update` 加代理：`curl -fsSL https://usemagpie.ai/install.sh | sh -s -- --proxy http://127.0.0.1:7890`，或 `magpie update --proxy socks5://127.0.0.1:1080`（支持 http、https、socks5、socks5h；环境变量 `HTTPS_PROXY`、`ALL_PROXY` 同样生效）。`--mirror <前缀>` 从你指定的 GitHub 下载镜像取发布文件，即 `<前缀>https://github.com/…`；`magpie update mirror <前缀>` 让之后每次更新（包括应用自己的更新）都用它，`magpie update mirror off` 取消。不指定就不用任何镜像；文件的 SHA-256 始终来自 usemagpie.ai，而不是镜像，镜像改过的文件会被拒绝安装。应用自己的更新走 设置 → 代理。

### magpie 会发送我的哪些信息？

你的提示词、回复、密钥和账号只发给你用的供应商，中间没有 magpie 自己的服务器。正式发布的 magpie 每天告诉我们一次它在用，好让我们知道有多少人在用、该先照顾哪些：本机随机生成的 ID、magpie 版本和系统，以及用了哪些 agent、供应商和模型，只用 magpie 自己的 ID（`claude`、`deepseek`、`deepseek/deepseek-v4`）和各自的数量。你自己添加的供应商及其上的模型只记作 `custom`。添加供应商页里排在最前的合作伙伴，每天被展示、打开和添加的次数也一并发送，只有次数。不发送名称、Base URL、账号、密钥、提示词和用量。设置 → 隐私 → 分享我用的 agent、provider 和模型 可以去掉 agent、供应商、模型和合作伙伴次数这部分；计入用户数、`DO_NOT_TRACK=1` 或 `MAGPIE_NO_STATS=1` 全部关闭。从源码构建的版本从不发送。合作伙伴的官网和「获取 Key」链接经 `usemagpie.ai/go/…` 跳转，跳转前记一次点击（哪个合作伙伴、哪个链接、哪个国家），usemagpie.ai 也会统计合作伙伴列表被拉取的次数。这部分是服务器本身看到的，和任何网站统计访问一样，不受上面的设置影响；不记录 ID、IP 和账号。插件、导入链接和库里的图标经 `usemagpie.ai/api/icon` 获取，图标所在的服务器只看到 Cloudflare 的地址，看不到你的 IP；这台服务器只转发图片，不计数也不记录。[隐私页](https://usemagpie.ai/docs/zh/privacy)列出了 magpie 自己发出的所有内容，附每日计数的示例、它在本机留下的文件和每个开关。

### Agent 报 502 或连不上，magpie 的路由标签页里却什么都没有？

代理软件（Surge、Clash、mihomo 等，开了系统代理、TUN 或增强模式）把 Agent 发往 `http://127.0.0.1:3425` 的请求接走、转去了别处，请求根本没到 magpie。只在跳过列表（`skip-proxy`、「绕过」）里写 127.0.0.1 不一定够：有些 Agent（比如 Codex）照样会走代理。在代理软件里加两条本地地址直连的规则，放在其他规则前面：

Surge

```
IP-CIDR,127.0.0.0/8,DIRECT,no-resolve
IP-CIDR6,::1/128,DIRECT,no-resolve
```

Clash / mihomo 的配置里把这两行写在 `rules:` 下，每行前面加 `-`。改完让 Agent 重新发一次请求即可。

遇到问题，或者有值得分享的配置？来 [Discord](https://discord.gg/vGSnD3ZKQF) 聊。想给自己的用户一键添加供应商的厂商，请看 [Add to magpie](https://usemagpie.ai/docs/zh/import)。
