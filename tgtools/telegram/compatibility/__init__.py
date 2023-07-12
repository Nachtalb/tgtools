from typing import Optional

from telegram import Animation, PhotoSize, Video

from tgtools.telegram.compatibility.base import InputFileType, MediaCompatibility, OutputFileType
from tgtools.telegram.compatibility.document import DocumentCompatibility
from tgtools.telegram.compatibility.gif import GifCompatibility
from tgtools.telegram.compatibility.image import ImageCompatibility
from tgtools.telegram.compatibility.video import VideoCompatibility
from tgtools.utils.types import TELEGRAM_FILES

__all__ = ["make_tg_compatible"]


async def make_tg_compatible(
    file: InputFileType, force_download: bool = False
) -> tuple[Optional[OutputFileType], TELEGRAM_FILES]:
    """
    Make sure the file is compatible with Telegram.

    Args:
        file (MediaSummary): The media file to be checked for compatibility.
        force_download (bool): Force download the file (defaults to False).

    Returns:
        tuple[FileSummary | MediaSummary | None, MediaType]: A tuple containing either the adjusted file summary and
                                                             its type. None if the file is not compatible in any way.
    """
    compatibility: MediaCompatibility
    match file.telegram_type:
        case type_ if type_ is PhotoSize:
            compatibility = ImageCompatibility(file)
        case type_ if type_ is Video:
            compatibility = VideoCompatibility(file)
        case type_ if type_ is Animation:
            compatibility = GifCompatibility(file)
        case _:
            compatibility = DocumentCompatibility(file)
    return await compatibility.make_compatible(force_download=force_download)
