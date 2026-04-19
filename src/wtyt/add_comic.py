from __future__ import annotations

import argparse
import subprocess
from argparse import ArgumentParser

from wtyt import config, yamtrack
from wtyt.webtoon import Comic, ComicId
from wtyt.yamtrack import MediaType, Status


ytapi = yamtrack.Api(config.yamtrack_url)
CATBOX_HASH = (
    subprocess
    .run(("rbw", "get", "catbox hash"), check=True, stdout=subprocess.PIPE)
    .stdout.decode()
    .strip()
)


class Args(argparse.Namespace):
    link: str
    # status: Status


def parse_args() -> Args:
    parser = ArgumentParser()
    parser.add_argument("link", type=str)
    # group = parser.add_mutually_exclusive_group(required=True)
    # group.add_argument(
    #     "-c", "--completed", action="store_const", dest="status",
    #     const=Status.Completed
    # )
    # group.add_argument(
    #     "-i",
    #     "--in-progress",
    #     action="store_const",
    #     dest="status",
    #     const=Status.InProgress,
    # )
    # group.add_argument(
    #     "-p", "--planning", action="store_const", dest="status", const=Status.Planning
    # )
    # group.add_argument(
    #     "-a", "--paused", action="store_const", dest="status", const=Status.Paused
    # )
    # group.add_argument(
    #     "-d", "--dropped", action="store_const", dest="status", const=Status.Dropped
    # )
    return parser.parse_args(namespace=Args())


def main() -> int:
    args = parse_args()

    comic = Comic.get(ComicId.from_link(args.link))
    notes = f"link: {comic.link}\nrss: {comic.rss}"
    ytapi.create(
        media_type=MediaType.Comic,
        title=comic.title,
        image_url=comic.store_thumb(CATBOX_HASH),
        status=Status.Planning,
        notes=notes,
    )

    return 0
