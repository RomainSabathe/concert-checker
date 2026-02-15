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


class SongkickSource(Source):
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
        artist = get_or_create_artist(db, ArtistCreate(name=self.artist_name))
        if (url := artist.songkick_url) is None:
            url = find_songkick_url(self.artist_name)
            _ = update_artist(db, ArtistUpdate(id=artist.id, songkick_url=url))
        self._base_url = url

    @override
    def fetch_shows(self) -> list[ShowDetails]:
        # TODO: there's probably a way to abstract this...
        show_extractor_agent = Agent(
            LLM_MODEL_NAME,
            system_prompt=f"""
                You are a helpful assistant that reads the Songkick page of the
                artist "{self.artist_name}" and extracts the list of show dates. Your task is
                to to extract the list of show dates from this artist.

                The artist's Songkick page is {self.base_url}. You can fetch the
                content of any page of the website using the provided tool.

                The `source_url` field of the output should be the URL of the page where
                you found the show details.

                The current date is {datetime.now().date}. Songkick organizes the page
                into "Upcoming concerts" and "Past concerts".

                For upcoming concerts: if show dates are missing the year information,
                deduce it based on the current date. For instance, if the show date is
                "December 15" and the current date is "June 1, 2024", then the show date
                should be "December 15, 2024" since it is in the future or that happened
                in the current year.

                For past concerts: inverse logic applies.

                If you cannot find any show date, return an empty list.
                """,
            # TODO: add a hash of the website so we only parse when updates are detected
            tools=[fetch_web_content],
            output_type=list[ShowDetails],
        )
        return show_extractor_agent.run_sync(self.artist_name).output


def find_songkick_url(artist_name: str) -> str | None:
    agent = Agent(
        LLM_MODEL_NAME,
        system_prompt="""
        You are a helpful assistant that finds the  Songkick page of a musical artist.
        The Songkick page of an artist is the one that contains the list of
        shows of that artist. 

        It has the following format: "https://www.songkick.com/artists/{id}-{artist-name}"

        If you cannot find the Songkick page of the artist, return null.
        """,
        tools=[duckduckgo_search_tool()],
        output_type=Url,
    )
    response = agent.run_sync(
        f"What is the Songkick page of the artist '{artist_name}'?"
    )
    if response.output.url is None:
        raise ValueError(
            f"Could not find the Songkick page for artist '{artist_name}'."
        )
    url = response.output.url

    # The "/calendar" endpoint shows more shows.
    if not url.endswith("/calendar"):
        url = url.rstrip("/") + "/calendar"
    return url
