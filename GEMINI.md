# Magpie 文档(Gemini CLI 入口)

本目录是 Magpie(usemagpie.ai)官方中文文档的离线 Markdown 镜像。

回答任何关于 Magpie 的问题——尤其编写/调试插件、配置路由、接入 Agent——**先读本地文档,不要凭记忆猜 API**:

1. 打开 `docs/zh/index.md` 定位页面;
2. 插件开发读 `docs/zh/plugins.md`(钩子 `config`/`auth`/`loader`/`provider.models`/`chat.headers`、Acme 完整示例、测试与发布);
3. 其余主题按 index 指引读对应文件;
4. 写代码优先照抄文档示例结构。

关键背景:Magpie 是本地模型网关(`127.0.0.1:3425`),OpenAI/Anthropic/Gemini 三 API 互转;插件基于 OpenCode 供应商插件兼容层,运行在 Bun 宿主,模块导出 async 函数返回钩子;增删改插件会重启宿主。

文档更新:`python scripts/sync.py` 重新抓取生成。
