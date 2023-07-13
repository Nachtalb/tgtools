from io import BytesIO
from pathlib import Path
from typing import Optional

from telegram import Video

from tgtools.models.summaries import Downloadable, MediaFileSummary
from tgtools.telegram.compatibility.base import OutputFileType
from tgtools.telegram.compatibility.document import DocumentCompatibility
from tgtools.utils.file import ffmpeg, read_file_like
from tgtools.utils.types import TELEGRAM_FILES


class VideoCompatibility(DocumentCompatibility):
    """
    Class for checking and making video files compatible with Telegram.
    Inherits from DocumentCompatibility.
    """

    async def make_streamable(self, data: bytes) -> BytesIO | None:
        """
        Make an mp4 streamable without reencoding.

        To make a mp4 file streamable all metadata must be at the front of the start. This is known as "faststart".
        No reencoding takes place so this should be rather fast.

        Args:
            data (bytes): The existing mp4 data

        Returns:
            BytesIO of the new file.
        """
        return await ffmpeg(data, "-f", "mp4", "-c copy", "-movflags", "+faststart")

    async def to_mp4(self, data: bytes) -> BytesIO | None:
        """
        Convert a any video (in BytesIO format) to an MP4 video (in BytesIO format) asynchronously.

        This function uses FFmpeg to perform the conversion. This also enables streamability just like the
        `make_streamable` method.

        Args:
            data (BytesIO): The input video as a BytesIO object.

        Returns:
            BytesIO | None: The output MP4 video as a BytesIO object, or None if the conversion fails.

        Examples:
            # Assuming `webm_data` is a BytesIO object containing a valid WebM video
            >>> mp4_data = await webm_to_mp4(webm_data)
            # `mp4_data` will be a BytesIO object containing the converted MP4 video or None if the conversion failed
        """
        video_filter = "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2"  # Make sure we have even width and height
        codec = "-c:v", "libx264"  # Use H264 codec (faster to encode compared to H265)
        # output_format = "-f", "ismv"  # May not be supported (Internet Streaming Media Format)
        output_format = "-f", "mp4"  # Use a mp4 container
        output_options = "-movflags", "+faststart", "-pix_fmt", "yuv420p"  # Streamability and ensure supported colors

        return await ffmpeg(data, *video_filter, *codec, *output_format, *output_options)

    async def make_compatible(self, force_download: bool = False) -> tuple[Optional[OutputFileType], TELEGRAM_FILES]:
        """
        Make the video file compatible with Telegram by checking its size and downloading if necessary.

        If the video file is too big to be sent to Telegram, we send the first frame of the image instead.

        Args:
            force_download (bool, optional): Force download the file even if it's already compatible. Defaults to False.

        Returns:
            tuple[Optional[OutputFileType], TELEGRAM_FILES]: A tuple containing the compatible media file (or None if
                not compatible) and its type.
        """

        file, _ = await super().make_compatible(force_download=force_download or self.file.file_ext in ["mkv", "webm"])
        if not file or not isinstance(file, (Downloadable, MediaFileSummary)):
            return None, Video

        self.file = file

        if isinstance(self.file, MediaFileSummary):
            file_content = await read_file_like(file=self.file.file)
            if self.file.file_ext in ["mp4", "mkv"]:
                conversion = await self.make_streamable(data=file_content)
            else:
                conversion = await self.to_mp4(data=file_content)

            if conversion:
                self.file.filename = Path(self.file.filename).with_suffix(".mp4").name
                self.file.size = conversion.getbuffer().nbytes
                self.file.file = conversion

        return self.file, Video
