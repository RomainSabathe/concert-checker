from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Artist(Base):
    __tablename__ = "artists"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    concerts = relationship("Concert", back_populates="artist")


class Venue(Base):
    __tablename__ = "venues"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    country_code = Column(String, nullable=False)


class Concert(Base):
    __tablename__ = "concerts"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)
    artist = relationship("Artist", back_populates="concerts")
    venue = relationship("Venue")
