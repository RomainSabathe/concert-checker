from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from common.dataclasses import ArtistShows


class Source(ABC):
    @abstractmethod
    def fetch_shows(self, db: Session) -> list[ArtistShows]:
        pass


class ArtistBoundSource(Source, ABC):
    artist_name: str

    def __init__(self, artist_name: str):
        self.artist_name = artist_name

    @abstractmethod
    def resolve(self, db: Session):
        """Resolve dependencies for the source (base url, etc.)"""
        pass
