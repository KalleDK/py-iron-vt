"""iron_vt.

Usage:
  iron_vt [--vault=<dir>] [--safe=<name>] [--no-b64] (add|get) <name>
  iron_vt (-h | --help)
  iron_vt --version

Options:
  -h --help      Show this screen.
  --version      Show version.
  --safe=<name>  Safe name [default: safe].
  --vault=<dir>  Vault directory [default: ./vt].
  --no-b64       Don't encode json in base64 [default: False].

"""
import getpass
from typing import TypedDict, cast
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
    },
)


def get_entry(args: Args):
    vault = Vault(path=args["--vault"], b64_encode=(not args["--no-b64"]))
    if not vault.exists(args["--safe"]):
        print(f"No such safe: {args['--safe']}")
        return
    key = getpass.getpass(f"Key for safe {args['--safe']}: ")
    safe = vault.load(args["--safe"], key)
    secret = safe.get(args["<name>"])
    if secret is None:
        print("no entry")
    print(secret)


def add_entry(args: Args):
    vault = Vault(path=args["--vault"], b64_encode=(not args["--no-b64"]))
    key = getpass.getpass(f"Key for safe {args['--safe']}: ")
    if vault.exists(args["--safe"]):
        safe = vault.load(args["--safe"], key)
    else:
        safe = vault.create(args["--safe"])

    secret = getpass.getpass(f"Secret for entry {args['<name>']}: ")
    safe.add(args["<name>"], secret)

    vault.save(safe, key)


def main():
    if __doc__ is None:
        raise Exception("missing docopt help text")
    args = cast(Args, docopt(__doc__, version=f"Iron Vault {VERSION}"))
    if args["get"]:
        try:
            get_entry(args)
        except Exception as e:
            print(e)
        return

    if args["add"]:
        try:
            add_entry(args)
        except Exception as e:
            print(e)
        return
