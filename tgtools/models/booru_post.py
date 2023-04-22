from abc import ABCMeta, abstractproperty
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator

from pydantic import PrivateAttr
from yarl import URL

from tgtools.utils.url import URLTemplateBuilder

if TYPE_CHECKING:
    from tgtools.api.booru_api import BooruApi

from .file_summary import URLFileSummary


class RATING:
    """
    A utility class for handling generic Booru rating levels and their corresponding strings.

    Attributes:
        general (str): The general rating string.
        sensitive (str): The sensitive rating string.
        questionable (str): The questionable rating string.
        explicit (str): The explicit rating string.
        levels (dict[str, int]): A dictionary mapping rating strings to their corresponding integer levels.
        full_name_map (dict[str, str]): A dictionary mapping rating all variations of
                                        rating strings to their full name.
    """

    general = "rating:general"
    sensitive = "rating:sensitive"
    questionable = "rating:questionable"
    explicit = "rating:explicit"

    levels = {
        "rating:general": 0,
        "rating:sensitive": 1,
        "rating:questionable": 2,
        "rating:explicit": 3,
    }

    full_name_map = {
        "g": general,
        "general": general,
        "rating:general": general,
        "s": sensitive,
        "sensitive": sensitive,
        "rating:sensitive": sensitive,
        "q": questionable,
        "questionable": questionable,
        "rating:questionable": questionable,
        "e": explicit,
        "explicit": explicit,
        "rating:explicit": explicit,
    }

    @staticmethod
    def level(rating: str) -> int:
        """
        Get the integer level of a given rating.

        Args:
            rating (str): The rating string.

        Returns:
            int: The corresponding integer level of the rating.

        Examples:
            >>> RATING.level("g")
            0

            >>> RATING.level("sensitive")
            1

            >>> RATING.level("rating:explicit")
            3
        """
        return RATING.levels[RATING.full(rating)]

    @staticmethod
    def simple(rating: str) -> str:
        """
        Get the simple rating string from a given rating.

        Without the "rating:" part.

        Args:
            rating (str): The rating string.

        Returns:
            str: The simple rating string.

        Examples:
            >>> RATING.simple("g")
            "general"

            >>> RATING.simple("e")
            "explicit"
        """
        return RATING.full(rating).split(":")[-1]

    @staticmethod
    def full(rating: str) -> str:
        """
        Get the full rating string from a given rating.

        Args:
            rating (str): The rating string.

        Returns:
            str: The full rating string.

        Examples:
            >>> RATING.simple("g")
            "rating:general"

            >>> RATING.simple("rating:sensitive")
            "rating:sensitive"

            >>> RATING.simple("explicit")
            "rating:explicit"
        """
        return RATING.full_name_map[rating]


class BooruPost(metaclass=ABCMeta):
    """
    A class representing a generic Booru post.

    Attributes:
        id (int): The posts ID
    """

    id: int

    _api: "BooruApi" = PrivateAttr()
    _file_summary: URLFileSummary | None = PrivateAttr(None)
    _post_url: URLTemplateBuilder = PrivateAttr(URLTemplateBuilder("https://example.com/posts/{id}"))

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.

        Returns:
            str: The string representation of the object.
        """
        return f"<{self.__class__.__name__} id={self.id}>"

    def set_api(self, api: "BooruApi") -> None:
        """
        Sets the API instance.

        Args:
            api (BooruApi): The API instance.
        """
        self._api = api

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
        return self._post_url.url(id=id).build_url()

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
    def tags_general(self) -> set[str]:
        """
        Get the general tags of the post.

        Returns:
            set[str]: The general tags as a set of strings.
        """
        ...

    @abstractproperty
    def tags_artist(self) -> set[str]:
        """
        Get the artist tags of the post.

        Returns:
            set[str]: The artist tags as a set of strings.
        """
        ...

    @abstractproperty
    def tags_copyright(self) -> set[str]:
        """
        Get the copyright tags of the post.

        Returns:
            set[str]: The copyright tags as a set of strings.
        """
        ...

    @abstractproperty
    def tags_character(self) -> set[str]:
        """
        Get the character tags of the post.

        Returns:
            set[str]: The character tags as a set of strings.
        """
        ...

    @abstractproperty
    def tags_meta(self) -> set[str]:
        """
        Get the meta tags of the post.

        Returns:
            set[str]: The meta tags as a set of strings.
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
    def file_summary(self) -> URLFileSummary:
        """
        Get the file summary of the post.

        Returns:
            URLFileSummary: The file summary as a URLFileSummary object.
        """
        ...


class TagsNotCategorised:
    """
    A class providing post method implementations for boorus with uncategorised tags.
    """

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


class CommonInfo:
    """
    A class providing post method implementations for common info found on Booru APIs.

    Attributes:
        id (int): The post ID.
        rating (str | None): The rating of the post.
        file_url (str): The URL of the file.
        file_ext (str): The file extension.
    """

    id: int
    rating: str
    file_url: str
    file_ext: str

    @property
    def rating_full(self) -> str | None:
        """
        Get the full named rating of the post.

        Returns:
            set[str]: The full rating strings.
        """
        return RATING.full(self.rating) if self.rating else None

    @property
    def rating_simple(self) -> str | None:
        """
        Get the simple named rating of the post.

        Without the "rating:" part.

        Returns:
            set[str]: The simple rating strings.
        """
        return RATING.simple(self.rating) if self.rating else None

    @property
    def best_file_url(self) -> str:
        """
        Get the best file URL of the post.

        Returns:
            str: The best file URL as a string.
        """
        return self.file_url

    @property
    def filename(self) -> str:
        """
        Get the filename of the post.

        Returns:
            str: The filename as a string.
        """
        return f"{self.id}.{self.file_ext}"
