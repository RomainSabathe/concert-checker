from datetime import datetime

from pydantic import BaseModel


class ArtistCreate(BaseModel):
    name: str


class VenueCreate(BaseModel):
    name: str
    city: str
    country: str | None
    country_code: str | None  # ISO 3166-1 alpha-2 country code


class ConcertCreate(BaseModel):
    date: datetime
    artist_id: int
    venue_id: int | None
