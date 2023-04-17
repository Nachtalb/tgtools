import re
from typing import Iterable

from yarl import URL
from emoji import emojize


def tagify(tags: Iterable[str] | str) -> set[str]:
    """
    Convert a list of tags or a single tag (string) into a set of hashtag-like strings.

    If a tag starts with a digit, it is prefixed with an underscore.
    Non-alphanumeric characters (except for underscores) are replaced with underscores.
    The input can be either a single string or an iterable of strings.

    Args:
        tags (Iterable[str] | str): A single tag (string) or an iterable of tags (strings).

    Returns:
        set[str]: A set of hashtag-like strings.

    Examples:
        >>> tagify("hello")
        {"#hello"}

        >>> tagify(["hello", "world"])
        {"#hello", "#world"}

        >>> tagify("123")
        {"#_123"}

        >>> tagify(["hello", "123"])
        {"#hello", "#_123"}
    """
    if not tags:
        return set()

    if isinstance(tags, str):
        tags = [tags]

    # Replace spaces with underscores and join the tags
    tags = " ".join(map(lambda s: s.replace(" ", "_"), tags))

    # Replace non-alphanumeric characters (except for underscores) with underscores
    tags = re.sub(r"(?![_a-zA-Z0-9\s]).", "_", tags).split(" ")

    # Add a hashtag to each tag, and prefix tags starting with a digit with an underscore
    return {f"#_{tag}" if tag[0].isdigit() else f"#{tag}" for tag in filter(None, tags)}


def host_emoji(url: str | URL) -> str:
    """
    Return a matching emoji for various art hosting sites.

    Args:
        url (str | URL): The URL of the art hosting site.

    Returns:
        str: The matching emoji for the provided site.

    Examples:
        >>> host_emoji("https://twitter.com")
        '🐦'
        >>> host_emoji("https://artstation.com")
        '🎨'
        >>> host_emoji("https://danbooru.donmai.us")
        '📦'
        >>> host_emoji("https://pixiv.net")
        '🅿️'
    """
    url = URL(url)

    match url.host:
        case "twitter.com" | "www.twitter.com" | "pbs.twimg.com":
            return emojize(":bird:")
        case "artstation.com" | "www.artstation.com":
            return emojize(":art:")
        case "danbooru.donmai.us":
            return emojize(":package:")
        case "pixiv.net" | "www.pixiv.net" | "i.pximg.net":
            return emojize(":parking:")
        case "deviantart.com" | "www.deviantart.com" | "pre00.deviantart.net":
            return emojize(":pencil:")
        case "instagram.com" | "www.instagram.com" | "scontent.cdninstagram.com":
            return emojize(":camera:")
        case "tumblr.com" | "www.tumblr.com" | "assets.tumblr.com":
            return emojize(":woman_dancing:")
        case _:
            return emojize(":frame_with_picture:")
