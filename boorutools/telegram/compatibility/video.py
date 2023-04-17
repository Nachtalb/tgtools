from boorutools.telegram.compatibility.base import MediaSummary
from boorutools.telegram.compatibility.document import DocumentCompatibility


class VideoCompatibility(DocumentCompatibility):
    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, bool]:
        return (await super().make_compatible(force_download))[0], False
