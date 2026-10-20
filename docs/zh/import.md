<!-- 来源: https://usemagpie.ai/docs/zh/import | 自动同步, 勿手改 -->

# Add to magpie

给用户一个链接，你的模型就会出现在他们用的每个 Agent 里：Claude Code、Codex、OpenCode、Gemini CLI、Pi、Crush。不用改配置文件，不用设环境变量，也不用手动复制 base URL。

用户看到的界面。在点「添加」之前，什么都不会保存。

## 快速开始

1. **生成链接**用 URL 参数描述你的服务：名称、你支持的每种 API 的 base URL，还可以带上用户的密钥和要提供的模型。
2. **放到按钮后面**放在控制台里、刚生成的密钥旁边：*Add to magpie*。
3. **用户确认**magpie 打开后，会清楚列出提示词和密钥将发往哪里，用户同意后才添加这个供应商。之后每个 Agent 都能直接用。

链接

```
https://usemagpie.ai/import#name=Acme%20Relay&chat=https://api.acme.example/v1&anthropic=https://api.acme.example&key=sk-…&models=gpt-5.5,claude-sonnet-5
```

## 链接格式

magpie 会向系统注册 `magpie://` 协议。导入链接就是这个协议，加上 `import` 和一串查询参数：

magpie://import?name=Acme%20Relay&chat=https://api.acme.example/v1&key=sk-…

在网页上，请改用 `usemagpie.ai/import`，把同样的参数放在 `#` 后面：

https://usemagpie.ai/import#name=Acme%20Relay&chat=https://api.acme.example/v1&key=sk-…

### 为什么用 https 链接

普通链接能用的地方它都能用：GitHub README、聊天软件和邮件客户端常常会去掉或拦截自定义协议。它会打开 magpie；还没装 magpie 时，会引导下载。

### 为什么放在 # 后面

浏览器从不把 # 后面的部分发给服务器。密钥从你的页面直接到用户电脑上，不经过 usemagpie.ai，连日志里也不会出现。

每个值都要做 URL 编码，`URLSearchParams` 或 `urlencode` 的结果即可。空格写成 `%20` 或 `+` 都行。

## 参数

