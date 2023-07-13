from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Optional

from aiopath import AsyncPath
from PIL import Image
from telegram import Animation, Document, PhotoSize, Video

from tgtools.utils.file import ffprobe, read_file_like, seek
from tgtools.utils.types import GIF_TYPES, IMAGE_TYPES, TELEGRAM_FILES, VIDEO_TYPES, FileOrPath, FilePath

__all__ = ["FileSummary", "MediaFileSummary", "MediaMixin", "FileExtMixin"]


class FileExtMixin:
    filename: str

    @property
    def file_ext(self) -> str:
        """The file extension, without the leading period."""
        return Path(self.filename).suffix[1:]

    @property
    def telegram_type(self) -> TELEGRAM_FILES:
        ext = self.file_ext
        if ext in VIDEO_TYPES:
            return Video
        elif ext in GIF_TYPES:
            return Animation
        elif ext in IMAGE_TYPES:
            return PhotoSize
        return Document


@dataclass
class FileSummary(FileExtMixin):
    """
    A Summary for any file

    Attributes:
        filename (str): The filename of the file
        file (FileOrPath): A FileLike or FilePath of the media file
        size (int): The physical size on the disk in bytes.

    Args:
        filename (str): The filename of the file
        file (FileOrPath): A FileLike or FilePath of the media file
        size (int): The physical size on the disk in bytes.
    """

    filename: str
    file: FileOrPath
    size: int

    @staticmethod
    async def _determine_size(file: FileOrPath) -> int:
        """
        Determine the disk volume in bytes of the file

        Args:
            file (FileOrPath): File like or path like

        Returns:
            The file's size in bytes as int
        """
        if isinstance(file, FilePath):  # type: ignore[misc, arg-type]
            a_file = AsyncPath(file)
            return (await a_file.stat()).st_size  # type: ignore[no-any-return]
        elif isinstance(file, BytesIO):
            return file.getbuffer().nbytes
        else:
            size = len(await read_file_like(file))
            await seek(file, 0)
        return size

    @classmethod
    async def from_file(cls, file: FileOrPath, filename: str) -> "FileSummary":
        """
        Create `FileSummary` from a file and it's filename

        Args:
            file (FileOrPath): File like or path like for the file
            filename (srt): The file's name

        Returns:
            The corresponding `FileSummary`
        """
        return FileSummary(
            filename=filename,
            file=file,
            size=await cls._determine_size(file),
        )

    async def as_common(self) -> BytesIO | Path | bytes:
        """
        Return the content of the file in a commonly used format
        """
        if isinstance(self.file, (AsyncPath, Path, str)):
            return Path(str(self.file))
        elif isinstance(self.file, BytesIO):
            return self.file
        return await read_file_like(self.file)


class MediaMixin:
    height: int
    width: int

    @property
    def ratio_wh(self) -> float:
        """The width-to-height ratio."""
        return self.width / self.height

    @property
    def ratio_hw(self) -> float:
        """The height-to-width ratio."""
        return self.height / self.width


@dataclass
class MediaFileSummary(MediaMixin, FileSummary):
    """
    A Summary for media file such as images and videos

    Attributes:
        filename (str): The filename of the file
        file (FileOrPath): A FileLike or FilePath of the media file
        size (int): The physical size on the disk in bytes.
        width (int): The width of the media
        height (int): The height of the media

    Args:
        filename (str): The filename of the file
        file (FileOrPath): A FileLike or FilePath of the media file
        size (int): The physical size on the disk in bytes.
        width (int): The width of the media
        height (int): The height of the media
    """

    height: int
    width: int

    @classmethod
    async def from_file(cls, file: FileOrPath, filename: str) -> "MediaFileSummary":
        summary = await super().from_file(file, filename)
        return await cls.from_file_summary(summary=summary)

    @classmethod
    async def from_file_summary(
        cls,
        summary: FileSummary,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> "MediaFileSummary":
        """
        Convert an existing FileSummary to a MediaFile if possible

        Args:
            summary (FileSummary): The FileSummary to convert
            width (int, optional): Width of the media, if not set automatically determined
            height (int, optional): Height of the media, if not set automatically determined

        Returns:
            The correct MediaFile with width and height set
        """
        if summary.file_ext not in [*IMAGE_TYPES, *GIF_TYPES, *VIDEO_TYPES]:
            raise ValueError("`summary` is not a media file")

        if not width or not height:
            width, height = await cls.size_from_file(file=summary.file, ext=summary.file_ext)

        return cls(
            filename=summary.filename,
            file=summary.file,
            size=summary.size,
            width=width,
            height=height,
        )

    @classmethod
    async def size_from_file(cls, file: FileOrPath, ext: str) -> tuple[int, int]:
        """
        Determine the width, height of a media file

        Args:
            file (FileOrPath): File as  a file like or a path
            ext (str): The files extension without the dot

        Returns:
            The tuple resolution of the file as width and height in that order
        """
        file_content = await read_file_like(file=file)

        if ext in [*VIDEO_TYPES, *GIF_TYPES]:
            return await cls._determine_size_video(input=file_content)
        elif ext in IMAGE_TYPES:
            return await cls._determine_size_image(input=file_content)
        else:
            raise NotImplementedError(f"No way to determine size for type `{ext}`")

    @staticmethod
    async def _determine_size_video(input: bytes) -> tuple[int, int]:
        """
        Get size of any video via ffprobe

        Args:
            input (bytes): The video file as bytes

        Returns:
            A tuple of width and height in that order
        """
        return tuple(  # type: ignore[return-value]
            (await ffprobe(input, "-select_streams", "v:0", "-show_entries", "stream=width,height"))["streams"][
                0
            ].values()
        )

    @staticmethod
    async def _determine_size_image(input: bytes) -> tuple[int, int]:
        """
        Get size of any image with PIL

        Args:
            input (bytes): The image file as bytes

        Returns:
            A tuple of width and height in that order
        """
        with Image.open(BytesIO(input)) as image:
            return image.size
