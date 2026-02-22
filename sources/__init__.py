from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from common.dataclasses import ShowDetails


class ArtistBoundSource(ABC):
    def __init__(self, artist_name: str):
        self.artist_name: str = artist_name

    @abstractmethod
    def resolve(self, db: Session):
        """Resolve dependencies for the source (base url, etc.)"""
        pass

    @abstractmethod
    def fetch_shows(self, db: Session) -> list[ShowDetails]:
        pass
