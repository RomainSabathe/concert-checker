from app.database import Base, SessionLocal, engine
from app.models import Artist, Concert, Venue  # noqa: F401

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    menitrust = Artist(name="Men I Trust")
    db.add(menitrust)
    db.commit()

    artists = db.query(Artist).all()
    for artist in artists:
        print(f"Artist: {artist.name}")

finally:
    db.close()
