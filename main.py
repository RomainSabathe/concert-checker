import logfire

from agents.artist_website_finder import ArtistWebsiteShowExtractorAgent
from app.database import Base, SessionLocal, engine
from app.models import Artist, Concert

logfire.configure()
logfire.instrument_pydantic_ai()

Base.metadata.create_all(bind=engine)


def main():
    db = SessionLocal()
    artist_name = "Men I Trust"

    # Create the Artist if it doesn't exist
    try:
        existing_artist = db.query(Artist).filter_by(name=artist_name).first()
        if not existing_artist:
            new_artist = Artist(name=artist_name)
            db.add(new_artist)
            db.commit()
            logfire.info(f"Added artist '{artist_name}' to the database.")
        else:
            logfire.info(f"Artist '{artist_name}' already exists in the database.")
    except Exception as e:
        logfire.error(f"Error adding artist '{artist_name}' to the database: {e}")
    finally:
        db.close()

    # Extracting shows for the artist
    out = ArtistWebsiteShowExtractorAgent.run_sync("Men I Trust")

    if len(out.output) == 0:
        logfire.warning(f"No shows found for artist '{artist_name}'.")
        return

    # Adding the shows to the database
    db = SessionLocal()
    artist_db = db.query(Artist).filter_by(name=artist_name).first()
    try:
        for show_details in out.output:
            logfire.info(f"Extracted show details: {show_details}")

            concert = Concert(
                date=show_details.date,
                artist=artist_db,
                venue_id=None,  # Venue handling can be added later
            )
            db.add(concert)
            logfire.info(
                f"Added concert on {concert.date} for artist '{artist_name}' to the database."
            )

    finally:
        db.commit()
        db.close()

    __import__("ipdb").set_trace()


if __name__ == "__main__":
    main()
