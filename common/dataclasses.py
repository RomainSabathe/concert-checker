from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy.orm import Session

# AI? Is this `dataclasses` file really the best place where to put these "I/O"
# dataclasses for agents?


@dataclass
class Url:
    url: str | None


# AI? Should this be a Pydantic base class? So that I could to .dump()?
# Would be useful in e.g. `add_shows_to_db`.
@dataclass
class ShowDetails:
    # TODO: certain parts of the code talk about "Show", other talk about "Concert". We
    # should standardize.
    date: datetime | date | str
    city: str
    state: str | None
    country: str | None
    country_code: str | None  # ISO 3166-1 alpha-2 country code
    venue: str | None

    source_url: str  # URL of the page where the show details were found


@dataclass
class EmailContent:
    subject: str
    from_addr: str
    to_addr: str
    date: str
    body: str


@dataclass
class AgentDependency:
    db: Session
