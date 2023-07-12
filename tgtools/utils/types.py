from pathlib import Path
from typing import IO, Protocol, Type, Union, runtime_checkable

from aiopath import AsyncPath
from telegram import Animation, Document, PhotoSize, Video


@runtime_checkable
class File(Protocol):
    """
    A file like object with synchronous write and read
    """

    def write(self, s: bytes) -> int:
        ...

    def read(self, n: int = -1) -> bytes:
        ...


@runtime_checkable
class AsyncFile(Protocol):
    """
    A file like object with asynchronous write and read
    """

    async def write(self, s: bytes) -> int:
        ...

    async def read(self, n: int = -1) -> bytes:
        ...


FileLike = Union[IO[bytes], File, AsyncFile]
"""Either a bytes-stream (e.g. open file handler) or a similar object that supports read and write (sync or async)."""

FilePath = Union[str, Path, AsyncPath]
"""A filepath either as string, as pathlib.Path or aiopath.AsyncPath object."""

FileOrPath = Union[FileLike, FilePath]
"""Representing any kind of file as file like or path like"""

IMAGE_TYPES = ["jpeg", "jpg", "png", "webp"]
"""Common image extensions"""
VIDEO_TYPES = ["mp4", "mkv", "webm"]
"""Common video extensions"""
GIF_TYPES = ["gif"]
"""GIF extension"""

TELEGRAM_FILES = Union[Type[Video], Type[Animation], Type[PhotoSize], Type[Document]]
"""A var representing all supported Telegram file types"""
