from io import BytesIO

import imageio
import numpy as np
from PIL import Image
from telegram import PhotoSize, Video

from tgtools.models.file_summary import FileSummary, URLFileSummary
from tgtools.telegram.compatibility.base import MediaSummary, MediaType
from tgtools.telegram.compatibility.document import DocumentCompatibility


class VideoCompatibility(DocumentCompatibility):
    """
    Class for checking and making video files compatible with Telegram.
    Inherits from DocumentCompatibility.
    """

    def _extract_first_image(self, content: BytesIO) -> BytesIO:
        """
        Extracts the first image from a video file.

        Args:
            content (BytesIO): The video file content.

        Returns:
            BytesIO: The first image extracted from the video content.
        """
        video_reader = imageio.get_reader(content, "ffmpeg")  # pyright: ignore[reportGeneralTypeIssues]
        first_frame = video_reader.get_data(0)

        image = Image.fromarray(np.uint8(first_frame))
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        image.close()
        buffer.seek(0)
        return buffer

    async def _get_first_frame(self):
        """
        Returns the first frame from self.file

        It handles both URLFileSummary and FileSummary

        Returns:
            BytesIO: The first frame of the video file.
        """
        if isinstance(self.file, URLFileSummary):
            async for buffer in self.file.iter_download_method():
                try:
                    return self._extract_first_image(buffer)
                except IndexError:
                    buffer.seek(0, 2)
        else:
            return self._extract_first_image(self.file.file)

    async def _get_first_frame_summary(self):
        """
        Returns the summary of the first frame of the video file.

        Returns:
            FileSummary: The summary of the first frame of the video file.
        """
        if first_frame := await self._get_first_frame():
            result = FileSummary(
                file_name=self.file.file_name.with_stem(".jpeg"),
                file=first_frame,
                size=first_frame.getbuffer().nbytes,
                width=self.file.width,
                height=self.file.height,
            )
            return result

    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, MediaType]:
        """
        Make the video file compatible with Telegram by checking its size and downloading if necessary.

        If the video file is too big to be sent to Telegram, we send the first frame of the image instead.

        Args:
            force_download (bool, optional): Force download the file even if it's already compatible. Defaults to False.

        Returns:
            tuple[MediaSummary | None, MediaType]: A tuple containing the compatible media file (or None if not
                                                   compatible) and its type.
        """
        if summary := (await super().make_compatible(force_download))[0]:
            return summary, Video
        elif frame_summary := await self._get_first_frame_summary():
            return frame_summary, PhotoSize
        return None, None
