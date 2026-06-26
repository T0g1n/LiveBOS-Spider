"""Whoosh 全文搜索引擎"""
import re
from pathlib import Path

from jieba.analyse import ChineseAnalyzer
from whoosh import index
from whoosh.fields import ID, TEXT, Schema
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.query import Every

from .config import DOCS_DIR, INDEX_DIR, EXCLUDE_PATTERNS

# Whoosh Schema
ANALYZER = ChineseAnalyzer()

SCHEMA = Schema(
    path=ID(stored=True, unique=True),
    title=TEXT(stored=True, analyzer=ANALYZER),
    content=TEXT(stored=True, analyzer=ANALYZER),
    breadcrumbs=TEXT(stored=True, analyzer=ANALYZER),
)


def _parse_markdown(filepath: Path) -> dict | None:
    """解析 Markdown 文件，提取 title、breadcrumbs、content"""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return None

    lines = text.split("\n")
    title = ""
    breadcrumbs = ""
    content_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        # 面包屑: > LiveBOS Studio > ...
        if stripped.startswith("> ") and "LiveBOS Studio" in stripped:
            breadcrumbs = stripped.lstrip("> ").strip()
        # 标题: # Title
        elif stripped.startswith("# ") and not title:
            title = stripped.lstrip("# ").strip()
        # 水平线 --- 标志着 header 结束
        elif stripped == "---" and (title or breadcrumbs):
            content_start = i + 1
            break

    # 正文：header 之后的内容，去掉图片引用
    content_lines = lines[content_start:]
    content = "\n".join(content_lines)
    # 移除 Markdown 图片语法以减小索引体积
    content = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', content)
    # 压缩空白行
    content = re.sub(r'\n{3,}', '\n\n', content).strip()

    if not title:
        title = filepath.stem

    # 相对路径（去掉 output/ 前缀）
    try:
        rel_path = filepath.relative_to(DOCS_DIR).as_posix()
    except ValueError:
        rel_path = filepath.as_posix()

    return {
        "path": rel_path,
        "title": title,
        "content": content,
        "breadcrumbs": breadcrumbs,
    }


def _is_excluded(rel_path: str) -> bool:
    """检查路径是否在排除列表中（中文导航 index.md）"""
    for pattern in EXCLUDE_PATTERNS:
        if pattern in rel_path:
            return True
    return False


class DocSearcher:
    """LiveBOS 文档搜索引擎"""

    def __init__(self):
        self.docs_dir = DOCS_DIR
        self.index_dir = INDEX_DIR
        self._ix = None

    @property
    def ix(self):
        if self._ix is None:
            self._ix = index.open_dir(str(self.index_dir))
        return self._ix

    def index_exists(self) -> bool:
        return self.index_dir.exists() and index.exists_in(str(self.index_dir))

    def build_index(self):
        """构建/重建全文索引"""
        self.index_dir.mkdir(parents=True, exist_ok=True)
        ix = index.create_in(str(self.index_dir), SCHEMA)

        writer = ix.writer()
        count = 0

        for filepath in self.docs_dir.rglob("*.md"):
            rel_path = filepath.relative_to(self.docs_dir).as_posix()

            # 跳过中文导航目录的 index.md
            if _is_excluded(rel_path):
                continue

            doc = _parse_markdown(filepath)
            if doc is None:
                continue

            writer.add_document(**doc)
            count += 1

        writer.commit()
        self._ix = ix

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """
        全文搜索
        返回 [{path, title, breadcrumbs, score, snippet}, ...]
        """
        if not self.index_exists():
            self.build_index()

        parser = MultifieldParser(
            ["title", "content", "breadcrumbs"],
            schema=self.ix.schema,
            group=OrGroup,
        )

        try:
            q = parser.parse(query)
        except Exception:
            return []

        results = []
        with self.ix.searcher() as searcher:
            hits = searcher.search(q, limit=limit)
            for hit in hits:
                # 提取高亮摘要
                snippet = hit.highlights("content", top=3)
                if not snippet:
                    # fallback: 取内容前 300 字符
                    content = hit.get("content", "")
                    snippet = content[:300]

                results.append({
                    "path": hit["path"],
                    "title": hit.get("title", ""),
                    "breadcrumbs": hit.get("breadcrumbs", ""),
                    "score": round(hit.score, 2),
                    "snippet": snippet,
                })

        return results

    def get_document(self, path: str) -> str | None:
        """获取文档完整内容"""
        # 尝试英文路径
        filepath = self.docs_dir / path
        if filepath.exists() and filepath.suffix == ".md":
            return filepath.read_text(encoding="utf-8")

        # 尝试添加 .md
        filepath = self.docs_dir / (path + ".md")
        if filepath.exists():
            return filepath.read_text(encoding="utf-8")

        # 搜索匹配的路径
        if self.index_exists():
            with self.ix.searcher() as searcher:
                results = searcher.search(Every("path"), limit=None)
                for hit in results:
                    if path in hit["path"] or hit["path"].endswith(path):
                        fp = self.docs_dir / hit["path"]
                        if fp.exists():
                            return fp.read_text(encoding="utf-8")

        return None

    def list_documents(self, directory: str = "") -> list[str]:
        """列出文档目录结构"""
        base = self.docs_dir / directory if directory else self.docs_dir
        if not base.exists():
            return []

        paths = []
        for item in sorted(base.rglob("*.md")):
            rel = item.relative_to(self.docs_dir).as_posix()
            if _is_excluded(rel):
                continue
            paths.append(rel)

        return paths

    def doc_count(self) -> int:
        """索引文档数"""
        if not self.index_exists():
            return 0
        with self.ix.searcher() as searcher:
            return searcher.doc_count()
