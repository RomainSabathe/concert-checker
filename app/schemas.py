from datetime import date

from pydantic import BaseModel


class ArtistCreate(BaseModel):
    name: str
    website_base_url: str | None = None
    songkick_url: str | None = None


class ArtistGet(BaseModel):
    name: str
    website_base_url: str | None = None
    songkick_url: str | None = None


class ArtistUpdate(BaseModel):
    id: int
    name: str | None = None
    website_base_url: str | None = None
    songkick_url: str | None = None


class VenueCreate(BaseModel):
    name: str
    city: str
    state: str | None = None
    country: str | None = None
    country_code: str | None = None  # ISO 3166-1 alpha-2 country code


class ConcertCreate(BaseModel):
    date: date
    artist_id: int
    venue_id: int | None = None
