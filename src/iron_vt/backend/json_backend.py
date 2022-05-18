import json
import pathlib
import dataclasses
import base64
import contextlib

from typing import Dict, Literal, TypedDict, Mapping


from iron_vt.vault import IronValutError, Entry

# region IO Helper

_Mode = Literal["rt", "wt"]


@contextlib.contextmanager
def _open(p: pathlib.Path, mode: _Mode):
    with p.open(mode=mode) as fp:
        yield fp


# endregion


# region Base64 Encoding


def _b64decode_field(line: str):
    return base64.b64decode(line.encode("utf-8"))


def _b64encode_field(line: bytes):
    return base64.b64encode(line).decode("utf-8")


def _b64decode_file(line: str):
    return base64.b64decode(line.encode("utf-8")).decode("utf-8")


def _b64encode_file(line: str):
    return base64.b64encode(line.encode("utf-8")).decode("utf-8")


# endregion


# region JSON Types


class JSONEntry(TypedDict):
    salt: str
    token: str


JSONSafe = Dict[str, JSONEntry]

# endregion


def load(path: pathlib.Path, b64_encode: bool):
    with _open(path, "rt") as fp:
        if b64_encode:
            safe_dct: JSONSafe = json.loads(_b64decode_file(fp.read()))
        else:
            safe_dct: JSONSafe = json.loads(fp.read())

    return {
        name: Entry(
            salt=_b64decode_field(entry_dct["salt"]),
            token=_b64decode_field(entry_dct["token"]),
        )
        for name, entry_dct in safe_dct.items()
    }


def save(path: pathlib.Path, b64_encode: bool, entries: Mapping[str, Entry]):
    json_entries: JSONSafe = {
        name: {
            "salt": _b64encode_field(entry.salt),
            "token": _b64encode_field(entry.token),
        }
        for name, entry in entries.items()
    }

    if b64_encode:
        data = _b64encode_file(json.dumps(json_entries, indent=4))
    else:
        data = json.dumps(json_entries, indent=4)

    with _open(path, "wt") as fp:
        fp.write(data)


def safe_path(path: pathlib.Path, safe_name: str, b64_encode: bool):
    suffix = ".b64" if b64_encode else ".json"
    safe_path = path.joinpath(safe_name).with_suffix(suffix)
    if safe_path.parent != path:
        raise IronValutError(f"invalid safe name {safe_name}")
    return safe_path


@dataclasses.dataclass
class JSONBackend:

    path: pathlib.Path
    b64_encode: bool = True

    def _safe_path(self, safe_name: str):
        return safe_path(self.path, safe_name, self.b64_encode)

    def load(self, name: str):
        safe_path = self._safe_path(name)
        return load(safe_path, self.b64_encode)

    def save(self, name: str, entries: Mapping[str, Entry]):
        safe_path = self._safe_path(name)
        save(safe_path, self.b64_encode, entries)

    def exists(self, name: str):
        safe_path = self._safe_path(name)
        return safe_path.exists() and safe_path.is_file()
