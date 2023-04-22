from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, PrivateAttr

from tgtools.api import HOSTS
from tgtools.models.booru_post import BooruPost, CommonInfo, TagsNotCategorised
from tgtools.models.file_summary import URLFileSummary
from tgtools.utils.urls.builder import URLTemplateBuilder

if TYPE_CHECKING:
    from tgtools.api.yandere import YandereApi


class YanderePost(BaseModel, TagsNotCategorised, CommonInfo, BooruPost):
    """
    A class representing a Yandere post.

    Attributes:
        actual_preview_height (int): The actual preview height in pixels.
        actual_preview_width (int): The actual preview width in pixels.
        approver_id (int | None): The ID of the approver, if any.
        author (str): The author of the post.
        change (int): The change number of the post.
        created_at (int): The post creation timestamp.
        creator_id (int): The ID of the creator.
        file_ext (str): The file extension.
        file_size (int): The file size in bytes.
        file_url (str): The URL of the file.
        frames (list): A list of frames, if any.
        frames_pending (list): A list of pending frames, if any.
        frames_pending_string (str): A string representation of pending frames.
        frames_string (str): A string representation of frames.
        has_children (bool): Indicates if the post has children.
        height (int): The image height in pixels.
        id (int): The post ID.
        is_held (bool): Indicates if the post is held.
        is_note_locked (bool): Indicates if the post is note locked.
        is_pending (bool): Indicates if the post is pending.
        is_rating_locked (bool): Indicates if the post is rating locked.
        is_shown_in_index (bool): Indicates if the post is shown in index.
        jpeg_file_size (int): The JPEG file size in bytes.
        jpeg_height (int): The JPEG height in pixels.
        jpeg_url (str): The URL of the JPEG file.
        jpeg_width (int): The JPEG width in pixels.
        last_commented_at (int): The timestamp of the last commented, if any.
        last_noted_at (int): The timestamp of the last note, if any.
        md5 (str): The MD5 hash of the post.
        parent_id (int | None): The ID of the parent post, if any.
        preview_height (int): The preview height in pixels.
        preview_url (str): The URL of the preview file.
        preview_width (int): The preview width in pixels.
        rating (str): The rating of the post.
        sample_file_size (int): The sample file size in bytes.
        sample_height (int): The sample height in pixels.
        sample_url (str): The URL of the sample file.
        sample_width (int): The sample width in pixels.
        score (int): The post score.
        source (str): The source of the post.
        status (str): The status of the post.
        tag_string (str): The tags of the post.
        updated_at (int): The post update timestamp.
        width (int): The image width in pixels.
    """

    actual_preview_height: int
    actual_preview_width: int
    approver_id: int | None
    author: str
    change: int
    created_at: int
    creator_id: int
    file_ext: str
    file_size: int
    file_url: str
    frames: list
    frames_pending: list
    frames_pending_string: str
    frames_string: str
    has_children: bool
    height: int
    id: int
    is_held: bool
    is_note_locked: bool
    is_pending: bool
    is_rating_locked: bool
    is_shown_in_index: bool
    jpeg_file_size: int
    jpeg_height: int
    jpeg_url: str
    jpeg_width: int
    last_commented_at: int
    last_noted_at: int
    md5: str
    parent_id: int | None
    preview_height: int
    preview_url: str
    preview_width: int
    rating: str
    sample_file_size: int
    sample_height: int
    sample_url: str
    sample_width: int
    score: int
    source: str
    status: str
    tag_string: str = Field(alias="tags")
    updated_at: int
    width: int

    _api: "YandereApi" = PrivateAttr()
    _post_url = URLTemplateBuilder(f"{HOSTS.yandere}/post/show/{{id}}")
    _file_summary: URLFileSummary | None = PrivateAttr(None)

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.

        Returns:
            str: The string representation of the object.
        """
        return f"<{self.__class__.__name__} id={self.id}>"

    def set_api(self, api: "YandereApi") -> None:
        """
        Sets the API instance.

        Args:
            api (YandereApi): The API instance.
        """
        self._api = api
        self._post_url = URLTemplateBuilder(f"{self._api.url}/post/show/{{id}}")

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

            if not self._file_summary.is_image:
                self._file_summary = URLFileSummary(
                    url=self.sample_url,
                    file_name=Path(self.filename),
                    size=self.sample_file_size,
                    height=self.sample_height,
                    width=self.sample_width,
                    download_method=self.download,  # pyright: ignore[reportGeneralTypeIssues]
                    iter_download_method=self.iter_download,  # pyright: ignore[reportGeneralTypeIssues]
                )
        return self._file_summary
