from io import BytesIO
from pathlib import Path
from typing import Optional

from telegram import Animation

from tgtools.models.summaries import Downloadable, MediaFileSummary
from tgtools.telegram.compatibility.base import OutputFileType
from tgtools.telegram.compatibility.video import VideoCompatibility
from tgtools.utils.file import ffmpeg, get_bytes_from_file
from tgtools.utils.types import TELEGRAM_FILES


class GifCompatibility(VideoCompatibility):
    """
    Class for checking and making GIF files compatible with Telegram.
    Inherits from DocumentCompatibility.
    """

    async def remove_audio(self, data: bytes) -> BytesIO | None:
        """
        Remove all audio tracks without reencoding

        Args:
            data (bytes): The file to adjust as bytes

        Returns:
            The new file as BytesIO
        """
        return await ffmpeg(data, "-an", "-c:v", "copy")

    async def make_compatible(self, force_download: bool = False) -> tuple[Optional[OutputFileType], TELEGRAM_FILES]:
        """
        Make the GIF file compatible by converting it to MP4 format if needed and downloading if necessary.

        Args:
            force_download (bool, optional): Force download the file even if it's already compatible. Defaults to False.

        Returns:
            tuple[Optional[OutputFileType], TELEGRAM_FILES]: A tuple containing the compatible media file (or None
                if not compatible) and its type.
        """
        file, _ = await super().make_compatible(force_download)
        if not file or not isinstance(file, (Downloadable, MediaFileSummary)):
            return None, Animation

        self.file = file

        if isinstance(self.file, MediaFileSummary):
            if converted := await self.remove_audio(await get_bytes_from_file(self.file.file)):
                self.file.file = converted
                self.file.filename = Path(self.file.filename).with_suffix(".mp4").name
                self.file.size = converted.getbuffer().nbytes

        return self.file, Animation
