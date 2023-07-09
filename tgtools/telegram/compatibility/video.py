from asyncio import subprocess
from io import BytesIO
from typing import Optional

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
        video_reader = imageio.get_reader(content, "ffmpeg")  # type: ignore[arg-type]
        first_frame = video_reader.get_data(0)

        image = Image.fromarray(np.uint8(first_frame))
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        image.close()
        buffer.seek(0)
        return buffer

    async def _get_first_frame(self) -> Optional[BytesIO]:
        """
        Returns the first frame from self.file

        It handles both URLFileSummary and FileSummary. We enforce `iter_download_method` as
        we never don't want to download the whole video as it might be very big.

        Returns:
            BytesIO: The first frame of the video file.

        Raises:
            NotImplementedError if the summary has no `iter_download_method`
        """
        if isinstance(self.file, URLFileSummary):
            if self.file.iter_download_method is not None:
                async for buffer in self.file.iter_download_method():
                    try:
                        return self._extract_first_image(buffer)
                    except IndexError:
                        buffer.seek(0, 2)
                else:
                    raise ValueError("Could not retrieve first frame from URL")
            else:
                raise NotImplementedError("To download the first frame implement iter_download_method")
        else:
            return self._extract_first_image(self.file.file)

    async def _get_first_frame_summary(self) -> FileSummary | None:
        """
        Returns the summary of the first frame of the video file.

        Returns:
            FileSummary: The summary of the first frame of the video file.
        """
        try:
            if first_frame := await self._get_first_frame():
                result = FileSummary(
                    file_name=self.file.file_name.with_stem(".jpeg"),
                    file=first_frame,
                    size=first_frame.getbuffer().nbytes,
                    width=self.file.width,
                    height=self.file.height,
                )
                return result
        except (NotImplementedError, ValueError):
            pass
        return None

    async def _run_ffmpeg(self, input: BytesIO, *arguments: str) -> BytesIO | None:
        """
        Run an ffmpeg command

        Args:
            input (BytesIO): Input file data
            *arguments (list[str]): Parameters for ffmpeg command

        Returns:
            The new file as BytesIO or None if it failed
        """
        input_file = "-i", "pipe:0"

        process = await subprocess.create_subprocess_exec(
            "ffmpeg",
            "-y",
            *input_file,
            *arguments,
            "pipe:1",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        stdout, _ = await process.communicate(input.getvalue())
        return BytesIO(stdout) if stdout else None

    async def make_streamable(self, data: BytesIO) -> BytesIO | None:
        """
        Make an mp4 streamable without reencoding.

        To make a mp4 file streamable all metadata must be at the front of the start. This is known as "faststart".
        No reencoding takes place so this should be rather fast.

        Args:
            data (BytesIO): The existing mp4 data

        Returns:
            BytesIO of the new file.
        """
        return await self._run_ffmpeg(data, "-f", "mp4", "-c copy", "-movflags", "+faststart")

    async def to_mp4(self, data: BytesIO) -> BytesIO | None:
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

        return await self._run_ffmpeg(data, *video_filter, *codec, *output_format, *output_options)

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
            if self.file.file_ext != "mp4" and isinstance(self.file, URLFileSummary):
                # Download for conversion. Telegram only supports mp4 as video format
                self.file = await self.download()

            if isinstance(self.file, FileSummary):
                match self.file.file_ext:
                    case "mp4", "mkv":
                        # Fast
                        conversion = self.make_streamable(self.file.file)
                    case _:
                        # Slow
                        conversion = self.to_mp4(self.file.file)

                if converted := await conversion:
                    converted.seek(0)
                    self.file.file = converted
                    self.file.size = converted.getbuffer().nbytes
                    self.file.file_name = self.file.file_name.with_suffix(".mp4")

            return summary, Video
        elif frame_summary := await self._get_first_frame_summary():
            return frame_summary, PhotoSize
        return None, None
