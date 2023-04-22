from abc import ABCMeta, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Any, AsyncGenerator, Generic, TypeVar, Union

from aiohttp import BasicAuth, ClientError, ClientSession
from aiopath import AsyncPath
from yarl import URL

from tgtools.models.booru_post import BooruPost
from tgtools.utils.urls.builder import RequestDict, URLTemplateBuilder

T_Post = TypeVar("T_Post", bound=BooruPost)


class BooruError(ClientError):
    """
    Custom error class for the API errors.
    """

    pass


JSON = Union[dict[str, Any], list[dict[str, Any]]]


class BooruApi(Generic[T_Post], metaclass=ABCMeta):
    """
    A class to interact with the API.

    Attributes:
        session (ClientSession): An aiohttp ClientSession.
        auth (BasicAuth | None): Basic authentication object.
        url (URL): The base URL for the API.
    """

    _post_url = URLTemplateBuilder("https://example.com/post/{id}.json")
    _posts_url = URLTemplateBuilder("https://example.com/posts.json")

    def __init__(
        self,
        session: ClientSession | None = None,
        auth: BasicAuth | None = None,
        host: str = "",
    ):
        """
        Initialise a DanbooruApi instance.

        Args:
            session (ClientSession | None): An aiohttp ClientSession. If None, a new session will be created.
            auth (BasicAuth | None): Basic authentication object.
            host (str): The base URL for the Danbooru API.

        Raises:
            ValueError: If only one of the user and api_key is provided.
        """
        self.session = session or ClientSession()

        self.url = URL(host)
        self.auth = auth

    async def close(self):
        await self.session.close()

    async def _request(self, request: RequestDict) -> JSON | None:
        """
        Make a request to the API.

        Args:
            request (RequestDict): The request dictionary for an aiohttp ClientSession request.

        Returns:
            JSON | None: The API response as a dictionary or list of dictionaries, or None if no data is returned.

        Raises:
            BooruError: If the API call is unsuccessful.
        """
        async with self.session.request(**request, auth=self.auth) as response:
            data = await response.json()
            if data.get("success", True) is False:
                raise BooruError(data.get("error"), data.get("message"))
        return data

    @abstractmethod
    def _convert_post(self, data: dict[str, Any]) -> T_Post:
        """
        Convert the API response data into a Post instance.

        Args:
            data (dict[str, Any]): The API response data.

        Returns:
            T_Post: A Post instance created from the data.
        """
        ...

    async def posts(self, tags: list[str] = [], limit: int = 10) -> list[T_Post]:
        """
        Retrieve a list of posts from the API.

        Args:
            tags (list[str]): A list of tags to filter the posts by.
            limit (int): The maximum number of posts to retrieve.

        Returns:
            list[T_Post]: A list of Post instances.
        """
        url = self._posts_url.url().query(limit=limit, tags=" ".join(tags)).build()
        if (posts := await self._request(url)) and isinstance(posts, list):
            return list(map(self._convert_post, posts))
        return []

    async def post(self, id: int) -> T_Post | None:
        """
        Retrieve a single post from the API by its ID.

        Args:
            id (int): The ID of the post to retrieve.

        Returns:
            T_Post | None: A Post instance if found, or None if not found.
        """
        url = self._post_url.url(id=id).build()
        if (post := await self._request(url)) and isinstance(post, dict):
            return self._convert_post(post)

    async def download(self, url: str, out: Path | None = None) -> Path | BytesIO:
        """
        Download a file from the given URL.

        Args:
            url (str): The URL of the file to download.
            out (Path | None): The output path to save the file to. If None, the file will be returned as a
                               BytesIO object.

        Returns:
            Path | BytesIO: The output path of the downloaded file, or a BytesIO object containing the file data.
        """
        async with self.session.get(url, auth=self.auth) as response:
            if out:
                aio_path = AsyncPath(out)
                await aio_path.write_bytes(await response.content.read())
                return out
            return BytesIO(await response.content.read())

    async def iter_download(
        self, url: str, out: Path | None = None, chunk_size: int = 1024 * 1024
    ) -> AsyncGenerator[BytesIO | Path, None]:
        """
        Download a file from the given URL in chunks.

        Args:
            url (str): The URL of the file to download.
            out (Path | None): The output path to save the file to. If None, the file will be returned as a BytesIO
                               object.
            chunk_size (int, optional): The size of the chunks to download. Defaults to 1024 * 1024.

        Yields:
            AsyncGenerator[BytesIO | Path, None]: The downloaded file as a BytesIO object if no output path is
                                                  provided, otherwise the output path, in chunks.
        """
        async with self.session.get(url, auth=self.auth) as response:
            if out:
                aio_path = AsyncPath(out)
                async with aio_path.open("wb") as file:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await file.write(chunk)
                        yield out
            else:
                buffer = BytesIO()
                async for chunk in response.content.iter_chunked(chunk_size):
                    buffer.write(chunk)
                    buffer.seek(0)
                    yield buffer
                    buffer.seek(0, 2)  # Go to end of fil
