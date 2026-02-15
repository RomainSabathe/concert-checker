import datetime
from datetime import datetime
from typing import override

from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from sqlalchemy.orm import Session

from app.crud import get_or_create_artist, update_artist
from app.schemas import ArtistCreate, ArtistUpdate
from common.constants import LLM_MODEL_NAME
from common.dataclasses import ShowDetails, Url
from sources import Source
from tools.web import fetch_web_content


class ArtistWebsiteSource(Source):
    def __init__(self, artist_name: str, *args, **kwargs):
        super().__init__(artist_name, *args, **kwargs)

        self._base_url: str | None = None

    @property
    def base_url(self) -> str:
        if self._base_url is None:
            raise ValueError("Base URL not resolved yet. Please call resolve() first.")
        return self._base_url

    @override
    def resolve(self, db: Session):
        # TODO: add docstring
        # Populating the DB with the website base url
        artist = get_or_create_artist(db, ArtistCreate(name=self.artist_name))
        if (url := artist.website_base_url) is None:
            url = find_artist_website(self.artist_name)
            _ = update_artist(db, ArtistUpdate(id=artist.id, website_base_url=url))
            # TODO: encapsulate db logic in try/except?

        self._base_url = url

    @override
    def fetch_shows(self) -> list[ShowDetails]:
        show_extractor_agent = Agent(
            LLM_MODEL_NAME,
            system_prompt=f"""
                You are a helpful assistant that navigates the official website of the
                artist "{self.artist_name}" and extracts the list of show dates. Your task is
                to to extract the list of show dates from this artist. Show dates are
                often located either on the front page or in dedicated pages (for
                instance named: "Live", "Shows", "Tour", "Concerts", etc.).

                The artist's official website is {self.base_url}. You can fetch the
                content of any page of the website using the provided tool.

                The current date is {datetime.now().date}. If show dates are missing the year
                information, deduce it based on the current date. For instance, if the show date
                is "December 15" and the current date is "June 1, 2024", then the show date
                should be "December 15, 2024" since it is in the future or that happened in the
                current year.
                The `source_url` field of the output should be the URL of the page where
                you found the show details.

                If you cannot find any show date, return an empty list.
                """,
            # TODO: add a hash of the website so we only parse when updates are detected
            tools=[fetch_web_content],
            output_type=list[ShowDetails],
        )
        return show_extractor_agent.run_sync(self.artist_name).output


def find_artist_website(artist_name: str) -> str:
    """Find the official website of a music artist.

    Args:
        artist_name (str): The name of the artist.

    Returns:
        ArtistWebsite: An object containing the URL of the artist's official website.
    """
    agent = Agent(
        LLM_MODEL_NAME,
        system_prompt="""
        You are a helpful assistant that finds the official website of a music artist. When
        given the name of an artist, you will search for their official website and return
        the URL. If you cannot find the website, return null.""",
        tools=[duckduckgo_search_tool()],
        output_type=Url,
    )
    response = agent.run_sync(
        f"What is the official website of the artist '{artist_name}'?"
    )
    if response.output.url is None:
        # TODO: add an exception in case the url is not found (None)
        pass
    url = response.output.url
    return url
