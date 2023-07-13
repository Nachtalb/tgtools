from pydantic import field_validator

from tgtools.models.booru.yandere import YanderePost


class ThreeDBooruPost(YanderePost):
    @field_validator("created_at", mode="before")
    @classmethod
    def created_at_extraction(cls, v: dict[str, int]) -> int:
        return v["s"]
