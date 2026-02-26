import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqladmin import Admin, ModelView
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from concert_checker.app.database import Base, SessionLocal, engine
from concert_checker.app.models import Artist, Concert, PageCache, Venue

Base.metadata.create_all(bind=engine)

app = FastAPI()
admin = Admin(app, engine)


@app.get("/", response_class=HTMLResponse)
def landing_page() -> str:
    with SessionLocal() as db:
        artists = db.scalars(
            select(Artist)
            .options(selectinload(Artist.concerts).selectinload(Concert.venue))
            .order_by(Artist.name)
        ).all()

    rows = ""
    for artist in artists:
        concerts = sorted(artist.concerts, key=lambda c: c.date)
        for i, concert in enumerate(concerts):
            artist_cell = (
                f"<td rowspan='{len(concerts)}'><strong>{artist.name}</strong></td>"
                if i == 0
                else ""
            )
            venue = concert.venue.name if concert.venue else ""
            location = ", ".join(filter(None, [concert.city, concert.country]))
            rows += (
                f"<tr>{artist_cell}"
                f"<td>{concert.date}</td>"
                f"<td>{venue}</td>"
                f"<td>{location}</td></tr>\n"
            )
        if not concerts:
            rows += f"<tr><td><strong>{artist.name}</strong></td><td colspan='3'><em>No concerts</em></td></tr>\n"

    return f"""<!DOCTYPE html>
<html>
<head><title>Concert Checker</title></head>
<body>
<h1>Concerts</h1>
<table border="1" cellpadding="4" cellspacing="0">
<tr><th>Artist</th><th>Date</th><th>Venue</th><th>Location</th></tr>
{rows}
</table>
</body>
</html>"""


class ArtistAdmin(ModelView, model=Artist):
    column_list = [Artist.id, Artist.name, Artist.website_base_url, Artist.songkick_url]
    column_searchable_list = [Artist.name]


class VenueAdmin(ModelView, model=Venue):
    column_list = [Venue.id, Venue.name, Venue.city, Venue.country]
    column_searchable_list = [Venue.name, Venue.city]


class ConcertAdmin(ModelView, model=Concert):
    column_list = [
        Concert.id,
        Concert.date,
        Concert.artist,
        Concert.venue,
        Concert.city,
        Concert.country,
        Concert.source_url,
    ]
    column_sortable_list = [Concert.date, Concert.city]
    column_default_sort = (Concert.date, True)


class PageCacheAdmin(ModelView, model=PageCache):
    column_list = [
        PageCache.id,
        PageCache.url,
        PageCache.last_fetched_at,
        PageCache.last_updated_at,
    ]


admin.add_view(ArtistAdmin)
admin.add_view(VenueAdmin)
admin.add_view(ConcertAdmin)
admin.add_view(PageCacheAdmin)


def serve():
    import uvicorn

    host = os.environ.get("UVICORN_HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=8000)
