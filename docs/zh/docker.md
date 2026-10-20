<!-- 来源: https://usemagpie.ai/docs/zh/docker | 自动同步, 勿手改 -->

# 在 Docker 里运行 magpie

在没有桌面的服务器或 NAS 上运行 magpie：它的网关为其他电脑上的 Agent 提供模型，供应商的添加和订阅登录都在浏览器页面里完成。

| **镜像** | `ghcr.io/yetone/magpie`，支持 `linux/amd64` 和 `linux/arm64` |
| --- | --- |
| **标签** | `latest`（最新正式版）、`0.1.1150`（某个版本）、`0.1`、`edge`（`main` 上的每次改动） |
| **端口** | `3425` 是 Agent 调用的网关；`3430` 是容器运行 `magpie web` 时的 Web 界面 |
| **数据卷** | `/config`：供应商、密钥、登录、插件和用量 |
| **用户** | nonroot（uid 65532） |

镜像里是 magpie 的纯终端版本，基于 distroless，并带了 bash 和 busybox，方便在容器里开终端。不指定命令时运行 `magpie serve`（只有网关）。容器里找不到需要配置的 Agent，所以这里的 magpie 是一个网关：用它的 Agent 运行在别的机器上。

## 运行

带 Web 界面运行，给页面一个重启后不变的 key，两个端口都只发布在宿主机的回环地址上：

Shell

```
docker run -d --name magpie --restart unless-stopped \
  -p 127.0.0.1:3425:3425 -p 127.0.0.1:3430:3430 \
  -e MAGPIE_WEB_KEY=$(openssl rand -hex 16) \
  -v magpie-config:/config \
  ghcr.io/yetone/magpie:latest web --addr 0.0.0.0:3430 --no-open

docker logs magpie
```

日志里给出带 key 的页面地址：

输出

```
● magpie web on http://127.0.0.1:3430/?k=0f3c9a1e…
  on the network http://172.17.0.2:3430/?k=0f3c9a1e…
  these are the container's own addresses: other machines use the host's, and MAGPIE_PUBLIC_URL=http://<host>:<port> puts it here
! anyone with the link can change magpie and see its keys, and the network carries it unencrypted
  the link carries MAGPIE_WEB_KEY · gateway http://127.0.0.1:3425 · Ctrl-C to stop
```

