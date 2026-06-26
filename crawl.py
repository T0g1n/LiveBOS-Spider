"""
LiveBOS 文档爬虫
- 下载所有 143 个主题页面
- 提取并下载所有图片（848 张）
- HTML → Markdown 转换
- 生成完整目录索引
"""
import asyncio
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE_URL = "http://127.0.0.1:55706/help/"
TOPIC_BASE = urljoin(BASE_URL, "topic/com.apex.livebos.stuido.help/html/")
OUTPUT = Path("output")
CONCURRENCY = 5

# ============================================================
# 工具函数
# ============================================================


def safe_name(text: str) -> str:
    """将中文标题转为安全的文件名"""
    # 移除或替换 Windows 文件名中的非法字符
    text = re.sub(r'[<>:"/\\|?*]', '_', text)
    # 压缩空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else "untitled"


def clean_mso_html(soup: BeautifulSoup) -> str:
    """清理 Word 生成的冗余 HTML"""
    # 移除 <o:p> 等 MSO 标签
    for tag in soup.find_all(re.compile(r'o:p|st1:|v:|w:')):
        tag.unwrap()

    # 移除 "if !vml" / "endif" 等 MSO 条件注释文本
    mso_pattern = re.compile(
        r'(?:if\s*!\s*vml|endif|if\s*gte\s*mso|if\s*!supportLineBreakNewLine)',
        re.IGNORECASE,
    )
    for text in soup.find_all(string=mso_pattern):
        text.extract()

    # 移除 script 和 style
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()

    # 移除空的 span
    for span in soup.find_all("span"):
        if not span.get_text(strip=True) and not span.find("img"):
            span.decompose()

    # 移除面包屑导航（已通过 frontmatter 保留）
    breadcrumb = soup.find("div", class_="help_breadcrumbs")
    if breadcrumb:
        breadcrumb.decompose()

    # 清理 <a> 标签中无效的 nav 链接（../../nav/... 等不可用）
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "../nav/" in href or "advanced/synchWithToc" in href:
            a.unwrap()  # 保留文本，去掉链接

    return str(soup)


def html_to_markdown(html: str) -> str:
    """HTML 转 Markdown"""
    # markdownify
    text = md(
        html,
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
    )
    # 清理 MSO 残留: if !vml / endif 等
    text = re.sub(r'\bif\s*!\s*vml\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bendif\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<!--\[if[^\]]*\]>', '', text)
    text = re.sub(r'<!\[endif\]-->', '', text)
    # 清理 lang=EN-US 等残留标签
    text = re.sub(r'\{[^}]*\}', '', text)
    # 清理多余空行
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    # 清理只有空白的行
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    # 清理行首行尾空白
    text = '\n'.join(line.strip() for line in text.split('\n'))
    return text.strip()


# ============================================================
# 页面下载和处理
# ============================================================


async def fetch_page(
    client: httpx.AsyncClient,
    url: str,
) -> tuple[str, str] | None:
    """下载页面，返回 (html, encoding)"""
    try:
        resp = await client.get(url, follow_redirects=True)
        # Topic 页面使用 GBK 编码（Content-Type header 中无 charset）
        # 直接解码原始字节，避免 httpx 的 text 缓存问题
        raw = resp.content
        for enc in ["gbk", "gb18030", "gb2312", "utf-8"]:
            try:
                return raw.decode(enc), enc
            except (UnicodeDecodeError, LookupError):
                continue
        return raw.decode("gbk", errors="replace"), "gbk"
    except Exception as e:
        print(f"  [ERROR] {url}: {e}")
        return None


async def download_image(
    client: httpx.AsyncClient,
    img_url: str,
    local_path: Path,
) -> bool:
    """下载单张图片到本地"""
    if local_path.exists() and local_path.stat().st_size > 0:
        return True  # 已下载
    try:
        resp = await client.get(img_url, follow_redirects=True)
        if resp.status_code == 200 and len(resp.content) > 0:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(resp.content)
            return True
        return False
    except Exception:
        return False


def extract_page_content(html: str) -> tuple[BeautifulSoup, str, str]:
    """
    从页面提取：
    - soup: 正文内容区域 (id='helpdiv')
    - title: 页面标题
    - breadcrumbs: 面包屑路径文本
    """
    soup = BeautifulSoup(html, "lxml")

    # 提取标题
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # 如果没有 helpdiv 标题，从 h1 取
    h1 = soup.find("h1")
    if not title and h1:
        title = h1.get_text(strip=True)

    # 提取面包屑
    breadcrumb_div = soup.find("div", class_="help_breadcrumbs")
    breadcrumbs = ""
    if breadcrumb_div:
        crumbs = [a.get_text(strip=True) for a in breadcrumb_div.find_all("a")]
        breadcrumbs = " > ".join(crumbs)

    # 提取正文
    helpdiv = soup.find("div", id="helpdiv")
    if helpdiv:
        content_soup = helpdiv
    else:
        # fallback: 使用 body
        body = soup.find("body")
        content_soup = body if body else soup

    return content_soup, title, breadcrumbs


