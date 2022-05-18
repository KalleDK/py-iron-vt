"""iron_vt.

Usage:
  iron_vt [--vault=<dir>] [--safe=<name>] [--no-b64] (add|get|del) <name>
  iron_vt [--vault=<dir>] [--safe=<name>] list
  iron_vt (-h | --help)
  iron_vt --version

Options:
  -h --help      Show this screen.
  --version      Show version.
  --safe=<name>  Safe name [default: safe].
  --vault=<dir>  Vault directory [default: ./vt].
  --no-b64       Don't encode json in base64 [default: False].

"""
import sys
import getpass
from typing import TypedDict, cast, TextIO
from docopt import docopt
from . import Vault, VERSION


Args = TypedDict(
    "Args",
    {
        "--help": bool,
        "--no-b64": bool,
        "--safe": str,
        "--vault": str,
        "--version": bool,
        "<name>": str,
        "add": bool,
        "get": bool,
        "del": bool,
        "list": bool,
    },
)


def get_entry(args: Args, stdout: TextIO, stderr: TextIO):
    vault = Vault(path=args["--vault"], b64_encode=(not args["--no-b64"]))
    if not vault.exists(args["--safe"]):
        print(f"No such safe: {args['--safe']}")
        return
    key = getpass.getpass(f"Key for safe {args['--safe']}: ", stream=stderr)
    safe = vault.load(args["--safe"], key)
    secret = safe.get(args["<name>"])
    if secret is None:
        print("no entry", file=stderr)
    print(secret, file=stdout)


def add_entry(args: Args, stdout: TextIO, stderr: TextIO):
    vault = Vault(path=args["--vault"], b64_encode=(not args["--no-b64"]))
    key = getpass.getpass(f"Key for safe {args['--safe']}: ", stream=stderr)
    if vault.exists(args["--safe"]):
        safe = vault.load(args["--safe"], key)
    else:
        safe = vault.create(args["--safe"])

    secret = getpass.getpass(f"Secret for entry {args['<name>']}: ")
    safe.add(args["<name>"], secret)

    vault.save(safe, key)


def del_entry(args: Args, stdout: TextIO, stderr: TextIO):
    vault = Vault(path=args["--vault"], b64_encode=(not args["--no-b64"]))
    if not vault.exists(args["--safe"]):
        print(f"No such safe: {args['--safe']}", file=stderr)
        return

    key = getpass.getpass(f"Key for safe {args['--safe']}: ", stream=stderr)

    safe = vault.load(args["--safe"], key)

    del safe[args["<name>"]]

    vault.save(safe, key)


def list_entries(args: Args, stdout: TextIO, stderr: TextIO):
    vault = Vault(path=args["--vault"], b64_encode=(not args["--no-b64"]))
    if not vault.exists(args["--safe"]):
        print(f"No such safe: {args['--safe']}", stderr)
        return

    key = getpass.getpass(f"Key for safe {args['--safe']}: ", stream=stderr)
    safe = vault.load(args["--safe"], key)

    for name in safe.entries:
        print(f"* {name}", file=stdout)


def main():
    if __doc__ is None:
        raise Exception("missing docopt help text")

    args = cast(Args, docopt(__doc__, version=f"Iron Vault {VERSION}"))

    stdout = sys.stdout
    stderr = sys.stderr

    if args["get"]:
        try:
            get_entry(args, stdout, stderr)
        except Exception as e:
            print(e)
        return

    if args["add"]:
        try:
            add_entry(args, stdout, stderr)
        except Exception as e:
            print(e)
        return

    if args["del"]:
        try:
            del_entry(args, stdout, stderr)
        except Exception as e:
            print(e)
        return

    if args["list"]:
        try:
            list_entries(args, stdout, stderr)
        except Exception as e:
            print(e)
        return
