from datetime import date

import logfire
from sqlalchemy.orm import Session

from app.crud import get_or_create_artist, get_or_create_concert, get_or_create_venue
from app.database import Base, SessionLocal, engine
from app.schemas import ArtistCreate, ConcertCreate, VenueCreate
from common.dataclasses import ArtistShows
from sources import ArtistBoundSource
from sources.artist_website import ArtistWebsiteSource
from sources.email import EmailSource
from sources.songkick import SongkickSource

logfire.configure()
logfire.instrument_pydantic_ai()

Base.metadata.create_all(bind=engine)


def main():
    db = SessionLocal()
    artist_name = "Melody's Echo Chamber"
    artist_name = "Men I Trust"

    # TODO: add logging
    # TODO: switch to async
    for source_class in [ArtistWebsiteSource, SongkickSource, EmailSource]:
        # AI? what about this?
        if issubclass(source_class, ArtistBoundSource):
            source = source_class(artist_name)
            source.resolve(db)
        else:
            source = source_class()

        shows = source.fetch_shows(db)
        add_shows_to_db(db, shows)

    db.commit()

    return


def add_shows_to_db(db: Session, artist_shows: list[ArtistShows]):
    if len(artist_shows) == 0:
        return

    for artist_show in artist_shows:
        artist_name = artist_show.artist_name
        artist = get_or_create_artist(db, ArtistCreate(name=artist_name))
        for show_details in artist_show.shows:
            venue_id = None
            if show_details.venue:
                venue = get_or_create_venue(
                    db,
                    VenueCreate(
                        name=show_details.venue,
                        city=show_details.city,
                        country=show_details.country,
                        country_code=show_details.country_code,
                    ),
                )
                venue_id = venue.id

            if not isinstance(show_details.date, date):
                logfire.warning("Need to implement the date parsing logic")
                continue
                # raise NotImplementedError("Need to implement the date parsing logic")

            _ = get_or_create_concert(
                db,
                ConcertCreate(
                    date=show_details.date,
                    artist_id=artist.id,
                    venue_id=venue_id,
                    source_url=show_details.source_url,
                    city=show_details.city,
                    country=show_details.country,
                    country_code=show_details.country_code,
                ),
            )


if __name__ == "__main__":
    main()