def collect_images(soup: BeautifulSoup, page_url: str) -> list[tuple[str, str]]:
    """
    收集页面中的所有图片
    返回 [(img_url, local_relative_path), ...]
    """
    images = []
    seen = set()
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src:
            continue
        abs_url = urljoin(page_url, src)
        if abs_url in seen:
            continue
        seen.add(abs_url)

        # 图片本地相对路径：保持与页面的相对关系
        # entity_object.files/image002.jpg → 保持不变
        images.append((abs_url, src))
    return images


async def process_topic(
    client: httpx.AsyncClient,
    topic: dict,
    sem: asyncio.Semaphore,
    stats: dict,
):
    """处理单个主题页面：下载、转 MD、下载图片"""
    page_url = topic["url"]
    nav_id = topic.get("cp", topic.get("href", "").split("cp=")[-1] if "cp=" in topic.get("href", "") else "")

    # 构建输出路径
    # 从 URL 中提取相对路径
    rel = page_url.replace(TOPIC_BASE, "")
    if "?" in rel:
        rel = rel.split("?")[0]

    out_md = OUTPUT / rel.replace(".html", ".md").replace(".htm", ".md")

    async with sem:
        result = await fetch_page(client, page_url)

    if result is None:
        stats["failed_pages"] += 1
        return

    html, _ = result
    content_soup, title, breadcrumbs = extract_page_content(html)

    # 收集图片
    images = collect_images(content_soup, page_url)

    # 下载图片（并发）
    if images:
        img_tasks = []
        for abs_url, rel_path in images:
            img_local = out_md.parent / rel_path.lstrip("./")
            img_tasks.append(download_image(client, abs_url, img_local))

        img_results = await asyncio.gather(*img_tasks)
        stats["images"] += sum(1 for r in img_results if r)
        stats["failed_images"] += sum(1 for r in img_results if not r)

    # 清理 HTML 并转换为 Markdown
    cleaned = clean_mso_html(content_soup)
    markdown = html_to_markdown(cleaned)

    # 构建最终 Markdown
    final_md = f"# {title}\n\n"
    if breadcrumbs:
        final_md += f"> {breadcrumbs}\n\n"
    final_md += "---\n\n"
    final_md += markdown
    final_md += "\n"

    # 保存
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(final_md, encoding="utf-8")
    stats["pages"] += 1


# ============================================================
# 目录树构建
# ============================================================


async def discover_tree(
    client: httpx.AsyncClient,
    nav_id: str,
    depth: int = 0,
    breadcrumb: list[str] | None = None,
    max_depth: int = 6,
) -> dict | None:
    """递归发现导航树"""
    if depth > max_depth:
        return None

    if breadcrumb is None:
        breadcrumb = []

    url = f"{BASE_URL}nav/{nav_id}"
    try:
        resp = await client.get(url, follow_redirects=True)
        # Nav 页面是 UTF-8 编码（Content-Type: text/html;charset=utf-8）
        # 不要强制设置 encoding，信任 httpx 自动检测
        html = resp.text
    except Exception:
        return None

    soup = BeautifulSoup(html, "lxml")
    title_tag = soup.select_one("h1.NavTitle")
    title = title_tag.get_text(strip=True) if title_tag else nav_id

    node = {
        "type": "nav",
        "id": nav_id,
        "title": title,
        "children": [],
    }

    for li in soup.select("ul.NavList > li"):
        a = li.find("a")
        if not a or not a.get("href"):
            continue
        href = a["href"].strip()
        item_title = a.get_text(strip=True)

        if not href.startswith("../topic/"):
            # 子导航
            child_nav = href.replace("../nav/", "")
            child = await discover_tree(client, child_nav, depth + 1, [], max_depth)
            if child:
                node["children"].append(child)
        else:
            # 主题页面
            topic_url = urljoin(BASE_URL, href.lstrip("../"))
            node["children"].append({
                "type": "topic",
                "title": item_title,
                "url": topic_url,
                "href": href,
                "cp": href.split("cp=")[-1] if "cp=" in href else "",
            })

    return node


# ============================================================
# 索引文件生成
# ============================================================


