from typing import Awaitable, Callable, Optional, Union

from aiopath import AsyncPath
from telegram import Document
from yarl import URL

from tgtools.utils.types import FileOrPath, FilePath

from .downloadable import Downloadable
from .file_summary import FileSummary, MediaFileSummary

__all__ = ["ToDownload"]


class ToDownload(Downloadable):
    """
    A file that still needs to be downloaded

    Attributes:
        url (URL): The URL of the file
        download_method (Callable[..., Awaitable[FileOrPath]]): The download method taking the url as a parameter
        filename (str): The filename of the file, either taken from the `filename` argument or the name in the URL

    Args:
        url (Union[str, URL]): The url of the file
        download_method (Callable[..., Awaitable[FileOrPath]]): The download method taking the url as a parameter
        filename (FilePath, optional): The filename either as str, Path or AsyncPath
    """

    def __init__(
        self,
        url: Union[str, URL],
        download_method: Callable[..., Awaitable[FileOrPath]],
        filename: Optional[FilePath] = None,
    ) -> None:
        self.url = URL(url)
        self.download_method = download_method
        self.filename = AsyncPath(filename or "").name or self.url.name

    async def download_to_summary(self) -> FileSummary:
        """
        Download the file and create a `FileSummary`
        """
        file: FileOrPath = await self.download_method(self.url)

        if self.telegram_type is Document:
            return await FileSummary.from_file(file=file, filename=self.filename)
        return await MediaFileSummary.from_file(file=file, filename=self.filename)
