#!/usr/bin/env python3
"""
Magpie 文档同步器 —— 把 usemagpie.ai 的中文文档抓取并转换成 Markdown,
供任意 AI 编程 Agent (Claude Code / Codex / Gemini CLI / OpenCode / Cursor /
ZCode 等) 直接读取本地文件, 免去每次手动粘贴文档。

零第三方依赖, 只用 Python 标准库。

用法:
    python sync.py            # 联网抓取最新并重新生成 docs/*.md
    python sync.py --local    # 用 _raw/ 里已缓存的 HTML(离线调试转换器用)
    python sync.py --langs zh,en,ja   # 指定语言 (默认 zh)

生成:
    docs/<lang>/<slug>.md     每页正文
    docs/<lang>/index.md      总览(每页标题 + 首段摘要 + 链接)
"""
import html
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser

BASE = "https://usemagpie.ai"
# 文档章节 -> slug(与站点导航一致)
PAGES = [
    ("start",     "快速上手"),
    ("intent",    "意图路由"),
    ("plugins",   "插件开发"),
    ("remote",    "远程 Magpie"),
    ("docker",    "Docker 部署"),
    ("privacy",   "隐私"),
    ("import",    "Add to magpie"),
    ("integrate", "接入应用"),
]

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(HERE, "_raw")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}
SKIP_CONTENT = {"script", "style", "noscript", "svg", "iframe", "button"}
BLOCK_TAGS = {"p", "div", "section", "main", "article", "header", "footer",
              "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li",
              "table", "thead", "tbody", "tr", "pre", "blockquote",
              "figure", "figcaption", "dl", "dt", "dd", "nav"}


# ----------------------------- HTML -> 节点树 -----------------------------
class Node:
    __slots__ = ("kind", "tag", "attrs", "children", "text")

    def __init__(self, kind, tag=None, attrs=None, text=None):
        self.kind = kind            # "root" | "el" | "text"
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []          # for el/root
        self.text = text            # for text


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = Node("root")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node("el", tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node("el", tag, dict(attrs)))

    def handle_endtag(self, tag):
        # 弹到最近的同名开标签, 容错未闭合
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if data:
            self.stack[-1].children.append(Node("text", text=data))

    def handle_entityref(self, name):
        self.handle_data(html.unescape(f"&{name};"))

    def handle_charref(self, name):
        self.handle_data(html.unescape(f"&#{name};"))


def parse_html(markup):
    tb = TreeBuilder()
    tb.feed(markup)
    return tb.root


def find_article(root):
    """优先取 <article>, 退化到 <main class=...doc>。"""
    art = _find_first(root, "article")
    if art:
        return art
    return _find_first(root, "main") or root


def _find_first(node, tag):
    if isinstance(node, Node) and node.kind == "el" and node.tag == tag:
        return node
    for c in getattr(node, "children", []):
        r = _find_first(c, tag)
        if r:
            return r
    return None


# ----------------------------- 序列化辅助 -----------------------------
def absolutize(href):
    if not href:
        return href
    if href.startswith("#") or href.startswith("http") or href.startswith("mailto:"):
        return href
    if href.startswith("/"):
        return BASE + href
    return href


def text_content(node):
    """收集后代纯文本, 保留 pre 里的换行与缩进(不做空白归一)。"""
    if node.kind == "text":
        return node.text or ""
    if node.kind == "el" and node.tag in SKIP_CONTENT:
        return ""
    if node.kind == "el" and node.tag == "br":
        return "\n"
    return "".join(text_content(c) for c in node.children)


def collapse(s):
    return re.sub(r"[ \t]*\n[ \t]*", "\n", s)


def has_block_child(node):
    return any(c.kind == "el" and c.tag in BLOCK_TAGS for c in node.children)


