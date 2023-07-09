from io import BytesIO
from pathlib import Path
from typing import AsyncGenerator, Awaitable, Callable

from pydantic import BaseModel


class Summary(BaseModel):
    """
    A summary of a file containing information such as file name, size, dimensions, and download method.

    Attributes:
        file_name (Path): The file name with its extension.
        size (int): The file size in bytes.
        height (int, optional): The height of the image or video. (Defaults to -1)
        width (int, optional): The width of the image or video. (Defaults to -1)
    """

    file_name: Path
    size: int
    height: int = -1
    width: int = -1

    @property
    def ratio_wh(self) -> float:
        """The width-to-height ratio."""
        return self.width / self.height

    @property
    def ratio_hw(self) -> float:
        """The height-to-width ratio."""
        return self.height / self.width

    @property
    def file_ext(self) -> str:
        """The file extension, without the leading period."""
        return self.file_name.suffix[1:]

    @property
    def is_image(self) -> bool:
        """Whether the file is an image."""
        return self.file_ext in ["jpg", "jpeg", "png", "webp"]

    @property
    def is_gif(self) -> bool:
        """Whether the file is a GIF."""
        return self.file_ext == "gif"

    @property
    def is_video(self) -> bool:
        """Whether the file is a video."""
        return self.file_ext in ["mp4", "webm", "mkv"]


class FileSummary(Summary):
    """
    A summary of a file containing the file itself, in addition to the attributes of the Summary class.

    Attributes:
        file (BytesIO): The file as a BytesIO object.
    """

    file: BytesIO

    class Config:
        arbitrary_types_allowed = True


class URLFileSummary(Summary):
    """
    A summary of a file containing a URL, in addition to the attributes of the Summary class.

    Attributes:
        url (str): The URL of the file.
        download_method (Callable): A callable function to download the file.
        iter_download_method (Callable): A callable function to download the file in chunks
            (for improved asynchronousy)
    """

    url: str
    download_method: Callable[..., Awaitable[BytesIO]]
    iter_download_method: Callable[..., AsyncGenerator[BytesIO, None]]
