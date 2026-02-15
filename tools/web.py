from crawl4ai import AsyncWebCrawler


async def fetch_web_content(url: str) -> str:
    """Fetch and extract content from a web page as markdown.

    Args:
        url: The URL of the web page to fetch.

    Returns:
        The page content converted to markdown format.
    """
    # TODO: add an alert/log in case we can't parse the content (output of the tool is
    # None)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url)
        return result.markdown
