from dataclasses import dataclass
from datetime import date, datetime

from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

from concert_checker.common.constants import LLM_MODEL_NAME
from concert_checker.tools.web import fetch_web_content


@dataclass
class ArtistWebsite:
    url: str | None


@dataclass
class ShowDetails:
    # TODO: certain parts of the code talk about "Show", other talk about "Concert". We
    # should standardize.
    date: datetime | date | str
    city: str
    country: str | None
    country_code: str | None  # ISO 3166-1 alpha-2 country code
    venue: str | None


def find_artist_website(artist_name: str) -> str:
    """Find the official website of a music artist.

    Args:
        artist_name (str): The name of the artist.

    Returns:
        ArtistWebsite: An object containing the URL of the artist's official website.
    """
    # TODO: add the website to the db.
    if artist_name == "Men I Trust":
        return "https://menitrust.com/"

    response = ArtistWebsiteFinderAgent.run_sync(
        f"What is the official website of the artist '{artist_name}'?"
    )
    if response.output.url is None:
        # TODO: add an exception in case the url is not found (None)
        pass
    return response.output.url


ArtistWebsiteFinderAgent = Agent(
    LLM_MODEL_NAME,
    system_prompt="""
    You are a helpful assistant that finds the official website of a music artist. When
    given the name of an artist, you will search for their official website and return
    the URL. If you cannot find the website, return null.""",
    tools=[duckduckgo_search_tool()],
    output_type=ArtistWebsite,
)

ArtistWebsiteShowExtractorAgent = Agent(
    LLM_MODEL_NAME,
    system_prompt=f"""
        You are a helpful assistant that navigates the official website of a music
        artist to extract the list of show dates from this artist. Show dates are often
        located either on the front page or in dedicated pages (for instance named:
        "Live", "Shows", "Tour", etc.).

        The current date is {datetime.now().date}. If show dates are missing the year
        information, deduce it based on the current date. For instance, if the show date
        is "December 15" and the current date is "June 1, 2024", then the show date
        should be "December 15, 2024" since it is in the future or that happened in the
        current year.

        If you cannot find any show date, return an empty list.
        """,
    # TODO: add a hash of the website so we only parse when updates are detected
    tools=[find_artist_website, fetch_web_content],
    output_type=list[ShowDetails],
)

ArtistWebsiteBrowserAgent = Agent(
    LLM_MODEL_NAME,
    system_prompt="""
    You are a helpful assistant that navigates to the official website of a music artist
    and retrieves information from it. When given the name of an artist, you will first
    search for their official website and then navigate to it to retrieve the required
    information. If you cannot find the website, return an empty string.""",
    tools=[],
    output_type=str,
)
