import json
from typing import Any


def serialize_json(data: Any) -> str:
    """Safely serialize data to JSON string."""
    return json.dumps(data, default=str)


def parse_json(data: str | None) -> Any:
    """Safely parse JSON string."""
    if not data:
        return {}
    try:
        return json.loads(data)
    except Exception:
        return {}
