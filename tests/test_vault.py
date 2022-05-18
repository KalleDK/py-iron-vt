import pathlib
import dataclasses
import pytest
import unittest.mock
import unittest

import iron_vt


@dataclasses.dataclass
class SafeFixture:
    safe: iron_vt.Safe
    key: str
    json_filename: str
    json_file: str
    b64_filename: str
    b64_file: str


@pytest.fixture
def valid_test_safe():
    return SafeFixture(
        safe=iron_vt.Safe(
            name="valid_safe",
            entries={
                "KEY_1": b"SECRET_A",
                "KEY_2": b"SECRET_B",
            },
        ),
        key="mykey",
        json_filename="valid_safe.json",
        json_file=""
        '{\n    "KEY_1": {\n        "salt": "AAAAAAAAAAAAAAAAAAAAAA==",\n'
        '        "token": "Z0FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBRWl'
        "qbmwwTUtELURqQ3BaTEpXcTZzZG5BTjhjMnBRU2g4cnZTdVBuSk9tYkdib3l5QkRi"
        'Zzc1MGZQR1loYW05R0E9PQ=="\n    },\n    "KEY_2": {\n        "salt"'
        ': "AAAAAAAAAAAAAAAAAAAAAA==",\n        "token": "Z0FBQUFBQUFBQUFBQ'
        "UFBQUFBQUFBQUFBQUFBQUFBQUFBSjVtQ3dQMXVFS0Ewazd1a1A3RmRJeDNCRkRtY2"
        'tscGstX1g2OEpHMjFRU2ZKV0FmZ0k0QjVyRjUyc2ZMREtsa0E9PQ=="\n    }\n}',
        b64_filename="valid_safe.b64",
        b64_file=""
        "ewogICAgIktFWV8xIjogewogICAgICAgICJzYWx0"
        "IjogIkFBQUFBQUFBQUFBQUFBQUFBQUFBQUE9PSIsC"
        "iAgICAgICAgInRva2VuIjogIlowRkJRVUZCUVVGQl"
        "FVRkJRVUZCUVVGQlFVRkJRVUZCUVVGQlFVRkJRVUZ"
        "CUldscWJtd3dUVXRFTFVScVEzQmFURXBYY1RaelpH"
        "NUJUamhqTW5CUlUyZzRjblpUZFZCdVNrOXRZa2RpYj"
        "NsNVFrUmlaemMxTUdaUVIxbG9ZVzA1UjBFOVBRPT0iC"
        "iAgICB9LAogICAgIktFWV8yIjogewogICAgICAgIC"
        "JzYWx0IjogIkFBQUFBQUFBQUFBQUFBQUFBQUFBQUE"
        "9PSIsCiAgICAgICAgInRva2VuIjogIlowRkJRVUZCU"
        "VVGQlFVRkJRVUZCUVVGQlFVRkJRVUZCUVVGQlFVRkJR"
        "VUZCU2pWdFEzZFFNWFZGUzBFd2F6ZDFhMUEzUm1SSmV"
        "ETkNSa1J0WTJ0c2NHc3RYMWcyT0VwSE1qRlJVMlpLVj"
        "BGbVowazBRalZ5UmpVeWMyWk1SRXRzYTBFOVBRPT0iC"
        "iAgICB9Cn0=",
    )


def test_vault_load_b64(valid_test_safe: SafeFixture):
    vault_path = "vt"

    m = unittest.mock.mock_open(read_data=valid_test_safe.b64_file)
    with unittest.mock.patch("iron_vt.backend.json_backend._open", m):
        vault = iron_vt.Vault(vault_path)
        got = vault.load(valid_test_safe.safe.name, valid_test_safe.key)

    m.assert_called_once_with(
        pathlib.Path(vault_path, valid_test_safe.b64_filename), "rt"
    )
    assert got == valid_test_safe.safe


def test_vault_load_json(valid_test_safe: SafeFixture):
    vault_path = "vt"

    m = unittest.mock.mock_open(read_data=valid_test_safe.json_file)
    with unittest.mock.patch("iron_vt.backend.json_backend._open", m):
        vault = iron_vt.Vault(vault_path, b64_encode=False)
        got = vault.load(valid_test_safe.safe.name, valid_test_safe.key)

    m.assert_called_once_with(
        pathlib.Path(vault_path, valid_test_safe.json_filename), "rt"
    )
    assert got == valid_test_safe.safe


def test_vault_save_b64(valid_test_safe: SafeFixture):
    vault_path = "vt"

    m = unittest.mock.mock_open()
    with (
        unittest.mock.patch("time.time") as mock_time_time,
        unittest.mock.patch("os.urandom") as mock_os_urandom,
        unittest.mock.patch("iron_vt.backend.json_backend._open", m),
    ):
        mock_time_time.return_value = 0
        mock_os_urandom.return_value = bytes(16)
        vault = iron_vt.Vault(vault_path)
        vault.save(valid_test_safe.safe, valid_test_safe.key)

    m.assert_called_once_with(
        pathlib.Path(vault_path, valid_test_safe.b64_filename), "wt"
    )
    handle = m()
    handle.write.assert_called_once_with(valid_test_safe.b64_file)


def test_vault_save_json(valid_test_safe: SafeFixture):
    vault_path = "vt"

    m = unittest.mock.mock_open()
    with (
        unittest.mock.patch("time.time") as mock_time_time,
        unittest.mock.patch("os.urandom") as mock_os_urandom,
        unittest.mock.patch("iron_vt.backend.json_backend._open", m),
    ):
        mock_time_time.return_value = 0
        mock_os_urandom.return_value = bytes(16)
        vault = iron_vt.Vault(vault_path, b64_encode=False)
        vault.save(valid_test_safe.safe, valid_test_safe.key)

    m.assert_called_once_with(
        pathlib.Path(vault_path, valid_test_safe.json_filename), "wt"
    )
    handle = m()
    handle.write.assert_called_once_with(valid_test_safe.json_file)


def test_safe_get():
    s = iron_vt.Safe("hola")
    s.add("demo_1", "SECRET_A")
    s.add("demo_2", "SECRET_B")
    assert s.get("demo_1") == "SECRET_A"
    assert s.get("demo_2") == "SECRET_B"
    s["demo_2"] = "SECRET_C"
    assert s["demo_1"] == "SECRET_A"
    assert s["demo_2"] == "SECRET_C"
    assert s.get("MISSING", "BACKUP") == "BACKUP"


@pytest.mark.parametrize(
    "exists,is_file,want",
    [
        (True, True, True),
        (True, False, False),
        (False, True, False),
        (False, False, False),
    ],
)
def test_safe_exists(exists: bool, is_file: bool, want: bool):
    with (
        unittest.mock.patch("pathlib.Path.exists") as mock_exists,
        unittest.mock.patch("pathlib.Path.is_file") as mock_is_file,
    ):

        mock_exists.return_value = exists
        mock_is_file.return_value = is_file

        vault = iron_vt.Vault()
        got = vault.exists("should_exists")

    assert got == want


def test_create():
    v = iron_vt.Vault()
    got = v.create("demo_1")
    want = iron_vt.Safe("demo_1")
    assert got == want
