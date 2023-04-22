import re
from random import choices
from typing import Iterable

from emoji import emojize
from yarl import URL


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
        >>> tagify("(^.^)")
        set()

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
    tags = re.sub(r"\b_+\b", "", re.sub(r"(?![_a-zA-Z0-9\s]).", "_", tags)).split(" ")

    # Add a hashtag to each tag, and prefix tags starting with a digit with an underscore
    return {f"#_{tag}" if tag[0].isdigit() else f"#{tag}" for tag in filter(None, tags)}


def tagified_string(tags: Iterable[str], limit: int = 0) -> str:
    """
    Create a string of hashtag-like strings from a list of tags.

    Args:
        tags (Iterable[str]): An iterable of tags (strings).
        limit (int, optional): The maximum number of tags to include in the output string. Defaults to 0 (no limit).

    Returns:
        str: A string of hashtag-like strings separated by commas.

    Examples:
        >>> tagified_string(["hello", "world"])
        "#hello, #world"

        >>> tagified_string(["hello", "world"], limit=1)
        "#hello" or "#world"
    """
    if limit:
        tags = choices(list(tags), k=limit)
    return ", ".join(tagify(tags))


HOST_MAP = {
    "twitter": {
        "name": "Twitter",
        "emoji": ":bird:",
        "urls": ["twitter.com", "www.twitter.com", "pbs.twimg.com"],
    },
    "artstation": {
        "name": "ArtStation",
        "emoji": ":art:",
        "urls": ["artstation.com", "www.artstation.com"],
    },
    "danbooru": {
        "name": "Danbooru",
        "emoji": ":package:",
        "urls": ["danbooru.donmai.us"],
    },
    "pixiv": {
        "name": "Pixiv",
        "emoji": ":P_button:",
        "urls": ["pixiv.net", "www.pixiv.net", "i.pximg.net"],
    },
    "deviantart": {
        "name": "DeviantArt",
        "emoji": ":pencil:",
        "urls": ["deviantart.com", "www.deviantart.com", "pre00.deviantart.net"],
    },
    "instagram": {
        "name": "Instagram",
        "emoji": ":camera:",
        "urls": ["instagram.com", "www.instagram.com", "scontent.cdninstagram.com"],
    },
    "tumblr": {
        "name": "Tumblr",
        "emoji": ":woman_dancing:",
        "urls": ["tumblr.com", "www.tumblr.com", "assets.tumblr.com"],
    },
}

URL_MAP = {url: key for key, data in HOST_MAP.items() for url in data["urls"]}

FALLBACK_EMOJIS = {
    "globe": ":globe_with_meridians:",
    "picture": ":framed_picture:",
}


def host_emoji(url: str | URL, fallback: str = FALLBACK_EMOJIS["picture"]) -> str:
    """
    Return a matching emoji for various art hosting sites.

    Args:
        url (str | URL): The URL of the art hosting site.
        fallback (str): The emoji to use as fallback if no host matched (default "🖼️")

    Returns:
        str: The matching emoji for the provided site.

    Examples:
        >>> host_emoji("https://twitter.com")
        '🐦'
        >>> host_emoji("https://artstation.com")
        '🎨'
        >>> host_emoji("https://pixiv.net")
        '🅿️'
    """
    url = URL(url)
    site_key = URL_MAP.get(url.host)
    return emojize(HOST_MAP[site_key]["emoji"]) if site_key else emojize(fallback)


def host_name(url: str | URL, with_emoji: bool = False, fallback: str = FALLBACK_EMOJIS["picture"]) -> str:
    """
    Return a readable name for various art hosting sites with an optional emoji.

    Args:
        url (str | URL): The URL of the art hosting site.
        with_emoji (bool, optional): Include the emoji at the start of the name. Defaults to False.
        fallback (str): The emoji to use as fallback if no host matched (default "🖼️")

    Returns:
        str: The readable name of the provided site, with an optional emoji at the start.

    Examples:
        >>> host_name("https://twitter.com")
        'Twitter'
        >>> host_name("https://artstation.com", with_emoji=True)
        '🎨 ArtStation'
        >>> host_name("https://pixiv.net", with_emoji=True)
        '🅿️ Pixiv'
    """
    url = URL(url)
    site_key = URL_MAP.get(url.host)

    if site_key:
        name = HOST_MAP[site_key]["name"]
        emoji = emojize(HOST_MAP[site_key]["emoji"]) if with_emoji else fallback
    else:
        name = url.host.capitalize() if url.host else str(url)
        emoji = emojize(fallback)

    return f"{emoji} {name}" if with_emoji else name
