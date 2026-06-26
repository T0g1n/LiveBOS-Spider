from livebos_spider import Spider, SpiderConfig


def main():
    config = SpiderConfig(
        start_urls=["https://httpbin.org/html"],
        request_delay=1.0,
        max_pages=3,
    )
    spider = Spider(config)
    results = spider.run()

    print(f"\nDone! Crawled {len(results)} pages.")
    for item in results:
        print(f"  - {item['url']}: {item.get('title', 'N/A')}")


if __name__ == "__main__":
    main()
