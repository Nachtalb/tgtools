from io import BytesIO

from PIL import Image

from boorutools.models.base import URLFileSummary
from boorutools.telegram.compatibility.base import MediaCompatibility, MediaSummary


class ImageCompatibility(MediaCompatibility):
    MAX_IMAGE_RATIO = 20  # 1:20
    MAX_SIZE_UPLOAD = 10_000_000
    MAX_SIZE_URL = 5_000_000
    MAX_IMAGE_SIZE_SUM = 10_000

    def resolution_too_heigh(self) -> bool:
        return self.file.width + self.file.height > self.MAX_IMAGE_SIZE_SUM

    def ratio_too_drastic(self) -> bool:
        return self.file.ratio_hw >= self.MAX_IMAGE_RATIO or self.file.ratio_wh >= self.MAX_IMAGE_RATIO

    def file_size_too_big(self, max_size: tuple[int, int] = tuple()) -> bool:
        if max_size:
            return self.file.size > max_size[0] or (
                isinstance(self.file, URLFileSummary) and self.file.size > max_size[1]
            )
        return self.file.size > self.MAX_SIZE_UPLOAD or (
            isinstance(self.file, URLFileSummary) and self.file.size > self.MAX_SIZE_URL
        )

    def is_webp(self) -> bool:
        return self.file.file_ext == "webp"

    def needs_processing(self) -> bool:
        return self.resolution_too_heigh() or self.ratio_too_drastic() or self.file_size_too_big() or self.is_webp()

    def decrease_file_size(self, image: Image.Image, max_size: tuple[int, int] = tuple()):
        """Continuously reduce image resolution until file is small enough to upload"""
        while self.file_size_too_big(max_size):
            image = self.reduce_resolution(image)

    def save_file(self, image: Image.Image, format: str | None = None):
        """Save image to self.file and update all information accordingly"""
        file = BytesIO()
        format = format or self.file.file_ext
        if format.lower() == "jpg":
            format = "jpeg"
        image.save(file, format=format or self.file.file_ext)
        if format:
            self.file.file_name = self.file.file_name.with_suffix(f".{format}")
        self.file.size = file.getbuffer().nbytes
        self.file.width, self.file.height = image.size

    def convert_to_jpeg(self, image: Image.Image) -> Image.Image:
        """Convert image to a JPEG"""
        if image.mode == "RGBA":
            white_background = Image.new("RGB", image.size, (255, 255, 255))
            white_background.paste(image, (0, 0), image)
            image = white_background
        self.save_file(image, "jpeg")
        return image

    def reduce_resolution(self, image: Image.Image) -> Image.Image:
        """Reduce resolution to either max allowed size or to 0.9 of it's current size"""
        resize_ratio = 0.9
        if self.resolution_too_heigh():
            resize_ratio = self.MAX_IMAGE_SIZE_SUM / (sum(image.size))

        image = image.resize((int(image.width * resize_ratio), int(image.height * resize_ratio)))
        self.save_file(image)
        return image

    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, bool]:
        if force_download and isinstance(self.file, URLFileSummary):
            self.file = await self.download()

        if self.ratio_too_drastic():
            document_size = (MediaCompatibility.MAX_SIZE_UPLOAD, MediaCompatibility.MAX_SIZE_URL)
            if self.file_size_too_big(document_size):
                self.file = await self.download()
                with Image.open(self.file.file) as image:
                    self.decrease_file_size(image, document_size)
            return self.file, True

        if self.needs_processing() and isinstance(self.file, URLFileSummary):
            self.file = await self.download()
        elif not self.needs_processing():
            return self.file, False

        with Image.open(self.file.file) as image:

            if self.is_webp():
                image = self.convert_to_jpeg(image)

            self.decrease_file_size(image)

            if self.resolution_too_heigh():
                self.reduce_resolution(image)
            return self.file, False
