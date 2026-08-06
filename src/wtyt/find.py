from __future__ import annotations

import argparse
from argparse import ArgumentParser
from typing import TYPE_CHECKING

from wtyt import config, yamtrack
from wtyt.notes import parse_notes
from wtyt.webtoon import Canvas, ComicId, Original
from wtyt.yamtrack import MediaType, Source, Status


if TYPE_CHECKING:
    from collections.abc import Sequence


ytapi = yamtrack.Api(config.yamtrack_url)


class Args(argparse.Namespace):
    status: Sequence[Status]
    typ: type[ComicId] | None


def parse_args() -> Args:
    parser = ArgumentParser()

    status = parser.add_argument_group(
        "status", "supply any number of statuses to search for"
    )
    status.add_argument(
        "-c",
        "--completed",
        action="append_const",
        dest="status",
        const=Status.Completed,
    )
    status.add_argument(
        "-i",
        "--in-progress",
        action="store_const",
        dest="status",
        const=Status.InProgress,
    )
    status.add_argument(
        "-p", "--planning", action="append_const", dest="status", const=Status.Planning
    )
    status.add_argument(
        "-a", "--paused", action="append_const", dest="status", const=Status.Paused
    )
    status.add_argument(
        "-d", "--dropped", action="append_const", dest="status", const=Status.Dropped
    )

    typ = parser.add_argument_group("type").add_mutually_exclusive_group()
    typ.add_argument(
        "-o", "--original", action="store_const", dest="typ", const=Original
    )
    typ.add_argument("-v", "--canvas", action="store_const", dest="typ", const=Canvas)

    return parser.parse_args(namespace=Args())


def main() -> int:
    args = parse_args()

    urls = [
        note_data["link"]
        for x in ytapi.export()
        if x.source == Source.Manual
        and x.media_type == MediaType.Comic
        and (not args.status or x.status in args.status)
        and (note_data := parse_notes(x.notes)) is not None
    ]

    for url in urls:
        comic = ComicId.from_link(url)
        if args.typ and not isinstance(comic, args.typ):
            continue

        print(url)

    return 0
