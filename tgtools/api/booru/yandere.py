from aiohttp import BasicAuth, ClientSession

from tgtools.api.booru import HOSTS, V1Api
from tgtools.models.booru import YanderePost


class YandereApi(V1Api[YanderePost]):
    """
    A class to interact with the Yandere API.

    Attributes:
        session (ClientSession): An aiohttp ClientSession.
        url (URL): The base URL for the API, defaults to HOSTS.yandere in tgtools.api
        auth (BasicAuth | None): Basic authentication object.
    """

    def __init__(self, session: ClientSession, host: str = HOSTS.yandere, auth: BasicAuth | None = None):
        super().__init__(host=host, session=session, auth=auth, _post_class=YanderePost)