def generate_index(node: dict, base_path: Path, depth: int = 0):
    """
    递归生成目录索引 Markdown 文件
    nav 节点生成 index.md，topic 节点生成相应路径
    """
    if node["type"] == "nav":
        # 为导航节点生成 index.md
        idx_path = base_path / "index.md"
        lines = [f"{'#' * (depth + 2)} {node['title']}\n"]

        if node.get("children"):
            for child in node["children"]:
                safe_title = safe_name(child["title"])

                if child["type"] == "nav":
                    # nav 节点链接到其子目录
                    child_dir = safe_title
                    lines.append(f"- [{child['title']}]({child_dir}/index.md)")
                    # 递归
                    generate_index(child, base_path / child_dir, depth + 1)
                else:
                    # topic 节点 - 计算对应 markdown 文件的路径
                    url_path = child["url"]
                    if "?" in url_path:
                        url_path = url_path.split("?")[0]
                    # 先替换 .html 再替换 .htm，避免 .html → .mdl 的问题
                    url_path = url_path.replace(".html", ".md").replace(".htm", ".md")
                    # 计算相对路径: 从 index.md 所在目录到 md 文件
                    rel = url_path.replace(TOPIC_BASE, "")
                    md_abs = OUTPUT / rel
                    # 使用 os.path.relpath 计算相对路径
                    md_rel = os.path.relpath(str(md_abs), str(base_path))
                    lines.append(f"- [{child['title']}]({md_rel.replace(os.sep, '/')})")

        idx_path.parent.mkdir(parents=True, exist_ok=True)
        idx_path.write_text("\n".join(lines), encoding="utf-8")


def map_tree_to_topics(node: dict) -> list[dict]:
    """收集所有 topic 叶子节点"""
    topics = []

    def visit(n):
        if n["type"] == "topic":
            topics.append(n)
        for child in n.get("children", []):
            visit(child)

    visit(node)
    return topics


# ============================================================
# 主流程
# ============================================================


async def main():
    print("=" * 60)
    print("LiveBOS 文档爬虫")
    print("=" * 60)

    stats = {"pages": 0, "failed_pages": 0, "images": 0, "failed_images": 0}

    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        # Phase 1: 发现目录树
        print("\n[Phase 1] 发现文档结构...")
        tree = await discover_tree(client, "1", max_depth=6)
        topics = map_tree_to_topics(tree)
        print(f"  发现 {len(topics)} 个主题页面")

        # Phase 2: 下载所有页面
        print(f"\n[Phase 2] 下载页面和图片 (并发={CONCURRENCY})...")
        sem = asyncio.Semaphore(CONCURRENCY)

        # 分批处理，显示进度
        batch = 20
        for i in range(0, len(topics), batch):
            chunk = topics[i : i + batch]
            tasks = [process_topic(client, t, sem, stats) for t in chunk]
            await asyncio.gather(*tasks)
            done = min(i + batch, len(topics))
            print(f"  [{done}/{len(topics)}] 页面: {stats['pages']}, "
                  f"图片: {stats['images']}, "
                  f"失败: 页面{stats['failed_pages']}/图片{stats['failed_images']}")

        # Phase 3: 生成目录索引
        print("\n[Phase 3] 生成目录索引...")
        OUTPUT.mkdir(parents=True, exist_ok=True)

        # 将 nav 树映射到输出目录结构
        concept = tree["children"][0] if len(tree["children"]) > 0 else None  # 概念手册 1_0
        devguide = tree["children"][1] if len(tree["children"]) > 1 else None  # 开发指南 1_1
        manual = tree["children"][2] if len(tree["children"]) > 2 else None  # 用户手册 1_2

        for section, dir_name in [
            (concept, "concept"),
            (devguide, "devguide"),
            (manual, "manual"),
        ]:
            if section:
                section_dir = OUTPUT / dir_name
                generate_index(section, section_dir, depth=0)

        # 顶层索引
        root_idx = OUTPUT / "index.md"
        root_lines = [
            "# LiveBOS Studio 帮助文档\n",
            f"> 共 {stats['pages']} 个页面, {stats['images']} 张图片\n",
            "## 目录\n",
        ]
        if concept:
            root_lines.append(f"- [概念手册](concept/index.md)")
        if devguide:
            root_lines.append(f"- [LiveBOS应用开发指南](devguide/index.md)")
        if manual:
            root_lines.append(f"- [用户手册](manual/index.md)")
        root_idx.write_text("\n".join(root_lines), encoding="utf-8")

        print("  目录索引已生成")

    # 总结
    print("\n" + "=" * 60)
    print(f"完成!")
    print(f"  页面: {stats['pages']} 成功, {stats['failed_pages']} 失败")
    print(f"  图片: {stats['images']} 成功, {stats['failed_images']} 失败")
    print(f"  输出: {OUTPUT.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
