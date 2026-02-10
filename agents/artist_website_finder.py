from dataclasses import dataclass

from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

from common.constants import LLM_MODEL_NAME


@dataclass
class ArtistWebsite:
    url: str


ArtistWebsiteFinderAgent = Agent(
    LLM_MODEL_NAME,
    system_prompt="""
    You are a helpful assistant that finds the official website of a music artist. When
    given the name of an artist, you will search for their official website and return
    the URL. If you cannot find the website, return an empty string.""",
    tools=[duckduckgo_search_tool()],
    output_type=ArtistWebsite,
)
