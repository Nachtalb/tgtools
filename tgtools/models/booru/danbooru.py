from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import PrivateAttr
from yarl import URL

from tgtools.models.booru.common import CommonPostInfo
from tgtools.models.summaries import DownloadableMedia

if TYPE_CHECKING:
    from tgtools.api.booru.danbooru import DanbooruApi


class DanbooruPost(CommonPostInfo):
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

    uploader_id: int
    approver_id: int | None

    pixiv_id: int | None

    large_file_url: str | None
    preview_file_url: str | None

    up_score: int
    down_score: int
    fav_count: int

    tag_string_general: str
    tag_string_artist: str
    tag_string_copyright: str
    tag_string_character: str
    tag_string_meta: str
    tag_count_general: int
    tag_count_artist: int
    tag_count_copyright: int
    tag_count_character: int
    tag_count_meta: int

    last_comment_bumped_at: datetime | None
    last_noted_at: datetime | None

    has_large: bool
    has_visible_children: bool
    has_active_children: bool

    is_banned: bool
    is_deleted: bool
    is_flagged: bool

    bit_flags: int

    _api: "DanbooruApi" = PrivateAttr()
    _file_summary: DownloadableMedia | None = PrivateAttr(None)
    _post_url_path = PrivateAttr("/posts/{{id}}")

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
    def best_file_url(self) -> str:
        """
        Get the best file URL of the post.

        Returns:
            str: The best file URL as a string.
        """
        return self.file_url if self.file_summary.file_ext != "zip" else (self.large_file_url or self.file_url)

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
    def file_summary(self) -> DownloadableMedia:
        """
        Get the file summary of the post.

        Returns:
            DanbooruFileSummary: The file summary as a DanbooruFileSummary object.
        """
        if not self._file_summary:
            self._file_summary = DownloadableMedia(
                url=self.file_url,
                filename=self.filename,
                size=self.file_size,
                height=self.height,
                width=self.width,
                download_method=self.download,
            )
            self._file_summary.url = URL(self.best_file_url)
        return self._file_summary

    @property
    def main_source(self) -> str | None:
        """
        Get the processed main source url

        Returns:
            str | None: The processed source, or None if there is no source
        """
        if self.pixiv_id:
            return f"https://www.pixiv.net/artworks/{self.pixiv_id}"
        return self.source
