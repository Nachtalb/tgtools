from abc import ABCMeta
from io import BytesIO
from pathlib import Path
from typing import Any, AsyncGenerator, Generic, Type, TypeVar

from aiohttp import BasicAuth, ClientError, ClientSession
from aiopath import AsyncPath
from yarl import URL

from tgtools.models.booru.base import BooruPost
from tgtools.utils.misc import JSONObject, JSONPrimitive
from tgtools.utils.urls.builder import RequestDict, URLTemplateBuilder

T_Post = TypeVar("T_Post", bound=BooruPost)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    " Edg/117.0.2045.31"
)


class BooruError(ClientError):
    """
    Custom error class for the API errors.
    """

    pass


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

    _cls: Type[T_Post]

    def __init__(
        self,
        host: str,
        session: ClientSession,
        _post_class: Type[T_Post],
        auth: BasicAuth | None = None,
    ):
        """
        Initialise a DanbooruApi instance.

        Args:
            host (str): The base URL for the Danbooru API.
            session (ClientSession): An aiohttp ClientSession.
            _post_class (Type[T_Post]): The Post class used for this api.
            auth (BasicAuth, optional): Basic authentication object.
            auth (BasicAuth, optional): Basic authentication object.
        """
        self.session = session

        self.url = URL(host)
        self.auth = auth

        self._post_class = _post_class

    async def _request(self, request: RequestDict) -> JSONObject | None:
        """
        Make a request to the API.

        Args:
            request (RequestDict): The request dictionary for an aiohttp ClientSession request.

        Returns:
            JSON | None: The API response as a dictionary or list of dictionaries, or None if no data is returned.
        """
        async with self.session.request(
            **request, auth=self.auth, headers={"User-Agent": DEFAULT_USER_AGENT}
        ) as response:
            data = await response.json()
            return data  # type: ignore[no-any-return]

    def _convert_post(self, data: dict[str, JSONPrimitive]) -> T_Post:
        """
        Convert the API response data into a Post instance.

        Args:
            data (dict[str, Any]): The API response data.

        Returns:
            T_Post: A Post instance created from the data.
        """
        post = self._post_class.parse_obj(data)
        post.set_api(self)
        return post

    async def posts(self, tags: list[str] = [], limit: int = 10, page: int = 0, **api_kwargs: Any) -> list[T_Post]:
        """
        Retrieve a list of posts from the API.

        Args:
            tags (list[str]): A list of tags to filter the posts by.
            limit (int): The maximum number of posts to retrieve.

        Returns:
            list[T_Post]: A list of Post instances.
        """
        url = self._posts_url.url().query(limit=limit, tags=" ".join(tags), page=page, **api_kwargs).build()
        if (posts := await self._request(url)) and isinstance(posts, list):
            return list(map(self._convert_post, posts))  # pyright: ignore
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
            return self._convert_post(post)  # type: ignore
        return None

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
