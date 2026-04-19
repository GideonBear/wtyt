from __future__ import annotations

import urllib.parse
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self, TypedDict

import requests

# TODO(GideonBear): contribute upstream  # noqa: FIX002
from catbox_api import catboxAPI  # type: ignore[import-not-found]

# TODO(GideonBear): contribute upstream  # noqa: FIX002
from webtoon_api import WebtoonApi  # type: ignore[import-not-found]


if TYPE_CHECKING:
    # TODO(GideonBear): contribute upstream  # noqa: FIX002
    from webtoon_api.webtoon_api import WebtoonApiCall  # type: ignore[import-not-found]


wtapi = WebtoonApi()


@dataclass
class ComicId(ABC):
    no: int

    @property
    @abstractmethod
    def method(self) -> WebtoonApiCall: ...

    @classmethod
    def from_link(cls, link: str) -> ComicId:
        typ: type[ComicId] = (
            Canvas if link.split("/", maxsplit=5)[4] == "canvas" else Original
        )
        return typ(int(link.rsplit("=", 1)[1]))


class Original(ComicId):
    method = wtapi.titleInfo


class Canvas(ComicId):
    method = wtapi.challengeTitleInfo


class TitleInfo(TypedDict):
    title: str
    thumbnail: str
    linkUrl: str


@dataclass
class Comic:
    _data: TitleInfo

    @classmethod
    def get(cls, no: ComicId) -> Self:
        data = no.method(
            titleNo=no.no,
            serviceZone="GLOBAL",
            language="en",
            platform="APP_ANDROID",
        )
        return cls(data["titleInfo"])

    @property
    def title(self) -> str:
        return self._data["title"]

    def store_thumb(self, catbox_hash: str) -> str:
        with requests.get(
            urllib.parse.urljoin(
                "https://webtoon-phinf.pstatic.net", self._data["thumbnail"]
            ),
            headers={
                "Referer": "http://m.webtoons.com/",
                "User-Agent": "nApps (Android 13; linewebtoon; 2.12.2)",
            },
            stream=True,
        ) as r:
            r.raise_for_status()
            file_id = catboxAPI(catbox_hash).upload_file("img.jpeg", r.raw)
        return f"https://files.catbox.moe/{file_id}"

    @property
    def link(self) -> str:
        return self._data["linkUrl"]

    @property
    def rss(self) -> str:
        a, b = self.link.rsplit("/", maxsplit=1)
        _, b = b.split("?")
        return f"{a}/rss?{b}"
