import re

from app.services.mapping_config import METRIC_ROW_ORDER, get_preferred_metric_label
from app.services.week_resolver import WeekResolver
from app.utils.date_utils import (
    format_sheet_date,
    get_week_bounds,
    get_week_label,
    parse_iso_date,
)


class MutationPlanner:
    def __init__(self) -> None:
        self.week_resolver = WeekResolver()

    def _extract_week_number(self, label: str) -> int | None:
        if not label:
            return None

        match = re.search(r"week\s+(\d+)", str(label).strip(), re.IGNORECASE)
        if not match:
            return None

        try:
            return int(match.group(1))
        except ValueError:
            return None

    def _get_last_existing_week(self, weeks: list[dict]) -> dict | None:
        if not weeks:
            return None

        valid_weeks = [
            week for week in weeks
            if week.get("column_index_1based") is not None
        ]

        if not valid_weeks:
            return None

        return max(valid_weeks, key=lambda w: w.get("column_index_1based", 0))

    def _get_next_week_label(self, target_date, weeks: list[dict]) -> str:
        last_week = self._get_last_existing_week(weeks)

        if last_week:
            last_label = last_week.get("label", "")
            last_week_number = self._extract_week_number(last_label)

            if last_week_number is not None:
                next_week_number = 1 if last_week_number >= 52 else last_week_number + 1
                return f"Week {next_week_number}"

        return get_week_label(target_date)

    def _plan_new_week(self, record_date: str, weeks: list[dict]) -> dict:
        target_date = parse_iso_date(record_date)
        week_start, week_end = get_week_bounds(target_date)

        existing_cols = [
            week.get("column_index_1based", 0)
            for week in weeks
            if week.get("column_index_1based")
        ]
        insert_after_col = max(existing_cols) if existing_cols else 3
        new_col = insert_after_col + 1

        last_week = self._get_last_existing_week(weeks)
        planned_label = self._get_next_week_label(target_date, weeks)

        return {
            "date": record_date,
            "label": planned_label,
            "start": format_sheet_date(week_start, include_year=True),
            "end": format_sheet_date(week_end, include_year=True),
            "column_index_1based": new_col,
            "insert_after_column_index_1based": insert_after_col,
            "based_on_last_week_label": last_week.get("label") if last_week else None,
            "reason": "No matching week column found for date.",
        }

    def _get_last_used_row(self, structure: dict) -> int:
        products = structure.get("products", {})

        # Start with actual parsed sheet height
        max_row = structure.get("row_count", 4)

        for product in products.values():
            product_row = product.get("product_row") or 0
            asin_row = product.get("asin_row") or 0
            metric_rows = product.get("metric_rows", {})
            metric_max = max(metric_rows.values()) if metric_rows else 0

            max_row = max(max_row, product_row, asin_row, metric_max)

        return max_row

    def _plan_new_asin_block(self, record, structure: dict) -> dict:
        last_used_row = self._get_last_used_row(structure)

        # leave one blank spacer row before new block
        product_row = last_used_row + 2
        asin_row = product_row + 1

        planned_metric_rows = []
        metric_row_lookup = {}

        current_row = asin_row + 1

        for metric_key in METRIC_ROW_ORDER:
            planned_metric_rows.append({
                "metric_key": metric_key,
                "display_label": get_preferred_metric_label(metric_key),
                "row": current_row,
            })
            metric_row_lookup[metric_key] = current_row
            current_row += 1

        spacer_row_after_block = current_row

        planned_values_ready = []
        record_data = record.model_dump()

        for metric_key in METRIC_ROW_ORDER:
            metric_value = record_data.get(metric_key)
            if metric_value is None:
                continue

            planned_values_ready.append({
                "metric": metric_key,
                "value": metric_value,
                "row": metric_row_lookup[metric_key],
            })

        return {
            "asin": record.asin,
            "date": record.date,
            "insert_after_row": last_used_row,
            "product_row": product_row,
            "asin_row": asin_row,
            "asin_label": "Product ASIN",
            "product_label": "Product",
            "product_name": "",
            "metric_rows": planned_metric_rows,
            "spacer_row_after_block": spacer_row_after_block,
            "total_rows_required": spacer_row_after_block - product_row + 1,
            "planned_values_ready": planned_values_ready,
            "reason": "ASIN block not found in sheet structure.",
        }

    def plan(self, structure: dict, records: list) -> dict:
        updates = []
        missing_asins = []
        missing_weeks = []
        planned_new_weeks = []
        planned_new_asin_blocks = []
        skipped_metrics = []
        warnings = []
        processed_records = []

        products = structure.get("products", {})
        weeks = structure.get("weeks", [])

        planned_week_keys = set()
        planned_asin_keys = set()

        for record in records:
            asin = record.asin
            record_date = record.date

            product_block = products.get(asin)
            resolved_week = self.week_resolver.resolve_week(record_date, weeks)

            record_summary = {
                "asin": asin,
                "date": record_date,
                "week_found": resolved_week is not None,
                "asin_found": product_block is not None,
            }

            if resolved_week and resolved_week.get("warnings"):
                for warning in resolved_week["warnings"]:
                    warnings.append({
                        "asin": asin,
                        "date": record_date,
                        "warning": warning,
                        "week_label": resolved_week.get("label"),
                        "week_start": resolved_week.get("start"),
                        "week_end": resolved_week.get("end"),
                    })

            if not product_block:
                missing_asins.append({
                    "asin": asin,
                    "date": record_date,
                    "reason": "ASIN block not found in sheet structure."
                })

                if asin not in planned_asin_keys:
                    planned_new_asin_blocks.append(
                        self._plan_new_asin_block(record, structure)
                    )
                    planned_asin_keys.add(asin)

            if not resolved_week:
                missing_weeks.append({
                    "asin": asin,
                    "date": record_date,
                    "reason": "No matching week column found for date."
                })

                planned_week = self._plan_new_week(record_date, weeks)
                planned_week_key = (planned_week["start"], planned_week["end"])

                if planned_week_key not in planned_week_keys:
                    planned_new_weeks.append(planned_week)
                    planned_week_keys.add(planned_week_key)

            if not product_block or not resolved_week:
                processed_records.append(record_summary)
                continue

            target_col = resolved_week["column_index_1based"]
            metric_rows = product_block.get("metric_rows", {})

            for metric_name, metric_value in record.model_dump().items():
                if metric_name in {"date", "asin"}:
                    continue

                if metric_value is None:
                    continue

                target_row = metric_rows.get(metric_name)

                if not target_row:
                    skipped_metrics.append({
                        "asin": asin,
                        "date": record_date,
                        "metric": metric_name,
                        "value": metric_value,
                        "reason": "Metric row not found in ASIN block."
                    })
                    continue

                updates.append({
                    "asin": asin,
                    "date": record_date,
                    "metric": metric_name,
                    "row": target_row,
                    "col": target_col,
                    "value": metric_value,
                    "week_label": resolved_week["label"],
                    "week_start": resolved_week["start"],
                    "week_end": resolved_week["end"],
                    "matched_start_iso": resolved_week.get("matched_start_iso"),
                    "matched_end_iso": resolved_week.get("matched_end_iso"),
                    "used_legacy_match": resolved_week.get("used_legacy_match", False),
                })

            processed_records.append(record_summary)

        return {
            "summary": {
                "records_received": len(records),
                "records_processed": len(processed_records),
                "updates_planned": len(updates),
                "missing_asins": len(missing_asins),
                "missing_weeks": len(missing_weeks),
                "planned_new_weeks": len(planned_new_weeks),
                "planned_new_asin_blocks": len(planned_new_asin_blocks),
                "skipped_metrics": len(skipped_metrics),
                "warnings": len(warnings),
            },
            "updates": updates,
            "missing_asins": missing_asins,
            "missing_weeks": missing_weeks,
            "planned_new_weeks": planned_new_weeks,
            "planned_new_asin_blocks": planned_new_asin_blocks,
            "skipped_metrics": skipped_metrics,
            "warnings": warnings,
            "processed_records": processed_records,
        }