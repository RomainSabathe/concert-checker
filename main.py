import logfire

from agents.artist_website_finder import ArtistWebsiteShowExtractorAgent

logfire.configure()
logfire.instrument_pydantic_ai()


def main():
    out = ArtistWebsiteShowExtractorAgent.run_sync("Men I Trust")
    __import__("ipdb").set_trace()


if __name__ == "__main__":
    main()
