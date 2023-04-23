from aiohttp import BasicAuth, ClientSession

from tgtools.api.booru import HOSTS
from tgtools.api.booru.base import BooruApi, BooruError
from tgtools.models.booru import DanbooruPost
from tgtools.utils.misc import BooruJSON
from tgtools.utils.urls.builder import RequestDict, URLTemplateBuilder


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

    def __init__(self, session: ClientSession, auth: BasicAuth | None = None, host: str = HOSTS.danbooru):
        super().__init__(host=host, session=session, _post_class=DanbooruPost, auth=auth)
        self._post_url = URLTemplateBuilder(f"{self.url}/posts/{{id}}.json")
        self._posts_url = URLTemplateBuilder(f"{self.url}/posts.json")

    async def _request(self, request: RequestDict) -> BooruJSON | None:
        """
        Make a request to the API.

        Args:
            request (RequestDict): The request dictionary for an aiohttp ClientSession request.

        Returns:
            JSON | None: The API response as a dictionary or list of dictionaries, or None if no data is returned.

        Raises:
            BooruError: If the API call is unsuccessful.
        """
        data = await super()._request(request)
        if isinstance(data, dict) and data.get("success", True) is False:
            raise BooruError(data.get("error"), data.get("message"))
        return data
