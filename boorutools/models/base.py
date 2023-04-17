from io import BytesIO
from pathlib import Path
from typing import Callable
from pydantic import BaseModel

from pydantic.dataclasses import dataclass


class Summary(BaseModel):
    file_name: Path
    size: int
    height: int
    width: int
    download_method: Callable

    @property
    def ratio_wh(self):
        return self.width / self.height

    @property
    def ratio_hw(self):
        return self.height / self.width

    @property
    def file_ext(self):
        return self.file_name.suffix[1:]

    @property
    def is_image(self) -> bool:
        return self.file_ext in ["jpg", "jpeg", "png", "webp"]

    @property
    def is_gif(self) -> bool:
        return self.file_ext == "gif"

    @property
    def is_video(self) -> bool:
        return self.file_ext in ["mp4", "webm", "mkv"]


class FileSummary(Summary):
    file: BytesIO

    class Config:
        arbitrary_types_allowed = True


class URLFileSummary(Summary):
    url: str
