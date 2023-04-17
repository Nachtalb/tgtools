from tgtools.models.file_summary import URLFileSummary
from tgtools.telegram.compatibility.base import MediaCompatibility, MediaSummary


class DocumentCompatibility(MediaCompatibility):
    """
    Class for checking and making document files compatible with Telegram.
    Inherits from MediaCompatibility.
    """

    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, bool]:
        """
        Make the document file compatible with Telegram by checking its size and downloading if necessary.

        Args:
            force_download (bool, optional): Force download the file even if it's already compatible. Defaults to False.

        Returns:
            tuple[MediaSummary | None, bool]: A tuple containing the compatible media file (or None if not compatible) and
                                              a boolean indicating if it has to be sent as a Telegram Document.
        """
        if self.file.size > self.MAX_SIZE_UPLOAD:
            return None, False
        if isinstance(self.file, URLFileSummary) and (self.file.size > self.MAX_SIZE_URL or force_download):
            self.file = await self.download()
        return self.file, True
