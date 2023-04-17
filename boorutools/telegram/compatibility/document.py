from boorutools.models.base import URLFileSummary
from boorutools.telegram.compatibility.base import MediaCompatibility, MediaSummary


class DocumentCompatibility(MediaCompatibility):
    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, bool]:
        if self.file.size > self.MAX_SIZE_UPLOAD:
            return None, False
        if isinstance(self.file, URLFileSummary) and (self.file.size > self.MAX_SIZE_URL or force_download):
            self.file = await self.download()
        return self.file, True
