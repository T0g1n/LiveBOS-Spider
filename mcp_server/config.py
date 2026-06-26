"""MCP 服务器配置常量"""
from pathlib import Path

# 文档根目录（爬虫输出）
DOCS_DIR = Path(__file__).parent.parent / "output"

# Whoosh 索引目录
INDEX_DIR = Path(__file__).parent.parent / "search_index"

# 搜索设置
TOP_K = 5           # 默认返回结果数
MAX_SNIPPET = 500   # 摘要最大长度（字符）

# 排除的目录（中文导航 index.md，无实际内容）
EXCLUDE_PATTERNS = [
    "概念/", "对象模型/", "工作流/", "报表/", "门户/", "基础架构/", "高级开发/",
    "业务建模设计/", "导入导出功能/", "文档输出/", "附录/", "LiveBOS工作流设计器/",
]

# 联网搜索
WEB_SEARCH_URL = "https://html.duckduckgo.com/html/"
