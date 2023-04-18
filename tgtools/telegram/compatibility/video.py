from telegram import Video

from tgtools.telegram.compatibility.base import MediaSummary, MediaType
from tgtools.telegram.compatibility.document import DocumentCompatibility


class VideoCompatibility(DocumentCompatibility):
    """
    Class for checking and making video files compatible with Telegram.
    Inherits from DocumentCompatibility.
    """

    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, MediaType]:
        """
        Make the video file compatible with Telegram by checking its size and downloading if necessary.

        Args:
            force_download (bool, optional): Force download the file even if it's already compatible. Defaults to False.

        Returns:
            tuple[MediaSummary | None, MediaType]: A tuple containing the compatible media file (or None if not compatible) and
                                                   its type.
        """
        return (await super().make_compatible(force_download))[0], Video
