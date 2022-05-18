# py-iron-vt

## Installing
```bash
git clone ...
pip install ./py-iron-vt
```

## Usage Library

### Get a secret simple
This is mostly for your read once settings, and not for updating / saving
```python
import iron_vt

safe = iron_vt.load(name="my_safe", key="my_key")
secret_a = safe["entry_a"]
secret_b = safe["entry_b"]
```

## Usage Client
```bash
Usage:
  iron_vt [--vault=<dir>] [--safe=<name>] [--no-b64] (add|get|del) <name>
  iron_vt [--vault=<dir>] [--safe=<name>] list
  iron_vt (-h | --help)
  iron_vt --version
```