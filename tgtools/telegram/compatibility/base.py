from abc import ABCMeta, abstractmethod
from io import BytesIO
from typing import Awaitable, Type

from telegram import Document, PhotoSize, Video

from tgtools.models.file_summary import FileSummary, URLFileSummary

MediaSummary = FileSummary | URLFileSummary
MediaType = Type[PhotoSize] | Type[Video] | Type[Document] | None


class MediaCompatibility(metaclass=ABCMeta):
    """
    Abstract base class for media compatibility check and conversion with Telegram.

    Attributes:
        MAX_SIZE_URL (int): The maximum size of a file to be sent as a URL (20 MB).
        MAX_SIZE_UPLOAD (int): The maximum size of a file to be uploaded (50 MB).
    """

    MAX_SIZE_URL = 20_000_000
    MAX_SIZE_UPLOAD = 50_000_000

    def __init__(self, file: MediaSummary) -> None:
        """
        Initialize the MediaCompatibility object.

        Args:
            file (MediaSummary): The media file to be checked for compatibility.
        """
        self.file = file

    def url_to_file_summary(self, content: BytesIO) -> FileSummary:
        """
        Convert a URLFileSummary object into a FileSummary object.

        Args:
            content (BytesIO): The content of the file as a BytesIO object.

        Returns:
            FileSummary: The converted FileSummary object.
        """
        if isinstance(self.file, FileSummary):
            return self.file
        data = self.file.dict(exclude={"url", "download_method", "iter_download_method"})
        data["file"] = content
        return FileSummary.parse_obj(data)

    async def download(self) -> FileSummary:
        """
        Download the media file and return it as a FileSummary object.

        Returns:
            FileSummary: The downloaded media file as a FileSummary object.
        """
        if isinstance(self.file, URLFileSummary):
            return self.url_to_file_summary(await self.file.download_method())
        return self.file

    @abstractmethod
    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, MediaType]:
        """
        Make the media file compatible with Telegram by checking its size and converting it if necessary.

        Args:
            force_download (bool, optional): Force download the file even if it's already compatible. Defaults to False.

        Returns:
            tuple[MediaSummary | None, bool]: A tuple containing the converted media file (or None if not converted) and
                                              a boolean indicating if it has to be sent as a Telegram Document.
        """
        ...
