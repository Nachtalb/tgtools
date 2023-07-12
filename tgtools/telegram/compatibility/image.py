from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image
from telegram import Document, PhotoSize

from tgtools.models.summaries import DownloadableMedia, MediaFileSummary, MediaMixin
from tgtools.telegram.compatibility.base import MediaCompatibility, OutputFileType
from tgtools.utils.file import get_bytes_from_file
from tgtools.utils.types import TELEGRAM_FILES


class ImageCompatibility(MediaCompatibility):
    """
    Class for checking and making image files compatible with Telegram.
    Inherits from MediaCompatibility.

    Attributes:
        MAX_IMAGE_RATIO (int): The maximum aspect ratio allowed for an image (1:20).
        MAX_SIZE_UPLOAD (int): The maximum size of an image file to be uploaded (10 MB).
        MAX_SIZE_URL (int): The maximum size of an image file to be sent as a URL (5 MB).
        MAX_IMAGE_SIZE_SUM (int): The maximum sum of image width and height (10,000).
    """

    MAX_IMAGE_RATIO = 20  # 1:20
    MAX_SIZE_UPLOAD = 10_000_000
    MAX_SIZE_URL = 5_000_000
    MAX_IMAGE_SIZE_SUM = 10_000

    def resolution_too_heigh(self) -> bool:
        """
        Check if the resolution of the image is too high.

        Returns:
            bool: True if the sum of the image width and height is greater than the maximum allowed, False otherwise.
        """
        if not isinstance(self.file, MediaMixin):
            return True
        return self.file.width + self.file.height > self.MAX_IMAGE_SIZE_SUM

    def ratio_too_drastic(self) -> bool:
        """
        Check if the aspect ratio of the image is too drastic.

        Returns:
            bool: True if the aspect ratio is greater than or equal to the maximum allowed, False otherwise.
        """
        if not isinstance(self.file, MediaMixin):
            return True
        return self.file.ratio_hw >= self.MAX_IMAGE_RATIO or self.file.ratio_wh >= self.MAX_IMAGE_RATIO

    def file_size_too_big(self) -> bool:
        """
        Check wether the file's disk volume is too high for uploads
        """
        if not hasattr(self.file, "size"):
            return True
        return self.file.size >= self.MAX_SIZE_UPLOAD

    def is_webp(self) -> bool:
        """
        Check if the image format is WebP.

        Returns:
            bool: True if the image format is WebP, False otherwise.
        """
        return self.file.file_ext == "webp"

    def needs_processing(self) -> bool:
        """
        Check if the image needs processing.

        Returns:
            bool: True if the image needs processing (due to resolution, aspect ratio, file size, or format),
                  False otherwise.
        """
        return self.resolution_too_heigh() or self.ratio_too_drastic() or self.file_size_too_big() or self.is_webp()

    async def decrease_file_size(self, decrease_resolution: bool = True) -> None:
        """
        Continuously reduce the image resolution until the file size is small enough to upload.

        Args:
            decrease_resolution (bool, optional): Decrease resolution to the max allowed as PhotoSize while decreasing
                the file size. This is not needed when sending the file as a Document.
        """
        if not isinstance(self.file, MediaFileSummary):
            raise ValueError("`self.file` needs to be a downloaded piece of media `MediaFileSummary`")

        with Image.open(await get_bytes_from_file(self.file.file)) as image:
            while self.file_size_too_big():
                image = self.reduce_resolution(image=image, decrease_resolution=decrease_resolution)
                await self.update_file(image=image)

    async def update_file(self, image: Image.Image, format: Optional[str] = None) -> None:
        """
        Save the image to self.file and update all information accordingly.

        Args:
            image (Image.Image): The image to save.
            format (str, optional): The format to save the image as. Defaults to None.
        """
        if not isinstance(self.file, MediaFileSummary):
            raise ValueError("`self.file` needs to be a downloaded piece of media `MediaFileSummary`")

        self.file.file = BytesIO()
        format = format or self.file.file_ext
        if format.lower() == "jpg":
            format = "jpeg"

        image.save(self.file.file, format=format)
        self.file.width, self.file.height = await self.file._determine_size_image(input=self.file.file.getvalue())
        if format != self.file.file_ext:
            self.file.filename = Path(self.file.filename).with_suffix(f".{format}").name

        self.file.file.seek(0)

    async def convert_to_jpeg(self) -> None:
        """
        Convert the image to a JPEG format.

        Returns:
            Image.Image: The converted image in JPEG format.
        """
        if not isinstance(self.file, MediaFileSummary):
            raise ValueError("`self.file` needs to be a downloaded piece of media `MediaFileSummary`")

        with Image.open(await get_bytes_from_file(self.file.file)) as image:
            if image.mode == "RGBA":
                white_background = Image.new("RGB", image.size, (255, 255, 255))
                white_background.paste(image, (0, 0), image)
                image = white_background
            await self.update_file(image, "jpeg")

    def reduce_resolution(self, image: Image.Image, decrease_resolution: bool = True) -> Image.Image:
        """
        Reduce the resolution of the image to either the maximum allowed size or to 90% of its current size.

        Args:
            image (Image.Image): The image to reduce the resolution of.
            decrease_resolution (bool, optional): If the image resolution should also be decreased to the max.
                Might not be needed in case we send the file as a Document.

        Returns:
            Image.Image: The image with reduced resolution.
        """
        """Reduce resolution to either max allowed size or to 0.9 of it's current size"""
        resize_ratio = 0.9
        if decrease_resolution and self.resolution_too_heigh():
            resize_ratio = self.MAX_IMAGE_SIZE_SUM / (sum(image.size))

        image = image.resize((int(image.width * resize_ratio), int(image.height * resize_ratio)))
        return image

    async def make_compatible(self, force_download: bool = False) -> tuple[Optional[OutputFileType], TELEGRAM_FILES]:
        """
        Make the image file compatible with Telegram by checking its size, aspect ratio, and format,
        and converting or resizing if necessary.

        The following cases are handled:
        1. If the aspect ratio is too drastic, the image is sent as a document.
        2. Further process the image due to resolution, aspect ratio, file size or format.
        3. If the force_download flag is set and the file is a URLFileSummary, download the file.

        Args:
            force_download (bool, optional): Force download the file even if it's already compatible. Defaults to False.

        Returns:
            tuple[MediaSummary | None, MediaType]: A tuple containing the compatible media file (or None if not
                                                   compatible) and its type.
        """
        file = self.download_if_needed(
            force_download=force_download or not isinstance(self.file, MediaMixin) or self.needs_processing()
        )
        if not file or not isinstance(file, (DownloadableMedia, MediaFileSummary)):
            return None, PhotoSize

        self.file = file

        if self.ratio_too_drastic():
            await self.decrease_file_size(decrease_resolution=False)
            return self.file, Document

        if self.is_webp():
            await self.convert_to_jpeg()

        if self.resolution_too_heigh():
            await self.decrease_file_size(decrease_resolution=True)

        return self.file, PhotoSize
