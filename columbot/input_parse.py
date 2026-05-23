from urllib.parse import urlparse

_REDDIT_HOSTS = {"reddit.com", "www.reddit.com", "old.reddit.com"}


def parse_username(raw: str) -> str:
    """Extract a Reddit username from a URL, u/prefix, or plain string."""
    stripped = raw.strip()
    if not stripped:
        raise ValueError("Username cannot be empty")

    if stripped.startswith(("http://", "https://")):
        return _parse_from_url(stripped)

    if stripped.startswith("/u/"):
        return stripped[3:]
    if stripped.startswith("u/"):
        return stripped[2:]

    return stripped


def _parse_from_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname not in _REDDIT_HOSTS:
        raise ValueError(f"Not a Reddit URL: {url}")

    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2 or parts[0] not in ("user", "u"):
        raise ValueError(f"Could not find username in Reddit URL: {url}")

    return parts[1]
