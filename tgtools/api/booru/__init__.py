from tgtools.api.booru.danbooru import DanbooruApi
from tgtools.api.booru.v1 import V1Api
from tgtools.api.booru.yandere import YandereApi

__all__ = ["YandereApi", "DanbooruApi", "V1Api"]


class HOSTS:
    danbooru = "https://danbooru.donmai.us"
    yandere = "https://yande.re"
