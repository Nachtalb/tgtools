from pydantic import validator
from tgtools.models.booru.yandere import YanderePost


class ThreeDBooruPost(YanderePost):
    @validator("created_at", pre=True)
    def created_at_extraction(cls, v: dict[str, int]) -> int:
        return v["s"]
