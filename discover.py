"""
LiveBOS 文档结构发现脚本
递归爬取所有导航页面，构建完整文档目录树
"""
import asyncio
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

BASE = "http://127.0.0.1:55706/help/"


def resolve_url(href: str, base: str = BASE) -> str:
    """解析相对 URL"""
    return urljoin(base, href.lstrip("../"))


def safe_print(s: str):
    """安全打印，处理终端编码问题"""
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))


async def fetch(client: httpx.AsyncClient, url: str) -> str:
    """获取页面内容，自动检测编码"""
    resp = await client.get(url, follow_redirects=True)
    # 尝试多种编码
    for enc in ["gbk", "utf-8", "gb2312", "gb18030"]:
        try:
            resp.content.decode(enc)
            resp.encoding = enc
            return resp.text
        except (UnicodeDecodeError, LookupError):
            continue
    # fallback
    resp.encoding = "gbk"
    return resp.text


def extract_nav_items(html: str) -> list[dict]:
    """从导航页面提取子项（子导航页面 或 主题页面链接）"""
    soup = BeautifulSoup(html, "lxml")
    items = []
    for li in soup.select("ul.NavList > li"):
        a = li.find("a")
        if not a or not a.get("href"):
            continue
        href = a["href"].strip()
        title = a.get_text(strip=True)

        # 判断是子导航页还是主题页
        if href.startswith("../nav/") or (not href.startswith("../topic/") and not href.startswith("http")):
            # nav 页面（形如 "1_0_1" 或 "../nav/1_0"）
            nav_id = href.replace("../nav/", "")
            items.append({"type": "nav", "id": nav_id, "title": title, "href": href})
        else:
            # topic 页面
            items.append({"type": "topic", "title": title, "href": href})

    return items


def get_breadcrumbs(html: str) -> list[str]:
    """提取面包屑导航"""
    soup = BeautifulSoup(html, "lxml")
    crumbs = soup.select("div.help_breadcrumbs a")
    return [c.get_text(strip=True) for c in crumbs]


def get_title(html: str) -> str:
    """提取页面标题"""
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.select_one("h1.NavTitle")
    if h1:
        return h1.get_text(strip=True)
    t = soup.find("title")
    return t.get_text(strip=True) if t else ""


async def discover_tree(
    client: httpx.AsyncClient,
    nav_id: str,
    depth: int = 0,
    breadcrumb: list[str] = None,
    max_depth: int = 6,
):
    """递归发现导航树"""
    if depth > max_depth:
        return None

    if breadcrumb is None:
        breadcrumb = []

    url = f"{BASE}nav/{nav_id}"
    try:
        html = await fetch(client, url)
    except Exception as e:
        safe_print(f"  {'  ' * depth}[ERROR] {nav_id}: {e}")
        return None

    title = get_title(html)
    indent = "  " * depth
    safe_print(f"{indent}[nav/{nav_id}] {title}")

    node = {
        "type": "nav",
        "id": nav_id,
        "title": title,
        "url": url,
        "breadcrumbs": get_breadcrumbs(html) or breadcrumb + [title] if depth > 0 else [title],
        "children": [],
    }

    items = extract_nav_items(html)
    for item in items:
        if item["type"] == "nav":
            child = await discover_tree(
                client, item["id"], depth + 1, node["breadcrumbs"], max_depth
            )
            if child:
                node["children"].append(child)
        else:
            topic_url = resolve_url(item["href"])
            topic_node = {
                "type": "topic",
                "title": item["title"],
                "url": topic_url,
                "href": item["href"],
                "breadcrumbs": node["breadcrumbs"] + [item["title"]],
            }
            safe_print(f"{indent}  [topic] {item['title']} -> {topic_url}")
            node["children"].append(topic_node)

    return node


async def main():
    async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
        safe_print("=" * 70)
        safe_print("LiveBOS 文档结构发现")
        safe_print("=" * 70)

        # 只发现 LiveBOS 相关的导航（nav/1 及其子项）
        tree = await discover_tree(client, "1", max_depth=6)

        # 统计
        def count_nodes(node):
            count = {"nav": 0, "topic": 0}
            if node["type"] == "nav":
                count["nav"] += 1
            elif node["type"] == "topic":
                count["topic"] += 1
            for child in node.get("children", []):
                c = count_nodes(child)
                count["nav"] += c["nav"]
                count["topic"] += c["topic"]
            return count

        stats = count_nodes(tree)
        safe_print("\n" + "=" * 70)
        safe_print(f"统计: {stats['nav']} 个导航页面, {stats['topic']} 个主题页面")
        safe_print("=" * 70)

        return tree


if __name__ == "__main__":
    asyncio.run(main())
