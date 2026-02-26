from fastapi import FastAPI
from sqladmin import Admin, ModelView

from concert_checker.app.database import Base, engine
from concert_checker.app.models import Artist, Concert, PageCache, Venue

Base.metadata.create_all(bind=engine)

app = FastAPI()
admin = Admin(app, engine)


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

    uvicorn.run(app, host="127.0.0.1", port=8000)
