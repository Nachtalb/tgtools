from dataclasses import dataclass
from tgtools.api.booru.danbooru import DanbooruApi
from tgtools.api.booru.v1 import V1Api, YandereApi

__all__ = ["YandereApi", "DanbooruApi", "V1Api"]


class HOSTS:
    danbooru = "https://danbooru.donmai.us"
    yandere = "https://yande.re"
    gelbooru = "https://gelbooru.com"
    threedbooru = "http://behoimi.org/"


@dataclass
class MinorVersion:
    post_api_path: str
    posts_api_path: str
    post_gui_path: str


class GelbooruStyleVersion(MinorVersion):
    post_api_path = "/index.php?page=dapi&s=post&q=index&json=1&id={id}"
    posts_api_path = "/index.php?page=dapi&s=post&q=index&json=1"
    post_gui_path = "index.php?page=post&s=view&id={id}"


class YandereStyleVersion(MinorVersion):
    post_api_path = "/post.json?tags=id:{id}"
    posts_api_path = "/post.json"
    post_gui_path = "post/show/{id}"
