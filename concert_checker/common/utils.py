import re


def slugify(name: str) -> str:
    """Convert a name to a URL/email-safe slug.

    "Men I Trust" -> "men-i-trust"
    """
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")
