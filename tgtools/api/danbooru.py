from io import BytesIO
from pathlib import Path
from typing import Any

from aiohttp import BasicAuth, ClientError, ClientSession
from aiopath import AsyncPath
from yarl import URL

from tgtools.api import HOSTS
from tgtools.models.danbooru import Post


class DanbooruError(ClientError):
    pass


class DanbooruApi:
    def __init__(
        self,
        session: ClientSession | None = None,
        user: str = "",
        api_key: str = "",
        host: str = HOSTS.danbooru,
    ):
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

    async def _request(
        self, endpoint: str, query: dict[str, str | int | float] = {}
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        async with self.session.get(self.url / (endpoint + ".json"), params=query, auth=self.auth) as response:
            data = await response.json()
            if data.get("success", True) is False:
                raise DanbooruError(data.get("error"), data.get("message"))
        return data

    def _post(self, data: dict[str, Any]) -> Post:
        post = Post.parse_obj(data)
        post._api = self
        return post

    async def posts(self, limit: int = 10, tags: list[str] = []) -> list[Post]:
        if (posts := await self._request("posts", {"limit": limit, "tags": " ".join(tags)})) and isinstance(
            posts, list
        ):
            return list(map(self._post, posts))
        return []

    async def post(self, id: int) -> Post | None:
        if (post := await self._request(f"posts/{id}")) and isinstance(post, dict):
            return self._post(post)

    async def download(self, url: str, out: Path | None = None) -> Path | BytesIO:
        async with self.session.get(url) as response:
            if out:
                aio_path = AsyncPath(out)
                await aio_path.write_bytes(await response.content.read())
                return out
            return BytesIO(await response.content.read())
