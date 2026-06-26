"""联网搜索兜底"""
import asyncio

import httpx


async def _ddg_search(query: str, limit: int = 5) -> list[dict]:
    """使用 DuckDuckGo HTML 搜索"""
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    full_query = f"LiveBOS {query}"

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            resp = await client.post(
                url,
                data={"q": full_query},
                headers=headers,
                follow_redirects=True,
            )
            if resp.status_code != 200:
                return []

            from bs4 import BeautifulSoup

            soup = BeautifulSoup(resp.text, "html.parser")
            results = []

            for item in soup.select(".result")[:limit]:
                title_el = item.select_one(".result__title")
                snippet_el = item.select_one(".result__snippet")
                link_el = item.select_one(".result__url")

                title = title_el.get_text(strip=True) if title_el else ""
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                link = link_el.get("href", "") if link_el else ""

                if title:
                    results.append({
                        "title": title,
                        "url": link,
                        "snippet": snippet,
                    })

            return results

    except Exception:
        return []


async def search_web(query: str, limit: int = 5) -> list[dict]:
    """
    联网搜索 LiveBOS 相关信息
    返回 [{title, url, snippet}, ...]
    """
    results = await _ddg_search(query, limit)

    if not results:
        # DuckDuckGo 无结果，返回提示
        return [{
            "title": "未找到相关网络结果",
            "url": "",
            "snippet": (
                f"LiveBOS 本地文档中也未找到关于 '{query}' 的信息。"
                f"建议：\n"
                f"1. 尝试使用不同的关键词重新搜索本地文档\n"
                f"2. 访问 LiveBOS 官网获取最新信息\n"
                f"3. 联系 LiveBOS 技术支持"
            ),
        }]

    return results
