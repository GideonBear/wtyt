from __future__ import annotations

import json
import subprocess

import requests

from wtyt import config, yamtrack
from wtyt.notes import parse_notes
from wtyt.yamtrack import MediaType, Source, Status


ytapi = yamtrack.Api(config.yamtrack_url)


def main() -> int:
    urls = [
        note_data["rss"]
        for x in ytapi.export()
        if x.source == Source.Manual
        and x.media_type == MediaType.Comic
        and x.status == Status.Completed
        and (note_data := parse_notes(x.notes)) is not None
    ]
    contents = json.dumps({"urls": urls})

    filename = "comics-rss.txt"
    auth = (
        subprocess
        .run(("rbw", "get", "rustypaste"), stdout=subprocess.PIPE, check=True)
        .stdout.decode()
        .strip()
    )
    requests.delete(
        f"{config.rustypaste_url}/{filename}", headers={"Authorization": auth}
    )
    requests.post(
        config.rustypaste_url,
        headers={"Authorization": auth, "filename": filename},
        files={"file": contents},
    )

    return 0
