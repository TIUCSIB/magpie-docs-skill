# Magpie 文档索引 (zh)

> 本页由 sync.py 自动生成。写插件/配置前, 先按需打开下面对应的 `docs/zh/xxx.md`。

- **快速上手** — [docs/zh/start.md](docs/zh/start.md)
  - magpie 是给你所有 Agent 统一选模型的地方。先把你有的供应商加进来，再给每个 Agent 选一个模型；magpie 会把它写进那个 Agent 自己的配置文件。
- **意图路由** — [docs/zh/intent.md](docs/zh/intent.md)
  - 按用户想做什么来选模型：写测试交给强模型，随口一问交给又快又便宜的模型。你用几个词描述每一类请求，每一轮开始时，由你指定的一个小模型判断这条消息属于哪一类。
- **插件开发** — [docs/zh/plugins.md](docs/zh/plugins.md)
  - 插件负责登录某个服务、替它发请求。magpie 把插件变成一个供应商，所有 agent 都能用，多账号、故障切换、用量这些也都有。magpie 运行的是 [OpenCode 的供应商插件](https://opencode.ai/docs/plugins/)，为 OpenCode 写的插件不用改就能在这里用；注册了供应
- **远程 Magpie** — [docs/zh/remote.md](docs/zh/remote.md)
  - 一个 magpie 可以服务多台电脑。在保存供应商的那台电脑上（你的台式机、一台服务器、[Docker 里的 NAS](https://usemagpie.ai/docs/zh/docker)）登录、配置一次供应商和路由组，然后在其他每台电脑上把这个 magpie 添加为一个供应商：**远程 magpie**（Remo
- **Docker 部署** — [docs/zh/docker.md](docs/zh/docker.md)
  - 在没有桌面的服务器或 NAS 上运行 magpie：它的网关为其他电脑上的 Agent 提供模型，供应商的添加和订阅登录都在浏览器页面里完成。
- **隐私** — [docs/zh/privacy.md](docs/zh/privacy.md)
  - 你的提示词、回复、密钥和账号只发给你用的供应商，中间没有 magpie 自己的服务器。这一页列出 magpie 在这些请求之外自己发出的所有内容，以及关掉它们的每个开关。内容按代码写成，每一节都附了代码链接。
- **Add to magpie** — [docs/zh/import.md](docs/zh/import.md)
  - 给用户一个链接，你的模型就会出现在他们用的每个 Agent 里：Claude Code、Codex、OpenCode、Gemini CLI、Pi、Crush。不用改配置文件，不用设环境变量，也不用手动复制 base URL。
- **接入应用** — [docs/zh/integrate.md](docs/zh/integrate.md)
  - 写给 AI 应用、Agent 或客户端的开发者：想让自己的应用和 magpie 配合好，有三个层次，从 magpie 这边什么都不用改，到在 Agents 页面拥有自己的一行。
