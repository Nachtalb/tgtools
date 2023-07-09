from types import new_class
from typing import Generic, Type

from aiohttp import BasicAuth, ClientSession

from tgtools.api.booru.base import BooruApi, T_Post
from tgtools.constants import HOSTS, MinorVersion, YandereStyleVersion
from tgtools.models.booru.threedbooru import ThreeDBooruPost
from tgtools.models.booru.yandere import YanderePost
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
        minor_version: Type[MinorVersion] = YandereStyleVersion,
        auth: BasicAuth | None = None,
    ):
        super().__init__(host=host, session=session, _post_class=_post_class, auth=auth)

        self.minor_version = minor_version

        self._post_url = URLTemplateBuilder(f"{self.url}/{minor_version.post_api_path}")
        self._posts_url = URLTemplateBuilder(f"{self.url}/{minor_version.posts_api_path}")

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
            return self._convert_post(post[0])  # pyright: ignore[reportGeneralTypeIssues]
        return None


class GenericV1Api(Generic[T_Post], V1Api[T_Post]):
    def __init__(
        self,
        session: ClientSession,
        auth: BasicAuth | None = None,
        host: str = "",
    ) -> None:
        ...


def create_v1_api_subclass(
    class_name: str,
    post_class: Type[T_Post],
    minor_version: Type[MinorVersion],
    default_host: str,
) -> Type[GenericV1Api[T_Post]]:
    def custom_init(
        self: V1Api[T_Post],
        session: ClientSession,
        auth: BasicAuth | None = None,
        host: str = default_host,
    ) -> None:
        V1Api.__init__(
            self,
            host=host,
            session=session,
            _post_class=post_class,
            minor_version=minor_version,
            auth=auth,
        )

    # Define a new class with the provided name, inheriting from V1Api
    cls = new_class(class_name, (GenericV1Api[T_Post],), exec_body=lambda ns: ns.update({"__init__": custom_init}))

    return cls


YandereApi = create_v1_api_subclass("YandereApi", YanderePost, YandereStyleVersion, HOSTS.yandere)
ThreeDBooruApi = create_v1_api_subclass("ThreeDBooruApi", ThreeDBooruPost, YandereStyleVersion, HOSTS.threedbooru)
KonachanApi = create_v1_api_subclass("KonachanApi", YanderePost, YandereStyleVersion, HOSTS.konachan)
