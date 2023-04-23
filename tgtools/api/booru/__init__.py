from tgtools.api.booru.danbooru import DanbooruApi
from tgtools.api.booru.v1 import V1Api, YandereApi

__all__ = ["YandereApi", "DanbooruApi", "V1Api"]


class HOSTS:
    danbooru = "https://danbooru.donmai.us"
    yandere = "https://yande.re"
