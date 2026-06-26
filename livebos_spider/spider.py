import time
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


@dataclass
class SpiderConfig:
    """爬虫配置"""
    start_urls: list[str] = field(default_factory=list)
    concurrency: int = 1
    request_delay: float = 1.0
    timeout: float = 10.0
    headers: dict = field(default_factory=lambda: {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    })
    max_pages: int = 0
    allowed_domains: list[str] = field(default_factory=list)


class Spider:
    """基础爬虫"""

    def __init__(self, config: SpiderConfig | None = None):
        self.config = config or SpiderConfig()
        self._visited: set[str] = set()
        self._results: list[dict] = []

    def is_allowed_domain(self, url: str) -> bool:
        if not self.config.allowed_domains:
            return True
        domain = urlparse(url).netloc
        return any(d in domain for d in self.config.allowed_domains)

    def fetch(self, url: str) -> httpx.Response:
        """发送 HTTP 请求"""
        with httpx.Client(timeout=self.config.timeout) as client:
            response = client.get(url, headers=self.config.headers)
            response.raise_for_status()
            return response

    def parse(self, response: httpx.Response) -> BeautifulSoup:
        """解析 HTML"""
        return BeautifulSoup(response.text, "lxml")

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        """提取页面中的所有链接"""
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(base_url, href)
            if self.is_allowed_domain(full_url):
                links.append(full_url)
        return links

    def process_item(self, url: str, soup: BeautifulSoup) -> dict:
        """处理单个页面（子类可重写）"""
        return {"url": url, "title": soup.title.get_text(strip=True) if soup.title else ""}

    def run(self):
        """运行爬虫"""
        queue = list(self.config.start_urls)
        page_count = 0

        while queue:
            if self.config.max_pages and page_count >= self.config.max_pages:
                break

            url = queue.pop(0)
            if url in self._visited:
                continue

            self._visited.add(url)
            page_count += 1

            try:
                print(f"[{page_count}] Crawling: {url}")
                response = self.fetch(url)
                soup = self.parse(response)
                item = self.process_item(url, soup)
                self._results.append(item)
                links = self.extract_links(soup, url)
                queue.extend(links)

            except Exception as e:
                print(f"[{page_count}] Error: {url} - {e}")

            time.sleep(self.config.request_delay)

        return self._results
