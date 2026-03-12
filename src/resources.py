import json


def load_resources():
    try:
        with open("resources.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


RESOURCES = load_resources()