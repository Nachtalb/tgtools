from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import root_validator

from tgtools.models.booru.base import BooruPost
from tgtools.models.booru.rating import RATING
from tgtools.models.file_summary import URLFileSummary


class CommonPostInfo(BooruPost):
    """
    A class providing post method implementations for common info found on Booru APIs.

    Attributes:
        id (int): The post ID.
        created_at (datetime): The post creation datetime.
        updated_at (datetime): The post update datetime.
        tag_string (str): The full tag string.
        rating (str | None): The rating of the post.
        parent_id (int | None): The ID of the parent post, if any.
        source (str): The source of the post.
        file_url (str): The URL of the file.
        file_ext (str): The file extension.
        file_size (int): The file size in bytes.
        width (int): The image width in pixels.
        height (int): The image height in pixels.
        score (int): The post score.
        has_children (bool): Indicates if the post has children.
        is_pending (bool): Indicates if the post is pending.
    """

    id: int

    created_at: datetime
    updated_at: datetime

    rating: str
    source: str | None
    score: int
    parent_id: int
    has_children: bool
    is_pending: bool

    tag_string: str

    width: int
    height: int

    md5: str | None

    file_size: int
    file_url: str
    file_ext: str

    @root_validator(pre=True)
    def handle_aliases(cls, values: dict[str, Any]) -> Any:
        if "image_width" in values:
            values["width"] = values.pop("image_width")

        if "image_height" in values:
            values["height"] = values.pop("image_height")

        if "tags" in values:
            values["tag_string"] = values.pop("tags")

        return values

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.

        Returns:
            str: The string representation of the object.
        """
        return f"<{self.__class__.__name__} id={self.id}>"

    @property
    def tags(self) -> set[str]:
        """
        Get all the tags of the post (excluding rating tags).

        Returns:
            set[str]: All the tags as a set of strings.
        """
        return set(self.tag_string.split())

    @property
    def is_bad(self) -> bool:
        """
        Check if the post is bad.

        Note: Yandere doesn't have hidden posts like other boorus, thus this is always False

        Returns:
            bool: True if the post is bad, False otherwise.
        """
        return False

    @property
    def rating_full(self) -> str | None:
        """
        Get the full named rating of the post.

        Returns:
            set[str]: The full rating strings.
        """
        return RATING.full(self.rating) if self.rating else None

    @property
    def rating_simple(self) -> str | None:
        """
        Get the simple named rating of the post.

        Without the "rating:" part.

        Returns:
            set[str]: The simple rating strings.
        """
        return RATING.simple(self.rating) if self.rating else None

    @property
    def best_file_url(self) -> str:
        """
        Get the best file URL of the post.

        Returns:
            str: The best file URL as a string.
        """
        return self.file_url

    @property
    def filename(self) -> str:
        """
        Get the filename of the post.

        Returns:
            str: The filename as a string.
        """
        return f"{self.id}.{self.file_ext}"

    @property
    def main_source(self) -> str | None:
        """
        Get the processed main source url

        Returns:
            str | None: The processed source, or None if there is no source
        """
        return self.source

    @property
    def file_summary(self) -> URLFileSummary:
        """
        Get the file summary of the post.

        Returns:
            URLFileSummary: The file summary as a DanbooruFileSummary object.
        """
        if not self._file_summary:
            self._file_summary = URLFileSummary(
                url=self.file_url,
                file_name=Path(self.filename),
                size=self.file_size,
                height=self.height,
                width=self.width,
                download_method=self.download,  # pyright: ignore[reportGeneralTypeIssues]
                iter_download_method=self.iter_download,  # pyright: ignore[reportGeneralTypeIssues]
            )

        return self._file_summary
