import re


def slugify_filename(value: str) -> str:
    ascii_only = value.encode("ascii", "ignore").decode("ascii").lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", ascii_only).strip("-")
    return cleaned or "capture"
