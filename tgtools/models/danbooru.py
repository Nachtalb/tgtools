from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator

from pydantic import BaseModel, PrivateAttr

if TYPE_CHECKING:
    from tgtools.api.danbooru import DanbooruApi

from .file_summary import URLFileSummary


class DanbooruFileSummary(URLFileSummary):
    """
    A class representing a summary of a Danbooru file.

    Attributes:
        is_gif (bool): Indicates if the file is a gif.
    """

    @property
    def is_gif(self) -> bool:
        """
        Checks if the file is a gif.

        Returns:
            bool: True if the file is a gif, False otherwise.
        """
        return self.file_ext == "zip"


class RATING:
    """
    A utility class for handling Danbooru rating levels and their corresponding strings.

    Attributes:
        general (str): The general rating string.
        sensitive (str): The sensitive rating string.
        questionable (str): The questionable rating string.
        explicit (str): The explicit rating string.
        levels (dict[str, int]): A dictionary mapping rating strings to their corresponding integer levels.
        full_name_map (dict[str, str]): A dictionary mapping rating all variations of
                                        rating strings to their full name.
    """

    general = "rating:general"
    sensitive = "rating:sensitive"
    questionable = "rating:questionable"
    explicit = "rating:explicit"

    levels = {
        "rating:general": 0,
        "rating:sensitive": 1,
        "rating:questionable": 2,
        "rating:explicit": 3,
    }

    full_name_map = {
        "g": general,
        "general": general,
        "rating:general": general,
        "s": sensitive,
        "sensitive": sensitive,
        "rating:sensitive": sensitive,
        "q": questionable,
        "questionable": questionable,
        "rating:questionable": questionable,
        "e": explicit,
        "explicit": explicit,
        "rating:explicit": explicit,
    }

    @staticmethod
    def level(rating: str) -> int:
        """
        Get the integer level of a given rating.

        Args:
            rating (str): The rating string.

        Returns:
            int: The corresponding integer level of the rating.

        Examples:
            >>> RATING.level("g")
            0

            >>> RATING.level("sensitive")
            1

            >>> RATING.level("rating:explicit")
            3
        """
        return RATING.levels[RATING.full(rating)]

    @staticmethod
    def simple(rating: str) -> str:
        """
        Get the simple rating string from a given rating.

        Without the "rating:" part.

        Args:
            rating (str): The rating string.

        Returns:
            str: The simple rating string.

        Examples:
            >>> RATING.simple("g")
            "general"

            >>> RATING.simple("e")
            "explicit"
        """
        return RATING.full(rating).split(":")[-1]

    @staticmethod
    def full(rating: str) -> str:
        """
        Get the full rating string from a given rating.

        Args:
            rating (str): The rating string.

        Returns:
            str: The full rating string.

        Examples:
            >>> RATING.simple("g")
            "rating:general"

            >>> RATING.simple("rating:sensitive")
            "rating:sensitive"

            >>> RATING.simple("explicit")
            "rating:explicit"
        """
        return RATING.full_name_map[rating]


