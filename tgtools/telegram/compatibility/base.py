from abc import ABCMeta, abstractmethod
from io import BytesIO
from typing import Union

from tgtools.models.file_summary import FileSummary, URLFileSummary

MediaSummary = Union[FileSummary, URLFileSummary]


class MediaCompatibility(metaclass=ABCMeta):
    MAX_SIZE_URL = 20_000_000
    MAX_SIZE_UPLOAD = 50_000_000

    def __init__(self, file: MediaSummary) -> None:
        self.file = file

    def url_to_file_summary(self, content: BytesIO) -> FileSummary:
        if isinstance(self.file, FileSummary):
            return self.file
        data = self.file.dict(exclude={"url"})
        data["file"] = content
        return FileSummary.parse_obj(data)

    async def download(self) -> FileSummary:
        return self.url_to_file_summary(await self.file.download_method())

    @abstractmethod
    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, bool]:
        ...
