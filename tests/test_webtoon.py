from __future__ import annotations

import pytest

from wtyt.webtoon import Canvas, Comic, ComicId, Original


@pytest.mark.parametrize(
    ("link", "ex_no", "ex_rss"),
    [
        (
            "https://www.webtoons.com/en/thriller/hand-jumper/list?title_no=2702",
            Original(2702),
            "https://www.webtoons.com/en/thriller/hand-jumper/rss?title_no=2702",
        ),
        (
            "https://www.webtoons.com/en/canvas/wolfhunt/list?title_no=985684",
            Canvas(985684),
            "https://www.webtoons.com/en/challenge/wolfhunt/rss?title_no=985684",
        ),
    ],
)
def test_webtoon(link: str, ex_no: ComicId, ex_rss: str) -> None:
    no = ComicId.from_link(link)
    assert no == ex_no
    rss = Comic.get(no).rss
    assert rss == ex_rss
