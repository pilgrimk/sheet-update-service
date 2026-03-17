from app.config import settings
from app.utils.date_utils import (
    parse_iso_date,
    parse_sheet_date_legacy,
    try_parse_full_sheet_date,
)


class WeekResolver:
    def resolve_week(self, target_date_str: str, weeks: list[dict]) -> dict | None:
        """
        Resolution policy:
        - Prefer year-aware sheet headers
        - Optionally allow legacy M/D headers
        - Emit warnings for legacy matches when allowed
        """
        target_date = parse_iso_date(target_date_str)
        target_year = target_date.year

        for week in weeks:
            start_str = week.get("start")
            end_str = week.get("end")

            if not start_str or not end_str:
                continue

            start_date = try_parse_full_sheet_date(start_str)
            end_date = try_parse_full_sheet_date(end_str)

            warnings = []

            full_dates_found = start_date is not None and end_date is not None

            if not full_dates_found:
                if settings.require_year_in_week_headers and not settings.allow_legacy_week_match:
                    continue

                if settings.allow_legacy_week_match:
                    try:
                        start_date = parse_sheet_date_legacy(start_str, target_year)
                        end_date = parse_sheet_date_legacy(end_str, target_year)

                        if settings.require_year_in_week_headers:
                            warnings.append(
                                "Week header is using legacy date format without year; "
                                "year-aware dates are required going forward."
                            )
                    except ValueError:
                        continue
                else:
                    continue

            if start_date <= target_date <= end_date:
                resolved = dict(week)
                if warnings:
                    resolved["warnings"] = warnings
                resolved["matched_start_iso"] = start_date.strftime("%Y-%m-%d")
                resolved["matched_end_iso"] = end_date.strftime("%Y-%m-%d")
                resolved["used_legacy_match"] = not full_dates_found
                return resolved

        return None