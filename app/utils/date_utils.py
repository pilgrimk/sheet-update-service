from datetime import datetime


def parse_iso_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def parse_sheet_date(date_str: str, reference_year: int) -> datetime:
    """
    Convert sheet date like '8/24' into datetime using reference year.
    """
    if not date_str:
        return None

    return datetime.strptime(f"{date_str}/{reference_year}", "%m/%d/%Y")