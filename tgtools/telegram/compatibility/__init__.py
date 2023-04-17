from tgtools.models.file_summary import FileSummary
from tgtools.telegram.compatibility.base import MediaSummary
from tgtools.telegram.compatibility.document import DocumentCompatibility
from tgtools.telegram.compatibility.gif import GifCompatibility
from tgtools.telegram.compatibility.image import ImageCompatibility
from tgtools.telegram.compatibility.video import VideoCompatibility

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