**容器外的 Agent 需要网关密钥。**在容器里任何 key 都行。来自宿主机或其他机器的请求只有带上启用的网关密钥才会应答，不带的返回 401：按[网关密钥](#share)里的步骤生成一个。`-p` 里的 `127.0.0.1:` 让端口只在宿主机上；去掉它，或写成宿主机的局域网或 VPN 地址，其他机器才能访问。

不加 `web --addr 0.0.0.0:3430 --no-open` 时容器只跑网关，需要在容器终端里配置（`docker exec -it magpie magpie provider add …`）。也可以把一个目录绑定挂载到 `/config` 来代替命名卷，前提是 uid 65532 能写它：`sudo chown -R 65532:65532 /volume1/docker/magpie/config`。

## Web 界面

打开日志里的链接。链接里的 key 会换成一个 cookie，并从地址栏里去掉；不带 key 打开会被拒绝（401）。设置了 `MAGPIE_WEB_KEY`（16 个以上的字母、数字或 `- . _ ~`；`openssl rand -hex 16` 可以生成一个）时，重启后 key 不变，浏览器保持登录 400 天。不设置时每次启动都会生成新 key，cookie 只在本次浏览器会话里有效。

这个页面处于**网关模式**：只有 供应商、网关、路由、用量、插件和 设置，没有 Agent、会话和资源库，因为容器里没有 Agent。设置 → 常规 → 网关模式 可以关掉它。

NAS 或通过 SSH 访问的服务器上，用隧道打开页面，不要发布 3430：`ssh -L 3430:127.0.0.1:3430 you@nas`，然后在自己电脑上打开日志里的链接。

**拿到链接的人都能修改 magpie、看到它的密钥。**让 3430 只在回环地址或 VPN 上。要跨网络访问，就用 HTTPS：用 `MAGPIE_TLS_CERT` 和 `MAGPIE_TLS_KEY` 给 magpie 一张证书，或者放在带 TLS 的反向代理（如 Caddy）后面。

## 登录订阅

在 供应商 里添加 API key，和桌面版一样。订阅登录（ChatGPT、Claude……）会在你的浏览器里打开厂商页面，完成后厂商把浏览器跳回 `localhost`，ChatGPT 是 `http://localhost:1455/auth/callback?code=…`。那是你自己的电脑，不是容器，所以页面打不开。把地址栏里的完整地址复制下来，粘贴到登录的 回调 URL 一栏。

在终端里也可以：

Shell

```
docker exec -it magpie magpie accounts add codex
```

打开它打印的链接并登录，再把浏览器最后停在的地址粘贴回去。Web 界面也能从文件导入登录。

Claude 订阅的登录和请求都经过 Claude Code，而镜像里没有它。先让 magpie 下载 Anthropic 官方的构建：它会说明版本、下载来源和保存位置，问过你再下载，并用 Anthropic 清单里的 SHA-256 校验。它保存在 `/config/cache` 里；再运行一次可以更新到新版本。缺少 Claude Code 时，`magpie accounts add claude` 也会提出下载。

Shell

```
docker exec -it magpie magpie claude-code install
```

Grok（SuperGrok）订阅通过 xAI 的 Grok Build CLI 登录，镜像里同样没有它。在浏览器界面里登录，或者用 `magpie plugin login grok` 登录时，magpie 会先按 xAI 安装脚本的方式安装它：从 `x.ai/cli` 下载 stable 版本，放在 `/config/home/.grok`。要用你自己放进数据卷的 Grok Build，把 `GROK_BIN_DIR` 设为它所在的文件夹。

## 保存了什么

magpie 写的所有东西都在 `/config` 下，所以重启、或者在同一个数据卷上新建容器，供应商、密钥、登录和插件都还在。

| 路径 | 内容 |
| --- | --- |
| `/config/magpie` | magpie 自己的文件：`settings.json`、供应商、网关密钥、路由组 |
| `/config/home` | 容器的 `HOME`：登录保存在对应 Agent 保存的位置（`~/.codex`、`~/.claude`……） |
| `/config/cache` | 模型目录、插件运行用的 Bun（第一次用插件时下载），以及 `magpie claude-code install` 下载的 Claude Code |
| `/config/data`、`/config/state` | magpie 保存的其他内容 |

旧镜像创建的数据卷照样能用：magpie 启动时会补上缺的目录。只有用旧镜像做的登录（当时存在数据卷之外）需要重新登录。

## 环境变量

| 变量 | 作用 |
| --- | --- |
| `MAGPIE_ADDR` | 网关监听的地址。镜像里设为 `0.0.0.0:3425`，发布的端口才能访问到它。 |
| `MAGPIE_PUBLIC_URL` | 其他机器访问网关用的地址，例如 `http://192.168.1.20:3425`（宿主机或 NAS 的地址，加发布的端口），或反向代理的 base URL。容器里 magpie 只看得到 Docker 自己的 `172.17.x` 地址；设置后，它显示和打印的就是该用的地址。 |
| `MAGPIE_WEB_KEY` | Web 界面的 key，重启后不变（16 个字符以上） |
| `MAGPIE_TLS_CERT`、`MAGPIE_TLS_KEY` | 挂载进容器的 PEM 证书（后面跟着证书链）和私钥：其他机器只能用 `https://` 访问网关和 Web 界面，它们发来的明文 HTTP 返回 400。文件变了会重新读取，续期不用重启。只给一个，或文件读不出来，magpie 不会启动。`MAGPIE_PUBLIC_URL` 也写成 `https://`。 |
| `MAGPIE_ALLOW_IPS` | 其他机器只能从这些地址访问网关和 Web 界面，写 IP 或 CIDR 网段：`203.0.113.7,10.0.0.0/8,2001:db8::/32`。其他地址即使带着网关密钥也会得到 403。不设置则所有地址都可访问，各自仍需密钥。见[允许的地址](#allow)。 |
| `HOME`、`XDG_CONFIG_HOME`、`XDG_CACHE_HOME`、`XDG_DATA_HOME`、`XDG_STATE_HOME` | 镜像已设为上面 `/config` 下的目录，不要改 |

## 网关密钥与其他机器

1. **给每个客户端生成一个密钥**网关 → 网关密钥，或在终端里 `docker exec magpie magpie gateway-key add "Laptop"`，它会打印新的 `sk-magpie-key-…`。容器外的每个请求（包括宿主机自己的）都必须带一个启用的网关密钥，不带的返回 401。每个密钥可以有自己的每日、每周、每月、每 N 天或每 N 小时的上限和可用模型（`magpie gateway-key limit`、`magpie gateway-key models`）。
2. **发布端口**用 `-p 3425:3425`（或绑定到 NAS 的局域网或 VPN 地址，`-p 192.168.1.20:3425:3425`）并加上 `-e MAGPIE_PUBLIC_URL=http://192.168.1.20:3425` 重新创建容器。

在其他电脑上，把 Agent 指向这个网关，用其中一个密钥作为 API key：OpenAI 客户端用 `http://192.168.1.20:3425/v1`，Anthropic 或 Gemini 客户端用 `http://192.168.1.20:3425`。模型 id 是 `provider/model` 或路由组的名字，`GET /v1/models` 会列出它们。如果那台电脑自己也运行 magpie，就把容器添加为[远程 magpie](https://usemagpie.ai/docs/zh/remote)，由 magpie 替你配置 Agent。

容器里不需要打开 设置 → 局域网共享：打开它会另外生成一个名为 Magpie 的网关密钥，而不论开关如何，网关都会向容器外的请求要密钥。

**从旧镜像升级。**容器外发送 `magpie` 或其他非启用网关密钥的 Agent，现在会收到 401（“the API key sent is not an enabled magpie gateway key”）。按上面的步骤给它生成一个密钥，填进 Agent 的设置。已经发送网关密钥的 Agent，以及用网关密钥添加的远程 magpie，照常工作。

**允许的地址。**在公网主机上，用 `-e MAGPIE_ALLOW_IPS=203.0.113.7,10.0.0.0/8` 写上你的客户端所在的地址。来自其他地址的请求在看密钥之前就被拒绝（403），所以泄露的密钥从别处也用不了；拒绝信息和容器日志都会写出请求来自的地址。magpie 判断的是连接本身的地址，从不采信 `X-Forwarded-For` 头；写错的条目不会放行任何地址，而不是放行所有地址。Docker 默认的 bridge 网络会把客户端自己的地址传进容器，但宿主机自己发出的请求来自 bridge 的网关（`172.17.0.1`），Docker Desktop 和 rootless Docker 则把所有客户端显示成它们自己的一个地址：把它加上，或看 403 里写的是哪个。在反向代理或隧道后面时，所有请求都来自代理的地址，请在代理那里限制谁能访问。桌面版里同一个列表在 设置 → 网络与共享 → 允许的地址。

**跨互联网访问时，优先用 VPN**（如 Tailscale 或 WireGuard），不要直接开放 3425。容器前面的反向代理或隧道也算网络：它的客户端和其他机器一样需要网关密钥。

## 在 NAS 上用 Docker Compose

compose.yaml

```
services:
  magpie:
    image: ghcr.io/yetone/magpie:latest
    restart: unless-stopped
    ports:
      # 127.0.0.1：只在宿主机上；容器外的每个调用方都需要网关密钥
      - "127.0.0.1:3425:3425"
      - "127.0.0.1:3430:3430"
    environment:
      MAGPIE_PUBLIC_URL: http://<nas-address>:3425
      MAGPIE_WEB_KEY: <random-key>
    volumes:
      - ./config:/config
    command: [web, --addr, 0.0.0.0:3430, --no-open]
```

然后：`sudo chown -R 65532:65532 ./config`，`docker compose up -d`，通过 SSH 隧道打开 `http://127.0.0.1:3430/?k=<random-key>`，添加供应商，给每台机器生成一个网关密钥。要让其他机器访问网关，把它那一行改成 `"3425:3425"`（或 NAS 的局域网、VPN 地址），重新 `docker compose up -d`。

## 健康检查、终端与更新

- **健康检查。**镜像带 `HEALTHCHECK`：网关能应答时 `magpie healthcheck` 返回 0，`serve` 和 `web` 都一样，所以 `docker ps` 会显示 healthy，Compose 可以用 `depends_on: condition: service_healthy` 等它。
- **终端。**`docker exec -it magpie bash` 或 NAS 面板里的终端会打开一个 shell，`magpie` 在 PATH 里：`magpie providers`、`magpie models`、`magpie usage`、`magpie quota` 以及其他 [CLI 命令](https://github.com/yetone/magpie/blob/main/docs/reference.md)。
- **更新。**拉取新镜像，在同一个数据卷上重新创建容器：`docker pull ghcr.io/yetone/magpie:latest`，然后 `docker rm -f magpie` 再执行同样的 `docker run`；或 `docker compose pull && docker compose up -d`。
- **自己构建。**在[仓库](https://github.com/yetone/magpie)的检出目录里 `docker build -t magpie .` 得到同样的镜像。

遇到问题，或者有值得分享的配置？来 [Discord](https://discord.gg/vGSnD3ZKQF) 聊。细节见[参考文档](https://github.com/yetone/magpie/blob/main/docs/reference.md#docker)（英文）。
