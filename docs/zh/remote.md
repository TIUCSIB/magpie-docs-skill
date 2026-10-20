<!-- 来源: https://usemagpie.ai/docs/zh/remote | 自动同步, 勿手改 -->

# 远程 magpie

一个 magpie 可以服务多台电脑。在保存供应商的那台电脑上（你的台式机、一台服务器、[Docker 里的 NAS](https://usemagpie.ai/docs/zh/docker)）登录、配置一次供应商和路由组，然后在其他每台电脑上把这个 magpie 添加为一个供应商：**远程 magpie**（Remote magpie）。

|  | 共享的 magpie | 其他电脑上的 magpie |
| --- | --- | --- |
| 供应商、订阅、密钥 | 保存并登录在这里 | 通过远程 magpie 使用 |
| 路由组 | 在这里创建 | 以 `office/group/…` 选用 |
| Agent | 它自己的 | 仍由本机的 magpie 配置 |
| 用量与额度 | 在这里统计和读取 | 在这里显示，带上远程的名字 |

你面前的电脑仍然运行 magpie：它配置本机的 Agent、为它们选模型、保存它们的会话。只有模型来自另一台。

## 1. 共享主 magpie

1. **打开共享**在保存供应商的电脑上：设置 → 局域网共享 → 开启。magpie 随即在局域网上监听，并生成一个名为 Magpie 的网关密钥。开关下方的 地址 一行显示其他电脑访问它的地址，例如 `http://192.168.1.20:3425`。
2. **给每台电脑一个密钥**网关 → 网关密钥，或 `magpie gateway-key add "Laptop"`，它会打印 `sk-magpie-key-…`。每个密钥可以有自己的每日、每周或每月上限和可用模型，它的调用按它的名字统计。

共享关闭时，桌面版 magpie 只在本机监听，其他电脑访问不到。Docker 里的 magpie 则通过发布的端口访问，不论是否共享，都会向容器外的每个调用方要网关密钥；见 [Docker](https://usemagpie.ai/docs/zh/docker#share)。

## 2. 在其他电脑上添加

需要第 1 步里的地址和一个密钥。以下任一方式都可以：

- **应用：**在 供应商 页按 ＋ 添加供应商，在最后的 另一台电脑上的 magpie 下选 Remote magpie，填入地址和密钥。
- **TUI**（`magpie tui`）：在 Providers 页按 `a`，选 Remote magpie，输入地址和密钥。在它那一行，`w` 修改地址，`m` 重新获取列表。
- **CLI：**

Shell

```
magpie provider add remote-magpie sk-magpie-key-… url=http://192.168.1.20:3425 id=office
magpie models            # office/… 是共享 magpie 的模型
magpie provider refresh office   # 重新获取列表
```

`id=` 是这个供应商在本机的名字，也是它的模型 id 的开头（`office/…`）。地址可以写成 `192.168.1.20:3425`（默认 `http://`），后面带 `/v1`，或者写根地址：magpie 都会把各个 API 接到上面。每台共享出来的电脑添加一个远程 magpie，用不同的 id。

## 能用到什么

- **它的模型**，和它自己的 Agent 看到的一样：`office/relay-a/claude-sonnet-5`，标签是 `Claude Sonnet 5 · Relay A · office`。id 不变，名字只出现在标签里。在本机像其他模型一样为 Agent 选用。
- **它的路由组**，以 `office/group/…` 出现。路由在共享的 magpie 上用它的账号决定。
- **所有 API。**请求按 Agent 使用的 API 原样转发（Anthropic Messages 和 token 计数、Responses、Chat Completions）。共享 magpie 的供应商只用另一种 API 提供的模型，只转换一次，不会在两台电脑上各转一次。Responses 走 HTTP（包括 SSE），不走 WebSocket。
- **图像和视频。**它的图像和视频模型会被自动识别，经由它的图像生成、编辑和视频 API 提供。
- **System One。**它的决策模型（Jev、Clef，以及你自己命名的模型）接到它的 `/v1/systemone`，作为决策模型而不是对话模型出现。刷新供应商列表可以发现新的。只写 `office` 时使用列表里的第一个决策模型。
- **Embeddings、rerank 和语音转文字**发往它对应的 API。它们在 Agent 列表里保持远程上的样子；出现在列表里并不代表能用来对话。
- **价格。**每个模型在本机按共享 magpie 的计价（那边手动设的价格，否则是供应商的标价），两台电脑算出来一样。在本机设的价格优先。

## 额度与用量

用量页、菜单栏和 `magpie quota` 会显示共享 magpie 的订阅卡片，带上它的名字（`Codex · office`，id `office/codex`），内容是那边最近一次读取的结果：只有保存登录的电脑去问厂商。在本机刷新卡片会让那边再读一次，最多每 30 秒一次。Codex 重置或 WorkBuddy 签到要在那台电脑上，用它自己的应用、TUI 或 CLI 来做。那边限了额度、模型或账号的密钥看不到它的任何卡片：本机只显示这把密钥自己的卡片和它的限额。

共享的 magpie 把本机的请求记在本机所用网关密钥的名字下，并记下应答的账号。

## 出问题时

| 看到的提示 | 怎么做 |
| --- | --- |
| “magpie isn’t shared on the local network” 或 “remote magpie isn’t shared” | 在那台电脑上打开 局域网共享 |
| “remote magpie didn’t take this key”（401） | 用它的一个已启用的网关密钥：那边的 网关 → 网关密钥 |
| 某个模型 403 | 这个密钥可能只能用部分模型：在那台电脑上用 `magpie gateway-key models <id>` 查看或修改。只写 `office` 会请求 System One 的第一个决策模型，不管密钥允许什么；请用完整的 `office/provider/model` id |
| “couldn’t reach the remote magpie” | 检查地址、那边的 magpie 是否在运行并打开了共享、防火墙是否放行该端口 |
| 没有 System One 模型，或 “doesn’t share its quotas” | 更新那台电脑上的 magpie，再在本机刷新列表 |

**不在家时**，通过 Tailscale 或 WireGuard 等 VPN、用它在 VPN 里的地址访问共享的 magpie。不要把它的端口开放到互联网。

遇到问题，或者有值得分享的配置？来 [Discord](https://discord.gg/vGSnD3ZKQF) 聊。细节见[参考文档](https://github.com/yetone/magpie/blob/main/docs/reference.md)（英文）。