链接要么指定 magpie 的某个[预设](#presets)（预设已经知道该厂商的地址），要么从头描述一个供应商：一个名称，加至少一个 base URL。

| 参数 | 含义 |
| --- | --- |
| `name`或 preset | 供应商在 magpie 里的名称，最多 80 个字符。 |
| `chat` | OpenAI Chat Completions 的 base URL，以 `/v1` 结尾（magpie 会自动拼上 `/chat/completions`）。 |
| `responses` | OpenAI Responses 的 base URL，以 `/v1` 结尾。Codex 只支持这个 API；你不支持时，magpie 会替它转换。 |
| `anthropic` | Anthropic Messages 的 base URL：根地址，不带 `/v1`。 |
| `gemini` | Google Gemini API 的 base URL，以 `/v1beta` 结尾，和应用内编辑器、TUI 里填的是同一个。 |
| `key` | 用户的 API 密钥。不填的话，用户在对话框里自己粘贴。 |
| `models` | 提供给 Agent 的模型 id，用逗号分隔。不填时，magpie 会列出你的 `/v1/models` 返回的模型。 |
| `id` | Agent 在 `id/model` 里用的 id。默认取名称的小写加连字符形式（`Acme Relay` → `acme-relay`）。 |
| `catalog` | 一个 [models.dev](https://models.dev) 供应商 id，用它的元数据，比如转发 OpenAI 模型的服务可以填 `openai`。它提供：显示名、上下文长度（会写进支持该设置的 agent）、推理档位和是否支持图片；供应商自己的 `/models` 读不到时的模型列表；以及每 token 价格，用量页据此估算美元费用。可以用逗号填多个 id：它们的模型合在一起，同一个模型以排在前面的为准。 |
| `website` | 你的网站（https），显示在供应商页面上。 |
| `keys` | 用户创建密钥的页面（https）。链接里没有密钥时，对话框会链接到这里。 |
| `icon` | 你自己的图标（https）：PNG、JPEG、GIF、WebP、ICO 或 SVG，最大 1 MB。用户确认导入后，magpie 只下载一次，存在供应商旁边。不填时，magpie 显示 `catalog` 对应厂商的 logo，或一个默认图标。 |
| `preset`或 name | 预设 id；使用它的地址、目录和页面，可以用 `name` 改名。 |
| `region` | 预设有多个区域时，指定用哪个。 |

不用预设时，`chat`、`responses`、`anthropic`、`gemini` 至少要填一个；你支持几种 API 就填几个，每个 Agent 会用它原生支持的那一种。Base URL 必须是 **https**，只有指向 `localhost`、回环地址、内网地址和 `*.local` 时可以用 http，因为本地模型服务通常不配 TLS。地址里不能带查询参数、# 片段或账号密码。

### 预设

magpie 已经内置的厂商。`magpie presets` 会打印当前的列表。

`anthropic``openai``google``deepseek``xai``moonshot`Kimi`moonshot-cn``kimi-code``kimi-code-cn``zhipu`GLM · api · coding`zai`api · coding`minimax``minimax-cn``stepfun`plan · api`stepfun-cn`plan · api`xiaomi`MiMo`baidu-qianfan`千帆 · personal · team · api`tencent-cloud`plan · cn · intl · enterprise · enterprise-intl`huaweicloud`plan · api`volcengine`火山方舟 · coding · agent · api`qwen``qwen-cn``qwen-token-plan``bailian-token-plan``mistral``groq``bedrock``ollama-cloud``openrouter``opencode-go``clinepass``opencode-zen``kilo``commandcode``together``fireworks``siliconflow`cn · intl`nvidia``modelscope`魔搭`aihubmix``pipellm``302ai``cherryin``yylx`auto · global · cn`ollama``lmstudio`

有预设的厂商只需带上密钥：`magpie://import?preset=deepseek&key=sk-…`。想加入列表？[提个 issue](https://github.com/yetone/magpie/issues)。

## 链接生成器

填上你的服务信息，链接、按钮代码和 Markdown 会随输入实时生成。所有内容都只在这个页面里，不会发送出去。

预设

区域

名称

Id *可选*

OpenAI Chat base URL

Anthropic base URL

OpenAI Responses base URL *可选*

Gemini base URL *可选*

models.dev 目录 *可选*

API 密钥 *可选*

模型 *逗号分隔*

网站 *可选*

密钥页面 *可选*

图标 *可选，https*

网页链接

应用链接

HTML

Markdown

[![](https://usemagpie.ai/img/magpie-small.svg)试一下](#)会打开 magpie；你确认之前不会添加任何东西。

## 按钮

两个现成的徽章，一个用于浅色页面，一个用于深色页面。把它链接到你的导入链接即可；也可以自己画按钮，*Add to magpie* 字样和这只鸟都可以随意使用。

![Add to magpie](https://usemagpie.ai/img/add-to-magpie.svg)

![Add to magpie](https://usemagpie.ai/img/add-to-magpie-light.svg)

HTML

```
<a href="https://usemagpie.ai/import#preset=deepseek&key=sk-…">
  <img src="https://usemagpie.ai/img/add-to-magpie.svg" alt="Add to magpie" width="176" height="40">
</a>
```

Markdown

```
[![Add to magpie](https://usemagpie.ai/img/add-to-magpie.svg)](https://usemagpie.ai/import#preset=deepseek)
```

深色页面请用 `add-to-magpie-light.svg`。README 这类公开页面绝不能带密钥：去掉 `key`，让用户粘贴自己的。

## 在后端生成

按钮最适合放在展示新密钥的那个页面。在拿到密钥的地方生成链接：

JavaScript

```
const params = new URLSearchParams({
  name: "Acme Relay",
  chat: "https://api.acme.example/v1",
  anthropic: "https://api.acme.example",
  key: apiKey,
  models: ["gpt-5.5", "claude-sonnet-5"].join(","),
  icon: "https://acme.example/logo.svg",
});
const href = "https://usemagpie.ai/import#" + params;
```

Python

```
from urllib.parse import urlencode

href = "https://usemagpie.ai/import#" + urlencode({
    "name": "Acme Relay",
    "chat": "https://api.acme.example/v1",
    "anthropic": "https://api.acme.example",
    "key": api_key,
    "models": "gpt-5.5,claude-sonnet-5",
    "icon": "https://acme.example/logo.svg",
})
```

终端

```
magpie import 'magpie://import?preset=deepseek&key=sk-…'   # 会先询问；加 -y 跳过
```

## 安全

导入链接只是一个建议，决定权在用户手里。

- **总是要确认。**magpie 会显示名称、提示词和密钥将发往的每个地址，以及模型列表；用户点「添加」之前什么都不保存。用户还可以先改名或换掉密钥。
- **不会悄悄覆盖。**id 已被占用时，对话框会说明，按钮也会变成「替换」。
- **只接受 https。**除了本机和局域网，一律拒绝 http；`file:`、URL 里带账号密码以及其他协议直接拒绝。
- **只读一次。**在应用里，链接内容只交给窗口一次；刷新后对话框不会再出现。
- **图标是下载的，不是嵌入的。**`icon=` 地址由 magpie 下载，只在用户确认导入之后，只走 https，只存进它自己的图标目录，最大 1 MB，并校验类型。magpie 经 usemagpie.ai 的图标代理去取，所以你的服务器只看到 Cloudflare 的地址，看不到用户的 IP；请求从 Cloudflare 发出，碰不到用户本机和内网。回环或内网的域名在发出请求前就被拒绝。页面和对话框从不直接加载远程图片。
- **密钥不经过服务器。**网页链接把参数放在 # 片段里。密钥最终只存在 `~/.config/magpie/providers.json`，只有用户本人可读。

**链接里的密钥就是机密。**只在该用户本人能看到的页面上把密钥放进链接，最好是专门给 magpie 生成、可以随时吊销的密钥。绝不要把共享密钥放进公开链接。

## 平台支持

| 系统 | `magpie://` 如何注册 |
| --- | --- |
| macOS | 由应用自己注册，magpie.app 放进「应用程序」即可。 |
| Windows | magpie 首次运行时为当前用户注册。 |
| Linux | 通过桌面文件（`x-scheme-handler/magpie`）注册，安装器写一次，首次运行时再写一次。 |
| 终端 | `magpie import <链接>` 显示同样的摘要，添加前会询问。 |

导入链接需要 magpie 0.1.8 或更新版本。magpie 已在运行时，链接会交给那个实例，并把它的窗口调到前台。
