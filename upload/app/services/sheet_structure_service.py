from app.config import settings
from app.services.google_client import GoogleClientFactory
from app.services.mapping_config import match_metric_label, match_structure_label
from app.utils.date_utils import try_parse_full_sheet_date


class SheetStructureService:
    def load_values(self) -> tuple:
        client = GoogleClientFactory.create_client()
        spreadsheet = client.open_by_key(settings.default_spreadsheet_id)
        worksheet = spreadsheet.worksheet(settings.default_worksheet_name)
        values = worksheet.get_all_values()
        return spreadsheet, worksheet, values

    def parse_structure(self) -> dict:
        spreadsheet, worksheet, values = self.load_values()

        warnings = []

        structure = {
            "spreadsheet_title": spreadsheet.title,
            "worksheet_title": worksheet.title,
            "weeks": [],
            "products": {},
            "row_count": len(values),
            "warnings": warnings,
        }

        # Parse week columns from rows 2, 3, and 4 (1-based sheet rows)
        # values[1] = week label row
        # values[2] = week start row
        # values[3] = week end row
        if len(values) >= 4:
            week_row = values[1]
            start_row = values[2]
            end_row = values[3]

            max_cols = max(len(week_row), len(start_row), len(end_row))

            for col_idx in range(max_cols):
                week_label = week_row[col_idx] if col_idx < len(week_row) else ""
                start_date_raw = start_row[col_idx] if col_idx < len(start_row) else ""
                end_date_raw = end_row[col_idx] if col_idx < len(end_row) else ""

                if not str(week_label).strip():
                    continue

                # Validate that week start/end dates include year going forward.
                # We still record the week either way so the resolver can decide how strict to be.
                start_date_parsed = try_parse_full_sheet_date(start_date_raw)
                end_date_parsed = try_parse_full_sheet_date(end_date_raw)

                if (start_date_raw or end_date_raw) and (start_date_parsed is None or end_date_parsed is None):
                    warnings.append({
                        "type": "schema_warning",
                        "message": "Week header missing year or using unsupported format. Expected M/D/YYYY or YYYY-MM-DD.",
                        "column_index_1based": col_idx + 1,
                        "week_label": week_label,
                        "start_raw": start_date_raw,
                        "end_raw": end_date_raw,
                    })

                structure["weeks"].append({
                    "label": week_label,
                    "start": start_date_raw,
                    "end": end_date_raw,
                    "column_index_1based": col_idx + 1,
                })

        current_product = None

        for row_idx, row in enumerate(values, start=1):
            col_a = row[0] if len(row) > 0 else ""
            col_b = row[1] if len(row) > 1 else ""

            structure_key = match_structure_label(col_a)
            metric_key = match_metric_label(col_b)

            if structure_key == "product_label":
                current_product = {
                    "product_name": col_b,
                    "product_row": row_idx,
                    "asin": None,
                    "asin_row": None,
                    "metric_rows": {},
                }
                continue

            if structure_key == "asin_label" and current_product:
                current_product["asin"] = col_b
                current_product["asin_row"] = row_idx
                structure["products"][col_b] = current_product
                continue

            if metric_key and current_product:
                current_product["metric_rows"][metric_key] = row_idx

        return structure