class Post(BaseModel):
    """
    A class representing a Danbooru post.

    Attributes:
        id (int): The post ID.
        created_at (datetime): The post creation datetime.
        updated_at (datetime): The post update datetime.
        uploader_id (int): The ID of the uploader.
        approver_id (int | None): The ID of the approver, if any.
        tag_string (str): The full tag string.
        tag_string_general (str): The general tag string.
        tag_string_artist (str): The artist tag string.
        tag_string_copyright (str): The copyright tag string.
        tag_string_character (str): The character tag string.
        tag_string_meta (str): The meta tag string.
        rating (str | None): The rating of the post.
        parent_id (int | None): The ID of the parent post, if any.
        pixiv_id (int | None): The ID of the post on Pixiv, if any.
        source (str): The source of the post.
        md5 (str | None): The MD5 hash of the post.
        file_url (str): The URL of the file.
        large_file_url (str | None): The URL of the large file, if any.
        preview_file_url (str | None): The URL of the preview file, if any.
        file_ext (str): The file extension.
        file_size (int): The file size in bytes.
        image_width (int): The image width in pixels.
        image_height (int): The image height in pixels.
        score (int): The post score.
        up_score (int): The up score of the post.
        down_score (int): The down score of the post.
        fav_count (int): The number of favourites.
        tag_count_general (int): The count of general tags.
        tag_count_artist (int): The count of artist tags.
        tag_count_copyright (int): The count of copyright tags.
        tag_count_character (int): The count of character tags.
        tag_count_meta (int): The count of meta tags.
        last_comment_bumped_at (datetime | None): The datetime of the last bumped comment, if any.
        last_noted_at (datetime | None): The datetime of the last note, if any.
        has_large (bool): Indicates if the post has a large file.
        has_children (bool): Indicates if the post has children.
        has_visible_children (bool): Indicates if the post has visible children.
        has_active_children (bool): Indicates if the post has active children.
        is_banned (bool): Indicates if the post is banned.
        is_deleted (bool): Indicates if the post is deleted.
        is_flagged (bool): Indicates if the post is flagged.
        is_pending (bool): Indicates if the post is pending.
        bit_flags (int): The bit flags of the post.
    """

    id: int
    created_at: datetime
    updated_at: datetime
    uploader_id: int
    approver_id: int | None
    tag_string: str
    tag_string_general: str
    tag_string_artist: str
    tag_string_copyright: str
    tag_string_character: str
    tag_string_meta: str
    rating: str | None
    parent_id: int | None
    pixiv_id: int | None
    source: str
    md5: str | None
    file_url: str
    large_file_url: str | None
    preview_file_url: str | None
    file_ext: str
    file_size: int
    image_width: int
    image_height: int
    score: int
    up_score: int
    down_score: int
    fav_count: int
    tag_count_general: int
    tag_count_artist: int
    tag_count_copyright: int
    tag_count_character: int
    tag_count_meta: int
    last_comment_bumped_at: datetime | None
    last_noted_at: datetime | None
    has_large: bool
    has_children: bool
    has_visible_children: bool
    has_active_children: bool
    is_banned: bool
    is_deleted: bool
    is_flagged: bool
    is_pending: bool
    bit_flags: int

    _api: "DanbooruApi" = PrivateAttr()
    _file_summary: DanbooruFileSummary | None = PrivateAttr(None)

    def __repr__(self) -> str:
        return f"<Post id={self.id}>"

    async def download(self, out: Path | None = None) -> BytesIO | Path:
        """
        Download the post file.

        Args:
            out (Path | None): The output path for the downloaded file, if any.

        Returns:
            BytesIO | Path: The downloaded file as a BytesIO object if no output path is provided, otherwise the output path.
        """
        return await self._api.download(self.best_file_url, out)

    async def iter_download(
        self, out: Path | None = None, chunk_size: int = 1024 * 1024
    ) -> AsyncGenerator[BytesIO | Path, None]:
        """
        Download the post file in chunks.

        Args:
            out (Path | None): The output path for the downloaded file, if any.
            chunk_size (int, optional): The size of the chunks to download. Defaults to 1024 * 1024.

        Yields:
            AsyncGenerator[BytesIO | Path, None]: The downloaded file as a BytesIO object if no output path is provided, otherwise the output path, in chunks.
        """
        async for item in self._api.iter_download(self.best_file_url, out, chunk_size):
            yield item

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
    def tags_rating(self) -> set[str]:
        """
        Get the full named rating tags of the post.

        Returns:
            set[str]: The rating tags as a set of strings.
        """
        return {self.rating_full} if self.rating_full else set()

    @property
    def simple_tags_rating(self) -> set[str]:
        """
        Get the simple named rating tags of the post.

        Returns:
            set[str]: The rating tags as a set of strings.
        """
        return {self.rating_simple} if self.rating_simple else set()

    @property
    def tags(self) -> set[str]:
        """
        Get all the tags of the post (excluding rating tags).

        Returns:
            set[str]: All the tags as a set of strings.
        """
        return set(self.tag_string.split())

    @property
    def tags_with_rating(self) -> set[str]:
        """
        Get all the tags of the post, including rating tags.

        Returns:
            set[str]: All the tags with rating as a set of strings.
        """
        return self.tags & self.tags_rating

    @property
    def tags_general(self) -> set[str]:
        """
        Get the general tags of the post.

        Returns:
            set[str]: The general tags as a set of strings.
        """
        return set(self.tag_string_general.split())

    @property
    def tags_artist(self) -> set[str]:
        """
        Get the artist tags of the post.

        Returns:
            set[str]: The artist tags as a set of strings.
        """
        return set(self.tag_string_artist.split())

    @property
    def tags_copyright(self) -> set[str]:
        """
        Get the copyright tags of the post.

        Returns:
            set[str]: The copyright tags as a set of strings.
        """
        return set(self.tag_string_copyright.split())

    @property
    def tags_character(self) -> set[str]:
        """
        Get the character tags of the post.

        Returns:
            set[str]: The character tags as a set of strings.
        """
        return set(self.tag_string_character.split())

    @property
    def tags_meta(self) -> set[str]:
        """
        Get the meta tags of the post.

        Returns:
            set[str]: The meta tags as a set of strings.
        """
        return set(self.tag_string_meta.split())

    @property
    def url(self) -> str:
        """
        Get the gui URL of the post.

        Returns:
            str: The post URL as a string.
        """
        return f"https://danbooru.donmai.us/posts/{self.id}"

    @property
    def best_file_url(self) -> str:
        """
        Get the best file URL of the post.

        Returns:
            str: The best file URL as a string.
        """
        return self.file_url if not self.file_summary.is_gif else (self.large_file_url or self.file_url)

    @property
    def is_bad(self) -> bool:
        """
        Check if the post is bad.

        A post is considered bad if it is banned or if it is deleted and has a low up score compared to its down score
        (up score / abs(down score) < 2).

        Returns:
            bool: True if the post is bad, False otherwise.
        """
        return self.is_banned or (self.is_deleted and ((self.up_score or 1) / abs(self.down_score or 1) < 2))

    @property
    def filename(self) -> str:
        """
        Get the filename of the post.

        Returns:
            str: The filename as a string.
        """
        return f"{self.id}.{self.file_ext}"

    @property
    def file_summary(self) -> DanbooruFileSummary:
        """
        Get the file summary of the post.

        Returns:
            DanbooruFileSummary: The file summary as a DanbooruFileSummary object.
        """
        if not self._file_summary:
            self._file_summary = DanbooruFileSummary(
                url=self.file_url,
                file_name=Path(self.filename),
                size=self.file_size,
                height=self.image_height,
                width=self.image_width,
                download_method=self.download,  # pyright: ignore[reportGeneralTypeIssues]
                iter_download_method=self.iter_download,  # pyright: ignore[reportGeneralTypeIssues]
            )
            self._file_summary.url = self.best_file_url
        return self._file_summary
