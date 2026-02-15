from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Artist(Base):
    __tablename__ = "artists"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    concerts: Mapped[list["Concert"]] = relationship(back_populates="artist")


class Venue(Base):
    __tablename__ = "venues"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    country: Mapped[str | None] = mapped_column()
    country_code: Mapped[str | None] = mapped_column()


class Concert(Base):
    __tablename__ = "concerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column()
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"))
    venue_id: Mapped[int | None] = mapped_column(ForeignKey("venues.id"))
    artist: Mapped["Artist"] = relationship(back_populates="concerts")
    venue: Mapped["Venue | None"] = relationship()
