from io import BytesIO
from pathlib import Path
from typing import Any, Union

from aiohttp import BasicAuth, ClientError, ClientSession
from aiopath import AsyncPath
from yarl import URL

from tgtools.api import HOSTS
from tgtools.models.danbooru import Post


class DanbooruError(ClientError):
    """
    Custom error class for Danbooru API errors.
    """

    pass


JSON = Union[dict[str, Any], list[dict[str, Any]]]


class DanbooruApi:
    """
    A class to interact with the Danbooru API.

    Attributes:
        session (ClientSession): An aiohttp ClientSession.
        auth (BasicAuth | None): Basic authentication object.
        url (URL): The base URL for the Danbooru API.
        user (str): The Danbooru username.
        key (str): The Danbooru API key.
    """

    def __init__(
        self,
        session: ClientSession | None = None,
        user: str = "",
        api_key: str = "",
        host: str = HOSTS.danbooru,
    ):
        """
        Initialise a DanbooruApi instance.

        Args:
            session (ClientSession | None): An aiohttp ClientSession. If None, a new session will be created.
            user (str): The Danbooru username.
            api_key (str): The Danbooru API key.
            host (str): The base URL for the Danbooru API.

        Raises:
            ValueError: If only one of the user and api_key is provided.
        """
        self.session = session or ClientSession()

        self.auth = None
        if user and api_key:
            self.auth = BasicAuth(user, api_key)
        elif (user and not api_key) or (not user and api_key):
            raise ValueError("Either set both user and api_key or neither")

        self.url = URL(host)
        self.user = user
        self.key = api_key

    async def close(self):
        await self.session.close()

    async def _request(self, endpoint: str, query: dict[str, str | int | float] = {}) -> JSON | None:
        """
        Make a request to the Danbooru API.

        Args:
            endpoint (str): The API endpoint to call.
            query (dict[str, str | int | float]): The query parameters to pass.

        Returns:
            JSON | None: The API response as a dictionary or list of dictionaries, or None if no data is returned.

        Raises:
            DanbooruError: If the API call is unsuccessful.
        """
        async with self.session.get(self.url / (endpoint + ".json"), params=query, auth=self.auth) as response:
            data = await response.json()
            if data.get("success", True) is False:
                raise DanbooruError(data.get("error"), data.get("message"))
        return data

    def _post(self, data: dict[str, Any]) -> Post:
        """
        Convert the API response data into a Post instance.

        Args:
            data (dict[str, Any]): The API response data.

        Returns:
            Post: A Post instance created from the data.
        """
        post = Post.parse_obj(data)
        post._api = self
        return post

    async def posts(self, limit: int = 10, tags: list[str] = []) -> list[Post]:
        """
        Retrieve a list of posts from the Danbooru API.

        Args:
            limit (int): The maximum number of posts to retrieve.
            tags (list[str]): A list of tags to filter the posts by.

        Returns:
            list[Post]: A list of Post instances.
        """
        if (posts := await self._request("posts", {"limit": limit, "tags": " ".join(tags)})) and isinstance(
            posts, list
        ):
            return list(map(self._post, posts))
        return []

    async def post(self, id: int) -> Post | None:
        """
        Retrieve a single post from the Danbooru API by its ID.

        Args:
            id (int): The ID of the post to retrieve.

        Returns:
            Post | None: A Post instance if found, or None if not found.
        """
        if (post := await self._request(f"posts/{id}")) and isinstance(post, dict):
            return self._post(post)

    async def download(self, url: str, out: Path | None = None) -> Path | BytesIO:
        """
        Download a file from the given URL.

        Args:
            url (str): The URL of the file to download.
            out (Path | None): The output path to save the file to. If None, the file will be returned as a BytesIO object.

        Returns:
            Path | BytesIO: The output path of the downloaded file, or a BytesIO object containing the file data.
        """
        async with self.session.get(url) as response:
            if out:
                aio_path = AsyncPath(out)
                await aio_path.write_bytes(await response.content.read())
                return out
            return BytesIO(await response.content.read())
