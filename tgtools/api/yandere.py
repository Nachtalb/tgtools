from typing import Any

from aiohttp import BasicAuth, ClientSession

from tgtools.api import HOSTS
from tgtools.api.booru_api import BooruApi
from tgtools.models.yandere_post import YanderePost
from tgtools.utils.urls.builder import URLTemplateBuilder


class YandereApi(BooruApi[YanderePost]):
    """
    A class to interact with the Yandere API.

    Attributes:
        session (ClientSession): An aiohttp ClientSession.
        auth (BasicAuth | None): Basic authentication object.
        url (URL): The base URL for the Yandere API.
    """

    def __init__(self, session: ClientSession | None = None, auth: BasicAuth | None = None, host: str = HOSTS.yandere):
        super().__init__(session, auth, host)
        self._post_url = URLTemplateBuilder(f"{self.url}/post.json?tags=id:{{id}}")
        self._posts_url = URLTemplateBuilder(f"{self.url}/post.json")

    def _convert_post(self, data: dict[str, Any]) -> YanderePost:
        """
        Convert the API response data into a Post instance.

        Args:
            data (dict[str, Any]): The API response data.

        Returns:
            Post: A Post instance created from the data.
        """
        post = YanderePost.parse_obj(data)
        post._api = self
        return post
