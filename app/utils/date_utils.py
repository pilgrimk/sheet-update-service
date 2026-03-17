from datetime import datetime, timedelta
from typing import Optional


def parse_iso_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def try_parse_full_sheet_date(date_str: str) -> Optional[datetime]:
    """
    Parse supported year-aware sheet date formats.
    Supported:
    - M/D/YYYY
    - MM/DD/YYYY
    - YYYY-MM-DD
    """
    if not date_str:
        return None

    value = str(date_str).strip()

    full_formats = [
        "%m/%d/%Y",
        "%Y-%m-%d",
    ]

    for fmt in full_formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


def parse_sheet_date_legacy(date_str: str, reference_year: int) -> Optional[datetime]:
    """
    Backward-compatible parser for legacy sheet dates like '9/14'
    where the year is missing and must be inferred.
    """
    if not date_str:
        return None

    value = str(date_str).strip()
    return datetime.strptime(f"{value}/{reference_year}", "%m/%d/%Y")


def format_sheet_date(dt: datetime, include_year: bool = True) -> str:
    """
    Format as M/D/YYYY by default for unambiguous sheet storage.
    """
    if include_year:
        return f"{dt.month}/{dt.day}/{dt.year}"
    return f"{dt.month}/{dt.day}"


def get_week_bounds(target_date: datetime) -> tuple[datetime, datetime]:
    """
    Return Sunday-Saturday bounds for the given date.
    Python weekday(): Monday=0 ... Sunday=6
    """
    days_since_sunday = (target_date.weekday() + 1) % 7
    week_start = target_date - timedelta(days=days_since_sunday)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def get_week_label(target_date: datetime) -> str:
    iso_week = target_date.isocalendar().week
    return f"Week {iso_week}"