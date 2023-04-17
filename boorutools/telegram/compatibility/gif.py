from asyncio import subprocess
from io import BytesIO

from boorutools.models.file_summary import URLFileSummary
from boorutools.telegram.compatibility.base import MediaSummary
from boorutools.telegram.compatibility.document import DocumentCompatibility


class GifCompatibility(DocumentCompatibility):
    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, bool]:
        if self.file.file_ext == "webm":
            if isinstance(self.file, URLFileSummary):
                self.file = await self.download()

            if converted := await self.webm_to_mp4(self.file.file):
                self.file.file = converted
            else:
                return None, False

        return (await super().make_compatible(force_download))[0], False

    async def webm_to_mp4(self, data: BytesIO) -> BytesIO | None:
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
