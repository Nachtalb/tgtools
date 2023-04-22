from typing import Generic, Type

from aiohttp import BasicAuth, ClientSession

from tgtools.api.booru.base import BooruApi, T_Post
from tgtools.utils.urls.builder import URLTemplateBuilder


class V1Api(Generic[T_Post], BooruApi[T_Post]):
    """
    A class to interact with the V1 API.

    Attributes:
        session (ClientSession): An aiohttp ClientSession.
        auth (BasicAuth | None): Basic authentication object.
        url (URL): The base URL for the V1 API.
    """

    def __init__(
        self,
        host: str,
        session: ClientSession,
        _post_class: Type[T_Post],
        auth: BasicAuth | None = None,
    ):
        super().__init__(host=host, session=session, _post_class=_post_class, auth=auth)

        self._post_url = URLTemplateBuilder(f"{self.url}/post.json?tags=id:{{id}}")
        self._posts_url = URLTemplateBuilder(f"{self.url}/post.json")

    async def post(self, id: int) -> T_Post | None:
        """
        Retrieve a single post from the API by its ID.

        Args:
            id (int): The ID of the post to retrieve.

        Returns:
            T_Post | None: A Post instance if found, or None if not found.
        """
        url = self._post_url.url(id=id).build()
        if (post := await self._request(url)) and isinstance(post, list):
            return self._convert_post(post[0])
        return None
