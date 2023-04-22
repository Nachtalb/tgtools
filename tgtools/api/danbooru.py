from typing import Any

from aiohttp import BasicAuth, ClientSession

from tgtools.api import HOSTS
from tgtools.api.booru_api import BooruApi
from tgtools.models.danbooru_post import DanbooruPost
from tgtools.utils.urls.builder import URLTemplateBuilder


class DanbooruApi(BooruApi[DanbooruPost]):
    """
    A class to interact with the Danbooru API.

    Attributes:
        session (ClientSession): An aiohttp ClientSession.
        auth (BasicAuth | None): Basic authentication object.
        url (URL): The base URL for the Danbooru API.
        user (str): The Danbooru username.
        key (str): The Danbooru API key.
    """

    def __init__(self, session: ClientSession | None = None, auth: BasicAuth | None = None, host: str = HOSTS.danbooru):
        super().__init__(session, auth, host)
        self._post_url = URLTemplateBuilder(f"{self.url}/posts/{{id}}.json")
        self._posts_url = URLTemplateBuilder(f"{self.url}/posts.json")

    def _convert_post(self, data: dict[str, Any]) -> DanbooruPost:
        """
        Convert the API response data into a Post instance.

        Args:
            data (dict[str, Any]): The API response data.

        Returns:
            Post: A Post instance created from the data.
        """
        post = DanbooruPost.parse_obj(data)
        post._api = self
        return post
