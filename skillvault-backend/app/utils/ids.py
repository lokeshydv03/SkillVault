import uuid


def generate_id(prefix: str) -> str:
    """Generate a prefixed unique ID, e.g. task_abc123..."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def generate_slug(name: str) -> str:
    """Convert skill name into slug format."""
    clean = "".join(c if c.isalnum() or c in " _-" else "" for c in name.lower())
    return "_".join(clean.split())
