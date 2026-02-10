from utils import find_artist_website


def main():
    out1 = find_artist_website("Taylor Swift")
    out2 = find_artist_website("Glass Beams")
    out3 = find_artist_website("men i truts")
    __import__("ipdb").set_trace()


if __name__ == "__main__":
    main()
