from app.utils.date_utils import parse_iso_date, parse_sheet_date


class WeekResolver:
    def resolve_week(self, target_date_str: str, weeks: list[dict]) -> dict:
        target_date = parse_iso_date(target_date_str)
        year = target_date.year

        for week in weeks:
            start_str = week.get("start")
            end_str = week.get("end")

            if not start_str or not end_str:
                continue

            start_date = parse_sheet_date(start_str, year)
            end_date = parse_sheet_date(end_str, year)

            if start_date <= target_date <= end_date:
                return week

        return None