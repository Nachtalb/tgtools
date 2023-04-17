from boorutools.models.base import FileSummary
from boorutools.telegram.compatibility.base import MediaSummary
from boorutools.telegram.compatibility.document import DocumentCompatibility
from boorutools.telegram.compatibility.gif import GifCompatibility
from boorutools.telegram.compatibility.image import ImageCompatibility
from boorutools.telegram.compatibility.video import VideoCompatibility

__all__ = ["make_tg_compatible"]


async def make_tg_compatible(file: MediaSummary) -> tuple[FileSummary | MediaSummary | None, bool]:
    """
    Make sure the file is telegram compatibile

    Returns:
        A tuple of either the adjusted file summary and if the file has to
        be sent as a document or None and False in which case it's not compatible
        in any way.
    """
    if file.is_image:
        compatibility = ImageCompatibility(file)
    elif file.is_video:
        compatibility = VideoCompatibility(file)
    elif file.is_gif:
        compatibility = GifCompatibility(file)
    else:
        compatibility = DocumentCompatibility(file)

    return await compatibility.make_compatible()