def render_inline(node):
    """行内渲染: 返回单段文本(不含块级结构)。"""
    if node.kind == "text":
        return re.sub(r"\s+", " ", node.text or "")
    if node.kind != "el":
        return ""
    tag = node.tag
    if tag in SKIP_CONTENT:
        return ""
    if tag == "br":
        return " "
    if tag == "hr":
        return " "
    inner = "".join(render_inline(c) for c in node.children)
    if tag == "code":
        code = text_content(node).replace("\n", " ").strip(" ")
        if not code:
            return ""
        ticks = "`" * (max(len(m) for m in re.findall(r"`+", code)) + 1) if "`" in code else "`"
        pad = " " if code.startswith("`") or code.endswith("`") else ""
        return f"{ticks}{pad}{code}{pad}{ticks}"
    if tag in ("a",):
        href = absolutize(node.attrs.get("href", ""))
        label = inner.strip() or node.attrs.get("title", "") or href
        return f"[{label}]({href})" if href else label
    if tag in ("strong", "b"):
        return f"**{inner}**" if inner.strip() else inner
    if tag in ("em", "i"):
        return f"*{inner}*" if inner.strip() else inner
    if tag in ("del", "s"):
        return f"~~{inner}~~" if inner.strip() else inner
    if tag == "img":
        alt = node.attrs.get("alt", "")
        src = absolutize(node.attrs.get("src", ""))
        return f"![{alt}]({src})" if src else ""
    if tag == "sup":
        return f"^{inner}"
    if tag == "sub":
        return f"~{inner}"
    return inner  # span, font, small 等按纯文本


def render_heading(node, level):
    # 去掉锚点 <a> 的链接语法, 只留文字
    raw = text_content(node)
    t = collapse(raw).strip()
    t = re.sub(r"\s+", " ", t)
    return "#" * min(level, 6) + " " + t


def render_pre(node):
    code = text_content(node).replace("\r\n", "\n").replace("\r", "\n")
    code = code.strip("\n")
    # 去掉每行多余的前导空白对齐(保留相对缩进)
    lines = code.split("\n")
    lead = None
    for ln in lines:
        if ln.strip():
            m = re.match(r"^[ \t]*", ln)
            w = len(m.group(0))
            lead = w if lead is None else min(lead, w)
    if lead:
        lines = [ln[lead:] if len(ln) >= lead else ln for ln in lines]
    code = "\n".join(lines).rstrip()
    run = max((len(m) for m in re.findall(r"`+", code)), default=0)
    fence = "`" * max(3, run + 1)
    return f"{fence}\n{code}\n{fence}"


def render_table(node):
    rows = node.findall("tr") if hasattr(node, "findall") else _collect(node, "tr")
    if not rows:
        return ""
    md_rows = []
    for tr in rows:
        cells = [c for c in tr.children if c.kind == "el" and c.tag in ("td", "th")]
        vals = []
        for cell in cells:
            txt = "".join(render_inline(x) for x in cell.children)
            txt = collapse(txt).strip()
            txt = re.sub(r"\s+", " ", txt).replace("|", "\\|")
            vals.append(txt)
        md_rows.append(vals)
    if not md_rows:
        return ""
    width = max(len(r) for r in md_rows)
    for r in md_rows:
        while len(r) < width:
            r.append("")
    out = ["| " + " | ".join(md_rows[0]) + " |",
           "| " + " | ".join(["---"] * width) + " |"]
    for r in md_rows[1:]:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def _collect(node, tag):
    res = []
    for c in getattr(node, "children", []):
        if c.kind == "el":
            if c.tag == tag:
                res.append(c)
            else:
                res.extend(_collect(c, tag))
    return res


def render_children_blocks(node, indent=""):
    parts = []
    for c in node.children:
        r = render_block(c, indent)
        if r and r.strip():
            parts.append(r)
    return ("\n\n".join(p for p in parts)).strip("\n")


def render_block(node, indent=""):
    if node.kind == "text":
        t = re.sub(r"\s+", " ", node.text or "").strip()
        return (indent + t) if t else ""
    if node.kind != "el":
        return ""
    tag = node.tag
    if tag in SKIP_CONTENT:
        return ""
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        return indent + render_heading(node, int(tag[1]))
    if tag == "p":
        inline = "".join(render_inline(c) for c in node.children).strip()
        inline = re.sub(r" {2,}", " ", inline)
        return (indent + inline) if inline else ""
    if tag == "pre":
        return render_pre(node)
    if tag == "hr":
        return indent + "---"
    if tag == "blockquote":
        inner = render_children_blocks(node)
        if not inner:
            inner = "".join(render_inline(c) for c in node.children).strip()
        lines = inner.split("\n")
        return "\n".join(indent + "> " + ln for ln in lines)
    if tag in ("ul", "ol"):
        return render_list(node, tag, indent)
    if tag == "table":
        return indent + render_table(node)
    # div/section/main/article/header/footer/nav/dl 等容器:
    if has_block_child(node):
        return render_children_blocks(node, indent)
    inline = "".join(render_inline(c) for c in node.children).strip()
    inline = re.sub(r" {2,}", " ", inline)
    return (indent + inline) if inline else ""


