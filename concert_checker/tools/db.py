from pydantic_ai import RunContext

from concert_checker.app.crud import get_or_create_artist, search_artists_by_name
from concert_checker.app.schemas import ArtistCreate
from concert_checker.common.dataclasses import AgentDependency


async def list_artists_in_db(
    ctx: RunContext[AgentDependency], name_query: str
) -> list[str]:
    """Search for existing artists in the database by name.

    Performs a case-insensitive partial match. Use this to check if an artist
    already exists before creating a new entry, and to get the exact stored
    name for consistency.

    Args:
        name_query: The artist name (or partial name) to search for.

    Returns:
        A list of matching artist names from the database.
    """
    db = ctx.deps.db

    artists = search_artists_by_name(db, name_query)
    return [artist.name for artist in artists]


async def add_artist_to_db(ctx: RunContext[AgentDependency], artist_name: str) -> bool:
    """Add a new artist to the database.

    Use this ONLY and EXCLUSIVELY after running the `list_artists_in_db` tool to verify
    that the artist didn't already exist.

    If the artist already exists (exact match via list_artists_in_db), no
    duplicate is created and the function returns False.

    Args:
        artist_name: The name of the artist to add.

    Returns:
        True if the artist was newly created, False if it already existed.
    """
    db = ctx.deps.db

    if artist_name in await list_artists_in_db(ctx, artist_name):
        # The artist is already in the db
        return False

    _ = get_or_create_artist(db, ArtistCreate(name=artist_name))
    return True
