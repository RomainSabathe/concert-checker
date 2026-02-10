from agents import ArtistWebsiteFinderAgent


def find_artist_website(artist_name: str) -> str:
    """Find the official website of a music artist.

    Args:
        artist_name (str): The name of the artist.

    Returns:
        ArtistWebsite: An object containing the URL of the artist's official website.
    """
    response = ArtistWebsiteFinderAgent.run_sync(
        f"What is the official website of the artist '{artist_name}'?"
    )
    return response.output.url