def render_list(node, tag, indent):
    out = []
    idx = 1
    for li in node.children:
        if not (li.kind == "el" and li.tag == "li"):
            continue
        marker = f"{idx}." if tag == "ol" else "-"
        # 分离: 直接行内内容 与 嵌套块(子列表/段落/pre 等)
        inline_parts = []
        nested = []
        for c in li.children:
            if c.kind == "el" and c.tag in BLOCK_TAGS and c.tag in ("ul", "ol", "pre", "table", "blockquote", "p", "div"):
                nested.append(c)
            else:
                inline_parts.append(c)
        head = "".join(render_inline(x) for x in inline_parts).strip()
        head = re.sub(r" {2,}", " ", head)
        bullet = f"{indent}{marker} {head}" if head else f"{indent}{marker}"
        out.append(bullet)
        for n in nested:
            sub = render_block(n, indent + "  ")
            if sub.strip():
                out.append(sub)
        idx += 1
    return "\n".join(out)


def html_to_markdown(markup):
    root = parse_html(markup)
    art = find_article(root)
    kids = list(art.children)
    # 丢弃 <h1> 之前的块(站点面包屑在正文前)
    for i, c in enumerate(kids):
        if c.kind == "el" and c.tag == "h1":
            kids = kids[i:]
            break
    blocks = []
    for c in kids:
        b = render_block(c)
        if b and b.strip():
            blocks.append(b)
    doc = "\n\n".join(blocks)
    doc = re.sub(r"\n{3,}", "\n\n", doc).strip()
    return doc, art


# ----------------------------- 抓取 -----------------------------
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def get_html(slug, lang, use_local):
    path = os.path.join(RAW_DIR, f"{lang}-{slug}.html")
    if use_local and os.path.exists(path):
        return open(path, encoding="utf-8", errors="replace").read()
    url = f"{BASE}/docs/{lang}/{slug}"
    markup = fetch(url)
    os.makedirs(RAW_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(markup)
    return markup


def first_paragraph(md):
    for blk in md.split("\n\n"):
        s = blk.strip()
        if s and not s.startswith(("#", "|", "!", ">")) and "`" not in s[:1]:
            return s[:160]
    return ""


def main():
    args = sys.argv[1:]
    use_local = "--local" in args
    langs = ["zh"]
    for a in args:
        if a.startswith("--langs"):
            langs = a.split("=", 1)[1].split(",") if "=" in a else langs
    for lang in langs:
        outdir = os.path.join(HERE, "docs", lang)
        os.makedirs(outdir, exist_ok=True)
        index = []
        print(f"== lang={lang} local={use_local} ==")
        for slug, label in PAGES:
            try:
                markup = get_html(slug, lang, use_local)
                md, art = html_to_markdown(markup)
            except Exception as e:  # noqa
                print(f"  ! {slug}: FAILED {e}")
                continue
            title = md.split("\n", 1)[0].lstrip("# ").strip() or label
            header = f"<!-- 来源: {BASE}/docs/{lang}/{slug} | 自动同步, 勿手改 -->\n\n"
            body = header + md + "\n"
            with open(os.path.join(outdir, f"{slug}.md"), "w", encoding="utf-8") as f:
                f.write(body)
            summary = first_paragraph(md)
            index.append((slug, label, title, summary))
            print(f"  ok {slug:10} {len(md):6} chars  {title[:30]}")
        lines = [f"# Magpie 文档索引 ({lang})\n",
                 f"> 本页由 sync.py 自动生成。写插件/配置前, 先按需打开下面对应的 `docs/{lang}/xxx.md`。\n"]
        for slug, label, title, summary in index:
            link = f"[docs/{lang}/{slug}.md](docs/{lang}/{slug}.md)"
            lines.append(f"- **{label}** — {link}")
            if summary:
                lines.append(f"  - {summary}")
        with open(os.path.join(outdir, "index.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"  -> docs/{lang}/index.md")


if __name__ == "__main__":
    main()
