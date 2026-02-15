from sqlalchemy.orm import Session

from app.models import Artist, Concert, Venue
from app.schemas import ArtistCreate, ArtistUpdate, ConcertCreate, VenueCreate

# TODO: add logging.


def get_or_create_artist(db: Session, artist_data: ArtistCreate) -> Artist:
    """Get an existing Artist by name or create a new one if it doesn't exist.

    Args:
        db (Session): The database session to use for the query and creation.
        name (str): The name of the artist to get or create.
        **kwargs: Additional fields to set when creating a new Artist.

    Returns:
        Artist: The existing or newly created Artist object.
    """
    artist = db.query(Artist).filter_by(name=artist_data.name).first()
    if not artist:
        artist = Artist(**artist_data.model_dump())
        db.add(artist)
        db.flush()

    return artist


def update_artist(db: Session, artist_data: ArtistUpdate) -> Artist:
    artist = db.query(Artist).filter_by(id=artist_data.id).first()
    if not artist:
        raise ValueError(f"Artist with id {artist_data.id} not found.")

    for key, value in artist_data.model_dump(exclude={"id"}).items():
        if value is None:
            continue
        setattr(artist, key, value)

    return artist


def get_or_create_venue(db: Session, venue_data: VenueCreate) -> Venue:
    """Get an existing Venue by name and city or create a new one if it doesn't exist.

    Args:
        db (Session): The database session to use for the query and creation.
        venue_data (VenueCreate): The data for the venue to get or create.

    Returns:
        Venue: The existing or newly created Venue object.
    """
    venue = (
        db.query(Venue).filter_by(name=venue_data.name, city=venue_data.city).first()
    )
    if not venue:
        venue = Venue(**venue_data.model_dump())
        db.add(venue)
        db.flush()

    return venue


def get_or_create_concert(db: Session, concert_data: ConcertCreate) -> Concert:
    """Get an existing Concert by date, artist_id, and venue_id or create a new one if it doesn't exist.

    Args:
        db (Session): The database session to use for the query and creation.
        concert_data (ConcertCreate): The data for the concert to get or create.

    Returns:
        Concert: The existing or newly created Concert object.
    """
    concert = (
        db.query(Concert)
        .filter_by(
            date=concert_data.date,
            artist_id=concert_data.artist_id,
            # No need to check the venue. We assume that an artist has only 1 show per day.
        )
        .first()
    )
    if not concert:
        concert = Concert(**concert_data.model_dump())
        db.add(concert)
        db.flush()

    return concert
