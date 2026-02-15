from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime

from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

from common.constants import LLM_MODEL_NAME
from tools.web import fetch_web_content


@dataclass
class ShowDetails:
    # TODO: certain parts of the code talk about "Show", other talk about "Concert". We
    # should standardize.
    date: datetime | date | str
    city: str
    country: str | None
    country_code: str | None  # ISO 3166-1 alpha-2 country code
    venue: str | None


class Source(ABC):
    def __init__(self, artist_name: str):
        self.artist_name: str = artist_name

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @abstractmethod
    def fetch_shows(self) -> list[ShowDetails]:
        pass
