from io import BytesIO

from PIL import Image
from telegram import Document, PhotoSize

from tgtools.models.file_summary import URLFileSummary
from tgtools.telegram.compatibility.base import MediaCompatibility, MediaSummary, MediaType


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
        return self.file.width + self.file.height > self.MAX_IMAGE_SIZE_SUM

    def ratio_too_drastic(self) -> bool:
        """
        Check if the aspect ratio of the image is too drastic.

        Returns:
            bool: True if the aspect ratio is greater than or equal to the maximum allowed, False otherwise.
        """
        return self.file.ratio_hw >= self.MAX_IMAGE_RATIO or self.file.ratio_wh >= self.MAX_IMAGE_RATIO

    def file_size_too_big(self, max_size: tuple[int, int] = (0, 0)) -> bool:
        """
        Check if the file size of the image is too big.

        Args:
            max_size (tuple[int, int], optional): A tuple containing the maximum size for upload and URL.

        Returns:
            bool: True if the file size exceeds the maximum allowed, False otherwise.
        """
        if any(max_size):
            return self.file.size > max_size[0] or (
                isinstance(self.file, URLFileSummary) and self.file.size > max_size[1]
            )
        return self.file.size > self.MAX_SIZE_UPLOAD or (
            isinstance(self.file, URLFileSummary) and self.file.size > self.MAX_SIZE_URL
        )

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

    def decrease_file_size(self, image: Image.Image, max_size: tuple[int, int] = (0, 0)):
        """
        Continuously reduce the image resolution until the file size is small enough to upload.

        Args:
            image (Image.Image): The image to reduce the resolution of.
            max_size (tuple[int, int], optional): A tuple containing the maximum size for upload and URL.
        """
        while self.file_size_too_big(max_size):
            image = self.reduce_resolution(image)

    def save_file(self, image: Image.Image, format: str | None = None):
        """
        Save the image to self.file and update all information accordingly.

        Args:
            image (Image.Image): The image to save.
            format (str | None, optional): The format to save the image as. Defaults to None.
        """
        file = BytesIO()
        format = format or self.file.file_ext
        if format.lower() == "jpg":
            format = "jpeg"
        image.save(file, format=format or self.file.file_ext)
        if format:
            self.file.file_name = self.file.file_name.with_suffix(f".{format}")
        self.file.size = file.getbuffer().nbytes
        self.file.width, self.file.height = image.size
        self.file.file = file
        file.seek(0)

    def _recalculate_size(self, image: Image.Image | BytesIO):
        """
        Recalculate width and height of the image
        """
        if isinstance(image, BytesIO):
            with Image.open(image) as p_image:
                self.file.width, self.file.height = p_image.size
            image.seek(0)
        else:
            self.file.width, self.file.height = image.size

    def convert_to_jpeg(self, image: Image.Image) -> Image.Image:
        """
        Convert the image to a JPEG format.

        Args:
            image (Image.Image): The image to convert.

        Returns:
            Image.Image: The converted image in JPEG format.
        """
        if image.mode == "RGBA":
            white_background = Image.new("RGB", image.size, (255, 255, 255))
            white_background.paste(image, (0, 0), image)
            image = white_background
        self.save_file(image, "jpeg")
        return image

    def reduce_resolution(self, image: Image.Image) -> Image.Image:
        """
        Reduce the resolution of the image to either the maximum allowed size or to 90% of its current size.

        Args:
            image (Image.Image): The image to reduce the resolution of.

        Returns:
            Image.Image: The image with reduced resolution.
        """
        """Reduce resolution to either max allowed size or to 0.9 of it's current size"""
        resize_ratio = 0.9
        if self.resolution_too_heigh():
            resize_ratio = self.MAX_IMAGE_SIZE_SUM / (sum(image.size))

        image = image.resize((int(image.width * resize_ratio), int(image.height * resize_ratio)))
        self.save_file(image)
        return image

    async def make_compatible(self, force_download: bool = False) -> tuple[MediaSummary | None, MediaType]:
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
        if isinstance(self.file, URLFileSummary) and self.file.height <= 0 and self.file.width <= 0:
            self.file = await self.download()
            self._recalculate_size(self.file.file)

        if force_download and isinstance(self.file, URLFileSummary):
            self.file = await self.download()

        if self.ratio_too_drastic():
            document_size = (MediaCompatibility.MAX_SIZE_UPLOAD, MediaCompatibility.MAX_SIZE_URL)
            if self.file_size_too_big(document_size):
                self.file = await self.download()
                with Image.open(self.file.file) as image:
                    self.decrease_file_size(image, document_size)
            return self.file, Document

        if self.needs_processing() and isinstance(self.file, URLFileSummary):
            self.file = await self.download()
        elif not self.needs_processing():
            return self.file, PhotoSize

        with Image.open(self.file.file) as image:
            if self.is_webp():
                image = self.convert_to_jpeg(image)

            self.decrease_file_size(image)

            if self.resolution_too_heigh():
                self.reduce_resolution(image)
            return self.file, PhotoSize
