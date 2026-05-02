"""General helper utilities."""
import re
import hashlib
import math
from datetime import date, datetime
from typing import Any, Dict, List, Optional


def slugify(text: str) -> str:
    """Convert a string to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return re.sub(r"^-+|-+$", "", text)


def hash_string(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(value, max_val))


def get_season(d: Optional[date] = None) -> str:
    """Return fashion season string for a given date."""
    if d is None:
        d = date.today()
    month = d.month
    year = d.year
    if month in (3, 4, 5):
        return f"Spring {year}"
    elif month in (6, 7, 8):
        return f"Summer {year}"
    elif month in (9, 10, 11):
        return f"Fall {year}"
    return f"Winter {year}"


def normalize_score(raw: float, min_raw: float = 0, max_raw: float = 100) -> float:
    """Normalize a raw score to [0, 100]."""
    if max_raw == min_raw:
        return 0.0
    return clamp((raw - min_raw) / (max_raw - min_raw) * 100, 0, 100)


def chunk_list(lst: List[Any], size: int) -> List[List[Any]]:
    """Split a list into chunks of given size."""
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def hex_to_rgb(hex_color: str):
    """Convert #RRGGBB to (R, G, B) tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return "#{:02X}{:02X}{:02X}".format(r, g, b)


def color_distance(hex1: str, hex2: str) -> float:
    """Euclidean distance between two hex colors in RGB space."""
    r1, g1, b1 = hex_to_rgb(hex1)
    r2, g2, b2 = hex_to_rgb(hex2)
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def format_large_number(n: int) -> str:
    """Format 1234567 → '1.2M', 12345 → '12.3K'."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    if b == 0:
        return default
    return a / b


def compute_growth_rate(current: float, previous: float) -> float:
    """Percentage growth rate. Returns 0 if previous is 0."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 2)
