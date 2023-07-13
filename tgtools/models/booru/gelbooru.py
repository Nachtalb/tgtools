from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import PrivateAttr, model_validator
from telegram import PhotoSize

from tgtools.constants import GelbooruStyleVersion
from tgtools.models.booru.common import CommonPostInfo
from tgtools.models.summaries.downloadable import DownloadableMedia

if TYPE_CHECKING:
    from tgtools.api.booru.gelbooru import GelbooruApi


class GelbooruPost(CommonPostInfo):
    owner: str
    change: int
    creator_id: int

    directory: str

    has_comments: bool
    has_notes: bool
    post_locked: bool

    preview_url: str
    preview_height: int
    preview_width: int

    sample_height: int
    sample_url: str
    sample_width: int

    status: str
    title: str

    # Adjust values due to yet another wannabe custom booru api
    sample_file_size: int = 0
    file_size: int = 0
    file_ext: str = ""
    is_pending: bool = False
    created_at: datetime

    _api: "GelbooruApi" = PrivateAttr()

    _post_url_path = PrivateAttr(GelbooruStyleVersion.post_gui_path)
    _file_summary: DownloadableMedia | None = PrivateAttr(None)

    @model_validator(mode="before")
    @classmethod
    def handle_values(cls, values: dict[str, Any]) -> dict[str, Any]:
        if "file_ext" not in values:
            values["file_ext"] = Path(values["file_url"]).suffix.lstrip(".")

        values["created_at"] = datetime.strptime(values["created_at"], "%a %b %d %H:%M:%S %z %Y")
        values["updated_at"] = 0
        return values

    @property
    def file_summary(self) -> DownloadableMedia:
        """
        Get the file summary of the post.

        Returns:
            URLFileSummary: The file summary object.
        """
        if not self._file_summary:
            self._file_summary = super().file_summary
            if self._file_summary.telegram_type is not PhotoSize and self.sample_url:
                self._file_summary = DownloadableMedia(
                    url=self.sample_url,
                    filename=self.filename,
                    size=self.sample_file_size,
                    height=self.sample_height,
                    width=self.sample_width,
                    download_method=self.download,
                )
        return self._file_summary
