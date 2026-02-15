import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Artist(Base):
    __tablename__ = "artists"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    concerts: Mapped[list["Concert"]] = relationship(back_populates="artist")

    website_base_url: Mapped[str | None] = mapped_column()
    songkick_url: Mapped[str | None] = mapped_column()


class Venue(Base):
    __tablename__ = "venues"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    state: Mapped[str | None] = mapped_column()
    country: Mapped[str | None] = mapped_column()
    country_code: Mapped[str | None] = mapped_column()


class Concert(Base):
    __tablename__ = "concerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO: have `date` and `time` as separate fields to avoid situation where we
    # compare a datetime with a date.
    date: Mapped[datetime.date] = mapped_column()
    city: Mapped[str] = mapped_column()
    country: Mapped[str | None] = mapped_column()
    country_code: Mapped[str | None] = mapped_column()
    source_url: Mapped[str] = (
        mapped_column()
    )  # URL of the page where the show details were found

    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"))
    venue_id: Mapped[int | None] = mapped_column(ForeignKey("venues.id"))
    artist: Mapped["Artist"] = relationship(back_populates="concerts")
    venue: Mapped["Venue | None"] = relationship()


class PageCache(Base):
    __tablename__ = "page_caches"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(unique=True)
    content_hash: Mapped[str | None] = mapped_column()
    last_fetched_at: Mapped[datetime.datetime | None] = mapped_column()
    last_updated_at: Mapped[datetime.datetime | None] = mapped_column()
