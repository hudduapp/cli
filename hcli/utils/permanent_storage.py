import json
import os
from typing import Any

filename = "store.json"
dir_path = os.path.dirname(os.path.realpath(__file__)).split("/utils")[0]

file_path = f"{dir_path}/{filename}"


def read_field(key: str) -> Any:
    try:
        with open(file_path, "r") as f:
            fields = json.loads(f.read())
            return fields.get(key, None)
    except:
        return None


def set_field(key: str, value: Any) -> None:
    try:
        with open(file_path, "r") as f:
            try:
                fields = json.loads(f.read())
            except:
                fields = {}
            f.close()
    except:
        fields = {}
    with open(file_path, "w+") as f:
        fields[key] = value
        data = json.dumps(fields)
        f.write(data)

        f.close()


def unset_field(key: str) -> None:
    with open(file_path, "w+") as f:
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
