import re
from typing import Iterable


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
