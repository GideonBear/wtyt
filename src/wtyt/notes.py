from __future__ import annotations


HEADER = "Structured data follows. If you want to add a note, add it above this line."


def make_notes(data: dict[str, str]) -> str:
    for key in data:
        if ":" in key:
            msg = f"Bad key '{key}' for make_notes. Avoid colons."
            raise ValueError(msg)
    return "\n".join([HEADER] + [f"{k}: {v}" for k, v in data.items()])


def parse_notes(notes: str) -> dict[str, str] | None:
    data = {}
    lines = iter(notes.splitlines())
    for line in lines:
        if line == HEADER:
            break
    else:
        return None

    for line in lines:
        k, v = line.split(": ", maxsplit=1)
        data[k] = v

    return data
