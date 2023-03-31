import json
from typing import Any

filename = "store.json"


def read_field(key: str) -> Any:
    try:
        with open(filename, "r") as f:
            fields = json.loads(f.read())
            return fields.get(key, None)
    except:
        raise Exception(f"Field {key} is not set. You need to do additional configuration to run this command")


def set_field(key: str, value: Any) -> None:
    with open(filename, "r") as f:
        try:
            fields = json.loads(f.read())
        except:
            fields = {}
        f.close()

    with open(filename, "w") as f:
        fields[key] = value
        data = json.dumps(fields)
        f.write(data)

        f.close()


def unset_field(key: str) -> None:
    with open(filename, "w+") as f:
        try:
            fields = json.loads(f.read())
        except:
            fields = {}
        try:
            fields.pop(key)
        except:
            pass
        data = json.dumps(fields)
        f.write(data)
