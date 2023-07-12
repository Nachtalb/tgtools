from abc import ABCMeta, abstractmethod
from typing import Optional, Union

from tgtools.models.summaries import Downloadable, FileSummary, ToDownload
from tgtools.utils.types import TELEGRAM_FILES

InputFileType = Union[FileSummary, ToDownload, Downloadable]
OutputFileType = Union[FileSummary, Downloadable]


class MediaCompatibility(metaclass=ABCMeta):
    """
    Abstract base class for media compatibility check and conversion with Telegram.

    Attributes:
        MAX_SIZE_URL (int): The maximum size of a file to be sent as a URL (20 MB).
        MAX_SIZE_UPLOAD (int): The maximum size of a file to be uploaded (50 MB).
    """

    MAX_SIZE_URL = 20_000_000
    MAX_SIZE_UPLOAD = 50_000_000

    def __init__(self, file: InputFileType) -> None:
        """
        Initialize the MediaCompatibility object.

        Args:
            file (FileSummary): The media file to be checked for compatibility.
        """
        self.file = file

    async def download_if_needed(self, force_download: bool = False) -> OutputFileType:
        """
        Check wether the file has to be downloaded and download it

        Args:
            force_download (bool, optional): Force download the file (defaults to False)

        Returns:
            A FileSummary or a Downloadable depending on wether the file had to be downloaded or not
        """
        force_download = force_download or (
            hasattr(self.file.size, "size") and self.file.size > self.MAX_SIZE_URL < self.MAX_SIZE_UPLOAD
        )
        if (isinstance(self.file, Downloadable) and force_download) or isinstance(self.file, ToDownload):
            return await self.file.download_to_summary()
        return self.file

    @abstractmethod
    async def make_compatible(self, force_download: bool = False) -> tuple[Optional[OutputFileType], TELEGRAM_FILES]:
        """
        Make the media file compatible with Telegram by checking its size and converting it if necessary.

        Args:
            force_download (bool, optional): Force download the file even if it's already compatible. Defaults to False.

        Returns:
            tuple[Optional[FileType], bool]: A tuple containing the converted media file (or None if not converted) and
                                              a boolean indicating if it has to be sent as a Telegram Document.
        """
        ...
