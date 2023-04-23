from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import PrivateAttr

from tgtools.constants import GelbooruStyleVersion
from tgtools.models.booru.common import CommonPostInfo
from tgtools.models.file_summary import URLFileSummary

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

    sample_file_size: int
    sample_height: int
    sample_url: str
    sample_width: int

    status: str
    title: str

    _api: "GelbooruApi" = PrivateAttr()

    _post_url_path = PrivateAttr(GelbooruStyleVersion.post_gui_path)
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
