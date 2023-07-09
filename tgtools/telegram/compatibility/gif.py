from io import BytesIO

from telegram import Video

from tgtools.models.file_summary import FileSummary
from tgtools.telegram.compatibility.base import MediaSummary, MediaType
from tgtools.telegram.compatibility.video import VideoCompatibility


class GifCompatibility(VideoCompatibility):
    """
    Class for checking and making GIF files compatible with Telegram.
    Inherits from DocumentCompatibility.
    """

    async def remove_audio(self, data: BytesIO) -> BytesIO | None:
        """
        Remove all audio tracks without reencoding

        Args:
            data (BytesIO): The file to adjust as bytes

        Returns:
            The new file as BytesIO
        """
        return await self._run_ffmpeg(data, "-an", "-c:v", "copy")

    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, MediaType]:
        """
        Make the GIF file compatible by converting it to MP4 format if needed and downloading if necessary.

        Args:
            force_download (bool, optional): Force download the file even if it's already compatible. Defaults to False.

        Returns:
            tuple[MediaSummary | None, MediaType]: A tuple containing the compatible media file (or None if not
                                                   compatible) and its type.
        """
        summary, type_ = await super().make_compatible(force_download)
        if type_ is not Video or summary is None:
            return None, Video

        self.file = summary

        if isinstance(self.file, FileSummary) and self.file.file:
            if converted := await self.remove_audio(self.file.file):
                converted.seek(0)
                self.file.file = converted
                self.file.size = converted.getbuffer().nbytes

        return self.file, Video
