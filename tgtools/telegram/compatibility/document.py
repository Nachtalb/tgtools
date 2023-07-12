from typing import Optional

from telegram import Document

from tgtools.models.summaries import Downloadable, FileSummary
from tgtools.telegram.compatibility.base import MediaCompatibility, OutputFileType
from tgtools.utils.types import TELEGRAM_FILES


class DocumentCompatibility(MediaCompatibility):
    """
    Class for checking and making document files compatible with Telegram.
    Inherits from MediaCompatibility.
    """

    async def make_compatible(
        self, force_download: bool = False
    ) -> tuple[Optional[OutputFileType] | None, TELEGRAM_FILES]:
        """
        Make the document file compatible with Telegram by checking its size and downloading if necessary.

        Args:
            force_download (bool, optional): Force download the file even if it's already compatible. Defaults to False.

        Returns:
            tuple[MediaSummary | None, MediaType]: A tuple containing the compatible media file (or None if not
                                                   compatible) and its type.
        """
        if isinstance(self.file, (Downloadable, FileSummary)) and self.file.size > self.MAX_SIZE_UPLOAD:
            return None, Document

        self.file = await self.download_if_needed(force_download=force_download)

        return self.file, Document
