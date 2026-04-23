from __future__ import annotations

import csv
import re
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from functools import cache
from typing import TYPE_CHECKING, Self

# TODO(GideonBear): contribute upstream  # noqa: FIX002
import browser_cookie3  # type: ignore[import-not-found]
from requests import Session


if TYPE_CHECKING:
    from collections.abc import Iterator


class MediaType(Enum):
    Tv = "tv"
    Season = "season"
    Episode = "episode"
    Movie = "movie"
    Anime = "anime"
    Manga = "manga"
    Game = "game"
    Book = "book"
    Comic = "comic"
    Boardgame = "boardgame"


class Status(Enum):
    Completed = "Completed"
    InProgress = "In progress"
    Planning = "Planning"
    Paused = "Paused"
    Dropped = "Dropped"


class Source(Enum):
    Tmdb = "tmdb"
    Mal = "mal"
    Mangaupdates = "mangaupdates"
    Igdb = "igdb"
    Openlibrary = "openlibrary"
    Hardcover = "hardcover"
    Comicvine = "comicvine"
    Manual = "manual"


class Api:
    def __init__(self, url: str) -> None:
        self.url = url
        self.session = Session()
        self.session.cookies.update(
            browser_cookie3.chrome(
                domain_name=url.split("/")[2].split(":", maxsplit=1)[0]
            )
        )

    @cache  # noqa: B019
    def get_csrf(self) -> str:
        url = urllib.parse.urljoin(self.url, "create")
        r = self.session.get(url)
        r.raise_for_status()
        match = re.search(r'name="csrfmiddlewaretoken" value="([a-zA-Z0-9]+)"', r.text)
        if match is None:
            msg = "Couldn't find csrf token, are you logged in?"
            raise Exception(msg)  # noqa: TRY002
        return match.group(1)

    def create(
        self,
        media_type: MediaType,
        title: str,
        image_url: str,
        status: Status,
        notes: str | None = None,
    ) -> None:
        url = urllib.parse.urljoin(self.url, "create")
        data: dict[str, str | int] = {
            "csrfmiddlewaretoken": self.get_csrf(),
            "media_type": media_type.value,
            "title": title,
            "image": image_url,
            "status": status.value,
            "notes": notes or "",
            "season_number": 1,
            "episode_number": 1,
            "score": "",
            "progress": 0,
            "start_date": "",
            "end_date": "",
        }
        r = self.session.post(url, data=data)
        r.raise_for_status()

    def export(self) -> Iterator[ExportRow]:
        url = urllib.parse.urljoin(
            self.url, f"export/csv?csrfmiddlewaretoken={self.get_csrf()}"
        )
        r = self.session.get(url)
        r.raise_for_status()
        reader = csv.reader(r.text.splitlines(keepends=True))
        next(reader)  # header
        return map(ExportRow.from_row, reader)


@dataclass
class ExportRow:
    media_id: str
    source: Source
    media_type: MediaType
    title: str
    image: str
    season_number: int | None
    episode_number: int | None
    score: Decimal | None
    status: Status | None
    notes: str
    start_date: datetime | None
    end_date: datetime | None
    progress: str
    created_at: datetime
    progressed_at: datetime | None

    @classmethod
    def from_row(cls, row: list[str]) -> Self:
        (
            media_id,
            source,
            media_type,
            title,
            image,
            season_number,
            episode_number,
            score,
            status,
            notes,
            start_date,
            end_date,
            progress,
            created_at,
            progressed_at,
        ) = row
        return cls(
            media_id=media_id,
            source=Source(source),
            media_type=MediaType(media_type),
            title=title,
            image=image,
            season_number=int(season_number) if season_number else None,
            episode_number=int(episode_number) if episode_number else None,
            score=Decimal(score) if score else None,
            status=Status(status) if status else None,
            notes=notes,
            start_date=datetime.fromisoformat(start_date) if start_date else None,
            end_date=datetime.fromisoformat(end_date) if end_date else None,
            progress=progress,
            created_at=datetime.fromisoformat(created_at),
            progressed_at=datetime.fromisoformat(progressed_at)
            if progressed_at
            else None,
        )
