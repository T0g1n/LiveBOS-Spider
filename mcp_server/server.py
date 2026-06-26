"""
LiveBOS 文档 MCP 服务器

提供 4 个工具:
- search_documents: 全文搜索 LiveBOS 文档
- get_document:    获取指定文档完整内容
- list_documents:  列出可用文档
- search_web:      联网搜索 LiveBOS 信息（兜底）
"""
import json
import sys

from fastmcp import FastMCP

from .config import DOCS_DIR, INDEX_DIR, TOP_K
from .searcher import DocSearcher
from .web_fallback import search_web as _web_search

# 创建 MCP 服务器实例
mcp = FastMCP("livebos_docs")

# 全局搜索引擎实例（延迟初始化）
_searcher: DocSearcher | None = None


def _get_searcher() -> DocSearcher:
    """获取搜索引擎实例，首次调用时构建索引"""
    global _searcher
    if _searcher is None:
        _searcher = DocSearcher()
        if not _searcher.index_exists():
            print(f"[livebos-docs] 正在构建搜索索引...", file=sys.stderr)
            _searcher.build_index()
            print(
                f"[livebos-docs] 索引构建完成: {_searcher.doc_count()} 个文档",
                file=sys.stderr,
            )
        else:
            print(
                f"[livebos-docs] 已加载索引: {_searcher.doc_count()} 个文档",
                file=sys.stderr,
            )
    return _searcher


# ============================================================
# MCP Tools
# ============================================================


@mcp.tool()
def search_documents(query: str, limit: int = TOP_K) -> str:
    """
    全文搜索 LiveBOS 文档，返回最相关的文档摘要。

    参数:
    - query: 搜索关键词（中文或英文），如 "实体对象"、"工作流"、"权限管理"
    - limit: 返回结果数量，默认 5

    返回: Markdown 格式的搜索结果，包含标题、路径、相关度和内容摘要。
    """
    searcher = _get_searcher()
    results = searcher.search(query.strip(), limit=limit)

    if not results:
        return (
            f"## 未找到与 \"{query}\" 相关的文档\n\n"
            f"建议:\n"
            f"- 尝试不同的关键词\n"
            f"- 使用 `list_documents` 查看所有文档\n"
            f"- 使用 `search_web` 联网搜索\n"
        )

    lines = [f"## 搜索结果: \"{query}\"\n"]

    for i, r in enumerate(results, 1):
        breadcrumbs = r.get("breadcrumbs", "")
        lines.append(f"### {i}. {r['title']}")
        lines.append(f"- **路径**: `{r['path']}`")
        if breadcrumbs:
            lines.append(f"- **分类**: {breadcrumbs}")
        lines.append(f"- **相关度**: {r['score']}")
        lines.append(f"\n{r['snippet']}\n")
        lines.append("---\n")

    return "\n".join(lines)


@mcp.tool()
def get_document(path: str) -> str:
    """
    获取指定文档的完整 Markdown 内容。

    参数:
    - path: 文档路径，如 "concept/object_model/object_type/entity_object.md"
            也支持模糊匹配，如 "entity_object" 或 "实体对象"

    返回: 文档的完整 Markdown 文本。
    """
    searcher = _get_searcher()
    content = searcher.get_document(path.strip())

    if content is None:
        return (
            f"## 未找到文档: \"{path}\"\n\n"
            f"请使用 `list_documents` 查看所有可用文档路径，"
            f"或使用 `search_documents` 搜索相关文档。\n"
        )

    return content


@mcp.tool()
def list_documents(directory: str = "") -> str:
    """
    列出所有可用的 LiveBOS 文档。

    参数:
    - directory: 可选，只列出指定目录下的文档。
                 如 "concept/object_model" 或 "manual"

    返回: Markdown 格式的文档列表。
    """
    searcher = _get_searcher()
    paths = searcher.list_documents(directory.strip() if directory else "")

    if not paths:
        return "## 未找到文档"

    # 按目录分组
    by_dir: dict[str, list[str]] = {}
    for p in sorted(paths):
        d = p.rsplit("/", 1)[0] if "/" in p else "."
        by_dir.setdefault(d, []).append(p.rsplit("/", 1)[-1])

    lines = [f"## 文档列表 ({len(paths)} 个文件)\n"]
    for d, files in sorted(by_dir.items()):
        lines.append(f"### {d}/")
        for f in files:
            full = f"{d}/{f}" if d != "." else f
            lines.append(f"- {f}  (`{full}`)")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def search_web(query: str) -> str:
    """
    联网搜索 LiveBOS 相关信息（当本地文档没有覆盖时使用）。

    参数:
    - query: 搜索关键词

    返回: Markdown 格式的网络搜索结果。
    """
    import asyncio

    results = asyncio.run(_web_search(query.strip()))

    if not results:
        return f"## 未找到与 \"{query}\" 相关的网络结果"

    lines = [f"## 网络搜索: \"{query}\"\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"### {i}. {r['title']}")
        if r.get("url"):
            lines.append(f"- **链接**: {r['url']}")
        lines.append(f"\n{r.get('snippet', '')}\n")
        lines.append("---\n")

    return "\n".join(lines)


# ============================================================
# MCP Resources
# ============================================================


@mcp.resource("docs://{path}")
def doc_resource(path: str) -> str:
    """通过 URI 直接读取文档内容: docs://concept/object_model/object_type/entity_object.md"""
    searcher = _get_searcher()
    content = searcher.get_document(path)
    if content is None:
        return f"Document not found: {path}"
    return content


# ============================================================
# 入口
# ============================================================


def main():
    """MCP 服务器入口（STDIO 传输）"""
    print("[livebos-docs] 启动 LiveBOS 文档 MCP 服务器...", file=sys.stderr)
    _get_searcher()  # 确保索引就绪
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
