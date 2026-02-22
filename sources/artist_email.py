import re
from datetime import datetime
from typing import override

from pydantic_ai import Agent
from sqlalchemy.orm import Session

from common.constants import EMAIL_DOMAIN, LLM_MODEL_NAME
from common.dataclasses import ShowDetails
from sources import Source
from tools.email import fetch_unread_emails


def _slugify(name: str) -> str:
    """Convert an artist name to an email-safe slug.

    "Men I Trust" -> "men-i-trust"
    """
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


class ArtistEmailSource(Source):
    def __init__(self, artist_name: str, *args, **kwargs):
        super().__init__(artist_name, *args, **kwargs)
        self.slug = _slugify(artist_name)
        self.email_address = f"{self.slug}@{EMAIL_DOMAIN}"

    @override
    def resolve(self, db: Session):
        pass

    @override
    def fetch_shows(self, db: Session) -> list[ShowDetails]:
        emails = fetch_unread_emails(self.email_address)
        if not emails:
            return []

        email_text = "\n\n---\n\n".join(
            f"Subject: {e.subject}\nDate: {e.date}\n\n{e.body}" for e in emails
        )

        show_extractor_agent = Agent(
            LLM_MODEL_NAME,
            system_prompt=f"""
                You are reading emails from the artist "{self.artist_name}".
                Your task is to extract any concert or show announcements from these
                emails, including tour dates, one-off shows, festival appearances,
                and presale announcements.

                For each show, extract: the date, city, country, venue (if mentioned),
                and any other location details.

                The current date is {datetime.now().date()}. If an email mentions
                dates without a year, assume they refer to the nearest future occurrence
                of that date.

                The `source_url` field should be set to
                "email:{self.email_address}" since these come from emails, not
                web pages.

                If the emails don't announce any shows, return an empty list.
                """,
            output_type=list[ShowDetails],
        )
        return show_extractor_agent.run_sync(email_text).output
