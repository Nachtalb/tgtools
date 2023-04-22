from emoji import emojize
from yarl import URL

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
    "yandere": {
        "name": "Yandere",
        "emoji": ":sparkles:",
        "urls": ["yande.re", "files.yande.re"],
    },
    "fanbox": {
        "name": "Fanbox",
        "emoji": ":P_button:",
        "urls": ["fanbox.cc", "www.fanbox.ce"],
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
        if name and name[:4] == "Www.":
            name = name[4:].capitalize()
        emoji = emojize(fallback)

    return f"{emoji} {name}" if with_emoji else name
