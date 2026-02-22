from datetime import datetime
from typing import override

from pydantic_ai import Agent
from sqlalchemy.orm import Session

from common.constants import LLM_MODEL_NAME
from common.dataclasses import AgentDependency, ArtistShows
from sources import Source
from tools.db import add_artist_to_db, list_artists_in_db
from tools.email import fetch_unread_emails
from tools.web import fetch_web_content


class EmailSource(Source):
    @override
    def fetch_shows(self, db: Session) -> list[ArtistShows]:
        emails = fetch_unread_emails()
        if not emails:
            return []

        # TODO: have the presale/sale as first-class citizen. Right now I'm afraid the
        # agent may miss out on some important information because it doesn't provide
        # the information in the correct way (e.g. "tour annonced! dates tbc!")
        # TODO: right now, festivals will not be correctly extracted, because we only
        # extract 1 artist per each email. But, the fondamental question is: should we
        # allow to fetch info from artists that are not in the db? (i.e that we haven't
        # expressed an interest towards)? Actually, we would scrap the info from _all_
        # artists (in the email), and have a system of "favorite" to only get
        # notifications from those...
        show_extractor_agent = Agent(
            LLM_MODEL_NAME,
            system_prompt=f"""
                You are reading emails coming from a musical artist newsletter/email
                list.

                Your task is 3-fold:

                1. Identify the name of the artist. Use the `list_artists_in_db` tool
                to check if the artist already exists in the database. If a match is
                found, use the EXACT name from the database. If no match is found, use
                `add_artist_to_db` to register the new artist.
                2. Identify whether the email contains information about upcoming shows
                and, if so, extract the content of said shows. "Shows" can refer to
                tour dates, one-off shows, festival appearances, and presale
                announcements.
                3. For each show, extract: the date, city, country, venue (if
                mentioned), and any other location details.

                You are allowed to follow links contained in the email (e.g. in case
                the show information is on the linked page).

                The current date is {datetime.now().date()}. If an email mentions
                dates without a year, assume they refer to the nearest future occurrence
                of that date.

                For the `source_url` field: if the show info comes directly from the
                email body, set it to the sender's email address. If you followed a
                link to find the show info, set it to that URL.

                If the emails don't announce any shows, return an empty list.
                """,
            tools=[list_artists_in_db, add_artist_to_db, fetch_web_content],
            output_type=ArtistShows,
            deps_type=AgentDependency,
        )

        # TODO: async
        all_artist_shows: list[ArtistShows] = []
        for email in emails:
            email_text = f"Subject: {email.subject}\nFrom: {email.from_addr}\nDate: {email.date}\n\n{email.body}"
            artist_shows = show_extractor_agent.run_sync(
                email_text, deps=AgentDependency(db=db)
            ).output
            if artist_shows:
                all_artist_shows.append(artist_shows)

        return all_artist_shows
