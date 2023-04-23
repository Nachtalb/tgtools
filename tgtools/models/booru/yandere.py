from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import PrivateAttr

from tgtools.api.booru.constants import YandereStyleVersion
from tgtools.models.booru.common import CommonPostInfo
from tgtools.models.file_summary import URLFileSummary

if TYPE_CHECKING:
    from tgtools.api.booru.v1 import V1Api


class YanderePost(CommonPostInfo):
    """
    A class representing a Yandere post.

    Attributes:
        actual_preview_height (int): The actual preview height in pixels.
        actual_preview_width (int): The actual preview width in pixels.
        approver_id (int | None): The ID of the approver, if any.
        author (str): The author of the post.
        change (int): The change number of the post.
        created_at (datetime): The post creation timestamp.
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
        updated_at (datetime): The post update timestamp.
        width (int): The image width in pixels.
    """

    approver_id: int | None
    author: str
    change: int
    creator_id: int

    frames: list
    frames_pending: list
    frames_pending_string: str
    frames_string: str

    is_held: bool
    is_note_locked: bool
    is_rating_locked: bool
    is_shown_in_index: bool

    last_commented_at: int
    last_noted_at: int

    jpeg_file_size: int
    jpeg_height: int
    jpeg_url: str
    jpeg_width: int

    preview_url: str
    preview_height: int
    preview_width: int
    actual_preview_height: int
    actual_preview_width: int

    sample_file_size: int
    sample_height: int
    sample_url: str
    sample_width: int

    status: str

    _api: "V1Api[YanderePost]" = PrivateAttr()
    _post_url_path = PrivateAttr(YandereStyleVersion.post_gui_path)
    _file_summary: URLFileSummary | None = PrivateAttr(None)

    @property
    def file_summary(self) -> URLFileSummary:
        """
        Get the file summary of the post.

        Returns:
            URLFileSummary: The file summary object.
        """
        if not self._file_summary:
            self._file_summary = super().file_summary
            if not self._file_summary.is_image and self.sample_url:
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
