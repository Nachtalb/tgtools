from aiohttp import BasicAuth, ClientSession

from tgtools.api.booru.constants import HOSTS, GelbooruStyleVersion
from tgtools.api.booru.v1 import V1Api
from tgtools.models.booru.gelbooru import GelbooruPost


class GelbooruApi(V1Api[GelbooruPost]):
    def __init__(
        self,
        session: ClientSession,
        host: str = HOSTS.gelbooru,
        auth: BasicAuth | None = None,
    ):
        super().__init__(
            host=host, session=session, _post_class=GelbooruPost, minor_version=GelbooruStyleVersion, auth=auth
        )

    async def post(self, id: int) -> GelbooruPost | None:
        """
        Retrieve a single post from the API by its ID.

        Args:
            id (int): The ID of the post to retrieve.

        Returns:
            T_Post | None: A Post instance if found, or None if not found.
        """
        url = self._post_url.url(id=id).build()
        if (result := await self._request(url)) and isinstance(result, dict) and (posts := result.get("post")):
            return self._convert_post(posts[0])  # type: ignore
        return None

    async def posts(self, tags: list[str] = [], limit: int = 10) -> list[GelbooruPost]:
        """
        Retrieve a list of posts from the API.

        Args:
            tags (list[str]): A list of tags to filter the posts by.
            limit (int): The maximum number of posts to retrieve.

        Returns:
            list[T_Post]: A list of Post instances.
        """
        url = self._posts_url.url().query(limit=limit, tags=" ".join(tags)).build()
        if (result := await self._request(url)) and isinstance(result, dict) and (posts := result.get("post")):
            return list(map(self._convert_post, posts))  # type: ignore
        return []
