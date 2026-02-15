from datetime import date

import logfire

from agents.artist_website_finder import ArtistWebsiteShowExtractorAgent
from app.crud import get_or_create_artist, get_or_create_concert, get_or_create_venue
from app.database import Base, SessionLocal, engine
from app.schemas import ArtistCreate, ConcertCreate, VenueCreate

logfire.configure()
logfire.instrument_pydantic_ai()

Base.metadata.create_all(bind=engine)


def main():
    db = SessionLocal()
    artist_name = "Men I Trust"

    artist = get_or_create_artist(db, ArtistCreate(name=artist_name))

    # Extracting shows for the artist
    out = ArtistWebsiteShowExtractorAgent.run_sync("Men I Trust")

    if len(out.output) == 0:
        logfire.warning(f"No shows found for artist '{artist_name}'.")
        return

    # Adding the shows to the database
    try:
        for show_details in out.output:
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
                raise NotImplementedError("Need to implement the date parsing logic")

            # Actually add the concert to the db
            _ = get_or_create_concert(
                db,
                ConcertCreate(
                    date=show_details.date, artist_id=artist.id, venue_id=venue_id
                ),
            )

        db.commit()

    finally:
        db.close()

    __import__("ipdb").set_trace()


if __name__ == "__main__":
    main()
