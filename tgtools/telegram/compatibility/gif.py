from asyncio import subprocess
from io import BytesIO

from telegram import Video

from tgtools.models.file_summary import URLFileSummary
from tgtools.telegram.compatibility.base import MediaSummary, MediaType
from tgtools.telegram.compatibility.document import DocumentCompatibility


class GifCompatibility(DocumentCompatibility):
    """
    Class for checking and making GIF files compatible with Telegram.
    Inherits from DocumentCompatibility.
    """

    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, MediaType]:
        """
        Make the GIF file compatible with Telegram by converting it to MP4 format if needed and downloading if necessary.

        Args:
            force_download (bool, optional): Force download the file even if it's already compatible. Defaults to False.

        Returns:
            tuple[MediaSummary | None, MediaType]: A tuple containing the compatible media file (or None if not compatible) and
                                                   its type.
        """
        if self.file.file_ext == "webm":
            if isinstance(self.file, URLFileSummary):
                self.file = await self.download()

            if converted := await self.webm_to_mp4(self.file.file):
                converted.seek(0)
                self.file.file = converted
                self.file.size = converted.getbuffer().nbytes
            else:
                return None, Video

        return (await super().make_compatible(force_download))[0], Video

    async def webm_to_mp4(self, data: BytesIO) -> BytesIO | None:
        """
        Convert a WebM video (in BytesIO format) to an MP4 video (in BytesIO format) asynchronously.

        This function uses FFmpeg to perform the conversion. It takes the input WebM video as a BytesIO object
        and returns the output MP4 video as a BytesIO object, or None if the conversion fails.

        Args:
            data (BytesIO): The input WebM video as a BytesIO object.

        Returns:
            BytesIO | None: The output MP4 video as a BytesIO object, or None if the conversion fails.

        Examples:
            # Assuming `webm_data` is a BytesIO object containing a valid WebM video
            >>> mp4_data = await webm_to_mp4(webm_data)
            # `mp4_data` will be a BytesIO object containing the converted MP4 video or None if the conversion failed
        """
        input_file = "-i", "pipe:0"
        video_filter = "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2"
        codec = "-c:v", "libx264"
        output_format = "-f", "ismv"  # ismv is similar to mp4 but has improved movflags support basically
        output_options = "-movflags", "+faststart", "-pix_fmt", "yuv420p"

        process = await subprocess.create_subprocess_exec(
            "ffmpeg",
            "-y",
            *input_file,
            *video_filter,
            *codec,
            *output_options,
            *output_format,
            "pipe:1",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        stdout, _ = await process.communicate(data.getvalue())
        return BytesIO(stdout) if stdout else None
