from abc import ABCMeta, abstractproperty
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator

from pydantic import BaseModel, PrivateAttr
from yarl import URL

from tgtools.models.summaries.downloadable import DownloadableMedia
from tgtools.utils.urls.builder import URLTemplateBuilder

if TYPE_CHECKING:
    from tgtools.api.booru.base import BooruApi


class BooruPost(BaseModel, metaclass=ABCMeta):
    """
    A class representing a generic Booru post.

    Attributes:
        id (int): The posts ID
    """

    id: int

    # TODO: No idea how the correct type annotation here would be
    _api: "BooruApi" = PrivateAttr()  # type: ignore[type-arg]
    _file_summary: DownloadableMedia | None = PrivateAttr(None)
    _post_url: URLTemplateBuilder = PrivateAttr(URLTemplateBuilder("https://example.com/posts/{id}"))
    _post_url_path: str = PrivateAttr("")

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.

        Returns:
            str: The string representation of the object.
        """
        return f"<{self.__class__.__name__} id={self.id}>"

    def set_api(self, api: "BooruApi") -> None:  # type: ignore[type-arg]
        """
        Sets the API instance.

        Args:
            api (BooruApi): The API instance.
        """
        self._api = api
        self._post_url = URLTemplateBuilder(f"{self._api.url}{self._post_url_path}")

    async def download(self, out: Path | None = None) -> BytesIO | Path:
        """
        Download the post file.

        Args:
            out (Path | None): The output path for the downloaded file, if any.

        Returns:
            BytesIO | Path: The downloaded file as a BytesIO object if no output path is provided,
                            otherwise the output path.
        """
        return await self._api.download(self.best_file_url, out)

    async def iter_download(
        self, out: Path | None = None, chunk_size: int = 1024 * 1024
    ) -> AsyncGenerator[BytesIO | Path, None]:
        """
        Download the post file in chunks.

        Args:
            out (Path | None): The output path for the downloaded file, if any.
            chunk_size (int, optional): The size of the chunks to download. Defaults to 1024 * 1024.

        Yields:
            AsyncGenerator[BytesIO | Path, None]: The downloaded file as a BytesIO object if no output path is
                                                  provided, otherwise the output path, in chunks.
        """
        async for item in self._api.iter_download(self.best_file_url, out, chunk_size):
            yield item

    @property
    def tags_rating(self) -> set[str]:
        """
        Get the full named rating tags of the post.

        Returns:
            set[str]: The rating tags as a set of strings.
        """
        return {self.rating_full} if self.rating_full else set()

    @property
    def simple_tags_rating(self) -> set[str]:
        """
        Get the simple named rating tags of the post.

        Returns:
            set[str]: The rating tags as a set of strings.
        """
        return {self.rating_simple} if self.rating_simple else set()

    @property
    def tags_with_rating(self) -> set[str]:
        """
        Get all the tags of the post, including rating tags.

        Returns:
            set[str]: All the tags with rating as a set of strings.
        """
        return self.tags & self.tags_rating

    @property
    def url(self) -> URL:
        """
        Get the gui URL of the post.

        Returns:
            URL: The post URL.
        """
        return self._post_url.url(id=self.id).build_url()

    @property
    def tags_general(self) -> set[str]:
        """
        Get the general tags of the post.

        Note: Category tags are not available on this service.

        Returns:
            set[str]: The general tags as a set of strings.
        """
        return set()

    @property
    def tags_artist(self) -> set[str]:
        """
        Get the artist tags of the post.

        Note: Category tags are not available on this service.

        Returns:
            set[str]: The artist tags as a set of strings.
        """
        return set()

    @property
    def tags_copyright(self) -> set[str]:
        """
        Get the copyright tags of the post.

        Note: Category tags are not available on this service.

        Returns:
            set[str]: The copyright tags as a set of strings.
        """
        return set()

    @property
    def tags_character(self) -> set[str]:
        """
        Get the character tags of the post.

        Note: Category tags are not available on this service.

        Returns:
            set[str]: The character tags as a set of strings.
        """
        return set()

    @property
    def tags_meta(self) -> set[str]:
        """
        Get the meta tags of the post.

        Note: Category tags are not available on this service.

        Returns:
            set[str]: The meta tags as a set of strings.
        """
        return set()

    @abstractproperty
    def rating_full(self) -> str | None:
        """
        Get the full named rating of the post.

        Returns:
            set[str]: The full rating strings.
        """
        ...

    @abstractproperty
    def rating_simple(self) -> str | None:
        """
        Get the simple named rating of the post.

        Without the "rating:" part.

        Returns:
            set[str]: The simple rating strings.
        """
        ...

    @abstractproperty
    def tags(self) -> set[str]:
        """
        Get all the tags of the post (excluding rating tags).

        Returns:
            set[str]: All the tags as a set of strings.
        """
        ...

    @abstractproperty
    def best_file_url(self) -> str:
        """
        Get the best file URL of the post.

        Returns:
            str: The best file URL as a string.
        """
        ...

    @abstractproperty
    def is_bad(self) -> bool:
        """
        Check if the post is bad.

        Returns:
            bool: True if the post is bad, False otherwise.
        """
        ...

    @abstractproperty
    def filename(self) -> str:
        """
        Get the filename of the post.

        Returns:
            str: The filename as a string.
        """
        ...

    @abstractproperty
    def file_summary(self) -> DownloadableMedia:
        """
        Get the file summary of the post.

        Returns:
            URLFileSummary: The file summary as a URLFileSummary object.
        """
        ...

    @abstractproperty
    def main_source(self) -> str | None:
        """
        Get the processed main source url

        Returns:
            str | None: The processed source, or None if there is no source
        """
        ...
