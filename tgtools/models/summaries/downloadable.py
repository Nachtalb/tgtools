from typing import Awaitable, Callable, Optional, Union

from aiopath import AsyncPath
from telegram import Document
from yarl import URL

from tgtools.utils.types import FileOrPath, FilePath

from .file_summary import FileExtMixin, FileSummary, MediaFileSummary, MediaMixin

__all__ = ["Downloadable", "DownloadableMedia"]


class Downloadable(FileExtMixin):
    """
    A file that may be downloaded

    If we already have all the information such as size, we may not need to download the file. And can Telegram do it
    instead.

    Attributes:
        filename (str): The filename of the file, either taken from the `filename` argument or the name in the URL
        size (int): The physical size on the disk in bytes.
        url (URL): The URL of the file
        download_method (Callable[..., Awaitable[FileOrPath]]): The download method taking the url as a parameter

    Args:
        url (Union[str, URL]): The url of the file
        size (int): The physical size on the disk in bytes.
        download_method (Callable[..., Awaitable[FileOrPath]]): The download method taking the url as a parameter
        filename (FilePath, optional): The filename either as str, Path or AsyncPath

    """

    def __init__(
        self,
        url: Union[str, URL],
        size: int,
        download_method: Callable[..., Awaitable[FileOrPath]],
        filename: Optional[FilePath] = None,
    ) -> None:
        self.url = URL(url)
        self.filename = AsyncPath(filename or "").name or self.url.name
        self.download_method = download_method
        self.size = size

    async def download_to_summary(self) -> FileSummary:
        """
        Download the file and create a `FileSummary`
        """
        file: FileOrPath = await self.download_method(self.url)

        summary = FileSummary(
            filename=self.filename,
            file=file,
            size=self.size,
        )

        if self.telegram_type is Document:
            return summary
        return await MediaFileSummary.from_file_summary(summary=summary)

    async def as_common(self) -> str:
        """
        Return the content of the file in a commonly used format
        """
        return str(self.url)


class DownloadableMedia(Downloadable, MediaMixin):
    """
    A media file that may be downloaded.

    If we already have all the information such as size, we may not need to download the file. And can Telegram do it
    instead.

    Attributes:
        filename (str): The filename of the file, either taken from the `filename` argument or the name in the URL
        size (int): The physical size on the disk in bytes.
        url (URL): The URL of the file
        download_method (Callable[..., Awaitable[FileOrPath]]): The download method taking the url as a parameter

    Args:
        url (Union[str, URL]): The url of the file
        size (int): The physical size on the disk in bytes.
        download_method (Callable[..., Awaitable[FileOrPath]]): The download method taking the url as a parameter
        filename (FilePath, optional): The filename either as str, Path or AsyncPath

    """

    def __init__(
        self,
        url: Union[str, URL],
        size: int,
        width: int,
        height: int,
        download_method: Callable[..., Awaitable[FileOrPath]],
        filename: Optional[FilePath] = None,
    ) -> None:
        self.filename = AsyncPath(filename or "").name or self.url.name
        self.url = URL(url)
        self.download_method = download_method
        self.width = width
        self.height = height
        self.size = size

    async def download_to_summary(self) -> FileSummary:
        """
        Download the file and create a `MediaFileSummary`
        """
        file: FileOrPath = await self.download_method(self.url)

        return MediaFileSummary(
            filename=self.filename,
            file=file,
            size=self.size,
            width=self.width,
            height=self.height,
        )
