from dataclasses import dataclass
from datetime import date, datetime

# AI? Is this `dataclasses` file really the best place where to put these "I/O"
# dataclasses for agents?


@dataclass
class Url:
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
