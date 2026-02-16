import hashlib
from datetime import datetime

from crawl4ai import AsyncWebCrawler
from pydantic_ai import RunContext

from app.crud import get_or_create_page_cache
from app.schemas import PageCacheCreate
from common.dataclasses import AgentDependency


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


async def page_hash_has_changed(ctx: RunContext[AgentDependency], url: str) -> bool:
    """Check if the hash of the content of a web page has changed since the last check.

    This function fetches the current content of the web page, computes its hash, and
    compares it with the hash stored in the database. If the hash has changed, it
    updates the hash and the last updated timestamp in the database.

    This is useful to avoid re-parsing the content of a web page if it hasn't changed
    since the last check, which can save computational resources and reduce unnecessary
    API calls.

    Args:
        url: The URL of the web page to check.

    Returns:
        True if the hash has changed, False otherwise.
    """
    # TODO: continue with the run context..
    db = ctx.deps.db
    current_time = datetime.today()

    # Querying the DB
    page_cache = get_or_create_page_cache(db, PageCacheCreate(url=url))
    hash_in_cache = page_cache.content_hash
    page_cache.last_fetched_at = current_time

    # Checking the current content
    page_content = await fetch_web_content(url)
    current_hash = hashlib.sha256(page_content.encode()).hexdigest()

    hash_has_changed = current_hash is None or hash_in_cache != current_hash
    if hash_has_changed:
        page_cache.content_hash = current_hash
        page_cache.last_updated_at = current_time

    # AI? This is really bad I presume. This was supposed to ok but we were initially
    # just supposed to read the cache/db, but now we're writing to it...
    db.commit()
    return hash_has_changed
