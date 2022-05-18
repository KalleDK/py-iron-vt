import pathlib
import dataclasses
import pytest
import unittest.mock
import unittest

from typing import Mapping

import iron_vt

from iron_vt.backend import json_backend
from iron_vt.vault import Entry


@dataclasses.dataclass
class SafeFixture:
    name: str
    entries: Mapping[str, Entry]
    json_filename: str
    json_file: str
    b64_filename: str
    b64_file: str


@pytest.fixture
def valid_test_safe():
    return SafeFixture(
        name="valid_safe",
        entries={
            "pass1": Entry(salt=b"123", token=b"456"),
            "pass2": Entry(salt=b"123abc", token=b"456def"),
        },
        json_filename="valid_safe.json",
        json_file=""
        "{\n"
        '    "pass1": {\n'
        '        "salt": "MTIz",\n'
        '        "token": "NDU2"\n'
        "    },\n"
        '    "pass2": {\n'
        '        "salt": "MTIzYWJj",\n'
        '        "token": "NDU2ZGVm"\n'
        "    }\n"
        "}",
        b64_filename="valid_safe.b64",
        b64_file=""
        "ewogICAgInBhc3MxIjogewogICAgICAgICJzYWx0"
        "IjogIk1USXoiLAogICAgICAgICJ0b2tlbiI6ICJO"
        "RFUyIgogICAgfSwKICAgICJwYXNzMiI6IHsKICAg"
        "ICAgICAic2FsdCI6ICJNVEl6WVdKaiIsCiAgICAg"
        "ICAgInRva2VuIjogIk5EVTJaR1ZtIgogICAgfQp9",
    )


def test_open_read():
    m = unittest.mock.mock_open(read_data="dummytext")
    with unittest.mock.patch("pathlib.Path.open", m):
        p = pathlib.Path("dummy")
        with json_backend._open(p, "rt") as fp:  # type: ignore
            got = fp.read()
    m.assert_called_once_with(mode="rt")
    assert got == "dummytext"


def test_open_write():
    m = unittest.mock.mock_open()
    with unittest.mock.patch("pathlib.Path.open", m):
        p = pathlib.Path("dummy")
        with json_backend._open(p, "wt") as fp:  # type: ignore
            fp.write("dummytext")
    m.assert_called_once_with(mode="wt")
    handle = m()
    handle.write.assert_called_once_with("dummytext")


@pytest.mark.parametrize(
    "path,name,b64_encode,want,want_exception",
    [
        ("demo", "myname", False, "demo/myname.json", False),
        ("demo", "../myname", False, "demo/myname.json", True),
        ("demo", "myname", True, "demo/myname.b64", False),
    ],
)
def test_get_safe_path(
    path: str, name: str, b64_encode: bool, want: str, want_exception: bool
):
    _path = pathlib.Path(path)
    _want = pathlib.Path(want)
    if want_exception:
        with pytest.raises(iron_vt.IronVaultError):
            json_backend.safe_path(_path, name, b64_encode)
    else:
        got = json_backend.safe_path(_path, name, b64_encode)
        assert got == _want


def test_save_json(valid_test_safe: SafeFixture):
    m = unittest.mock.mock_open()
    with unittest.mock.patch("iron_vt.backend.json_backend._open", m):
        p = pathlib.Path(valid_test_safe.json_filename)
        json_backend.save(p, False, valid_test_safe.entries)
    m.assert_called_once_with(p, "wt")
    handle = m()
    handle.write.assert_called_once_with(valid_test_safe.json_file)


def test_save_b64(valid_test_safe: SafeFixture):
    m = unittest.mock.mock_open()
    with unittest.mock.patch("iron_vt.backend.json_backend._open", m):
        p = pathlib.Path(valid_test_safe.b64_filename)
        json_backend.save(p, True, valid_test_safe.entries)
    m.assert_called_once_with(p, "wt")
    handle = m()
    handle.write.assert_called_once_with(valid_test_safe.b64_file)


def test_load_json(valid_test_safe: SafeFixture):
    m = unittest.mock.mock_open(read_data=valid_test_safe.json_file)
    with unittest.mock.patch("iron_vt.backend.json_backend._open", m):
        p = pathlib.Path(valid_test_safe.json_filename)
        got = json_backend.load(p, False)
    m.assert_called_once_with(p, "rt")
    assert got == valid_test_safe.entries


def test_load_b64(valid_test_safe: SafeFixture):
    m = unittest.mock.mock_open(read_data=valid_test_safe.b64_file)
    with unittest.mock.patch("iron_vt.backend.json_backend._open", m):
        p = pathlib.Path(valid_test_safe.b64_filename)
        got = json_backend.load(p, True)
    m.assert_called_once_with(p, "rt")
    assert got == valid_test_safe.entries


def test_full_save_json(valid_test_safe: SafeFixture):
    valut_path = "vt"

    m = unittest.mock.mock_open()
    with unittest.mock.patch("iron_vt.backend.json_backend._open", m):
        vault = json_backend.JSONBackend(pathlib.Path(valut_path), b64_encode=False)
        vault.save(valid_test_safe.name, valid_test_safe.entries)

    m.assert_called_once_with(
        pathlib.Path(valut_path, valid_test_safe.json_filename), "wt"
    )
    handle = m()
    handle.write.assert_called_once_with(valid_test_safe.json_file)


def test_full_load_json(valid_test_safe: SafeFixture):
    valut_path = "vt"

    m = unittest.mock.mock_open(read_data=valid_test_safe.json_file)
    with unittest.mock.patch("iron_vt.backend.json_backend._open", m):
        vault = json_backend.JSONBackend(pathlib.Path(valut_path), b64_encode=False)
        got = vault.load(valid_test_safe.name)

    m.assert_called_once_with(
        pathlib.Path(valut_path, valid_test_safe.json_filename), "rt"
    )
    assert got == valid_test_safe.entries


def test_full_save_b64(valid_test_safe: SafeFixture):
    valut_path = "vt"

    m = unittest.mock.mock_open()
    with unittest.mock.patch("iron_vt.backend.json_backend._open", m):
        vault = json_backend.JSONBackend(pathlib.Path(valut_path), b64_encode=True)
        vault.save(valid_test_safe.name, valid_test_safe.entries)

    m.assert_called_once_with(
        pathlib.Path(valut_path, valid_test_safe.b64_filename), "wt"
    )
    handle = m()
    handle.write.assert_called_once_with(valid_test_safe.b64_file)


def test_full_load_b64(valid_test_safe: SafeFixture):
    valut_path = "vt"

    m = unittest.mock.mock_open(read_data=valid_test_safe.b64_file)
    with unittest.mock.patch("iron_vt.backend.json_backend._open", m):
        vault = json_backend.JSONBackend(pathlib.Path(valut_path), b64_encode=True)
        got = vault.load(valid_test_safe.name)

    m.assert_called_once_with(
        pathlib.Path(valut_path, valid_test_safe.b64_filename), "rt"
    )
    assert got == valid_test_safe.entries
