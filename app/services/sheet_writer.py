import gspread
from app.services.google_client import GoogleClientFactory


class SheetWriter:
    def update_rows(self, spreadsheet_id: str, worksheet_name: str, rows: list[dict], dry_run: bool = True) -> dict:
        if dry_run:
            return {
                "rows_updated": len(rows),
                "mode": "dry_run",
                "note": "No real sheet update performed.",
            }

        return {
            "rows_updated": len(rows),
            "mode": "live",
            "note": "Stub live response. Real implementation pending.",
        }

    def apply_updates(
        self,
        spreadsheet_id: str,
        worksheet_name: str,
        updates: list[dict],
        dry_run: bool = True,
    ) -> dict:
        """
        Apply already-planned cell updates to known row/column coordinates.
        Each update is expected to contain:
        - row
        - col
        - value
        """
        if dry_run:
            return {
                "updates_attempted": len(updates),
                "updates_applied": 0,
                "mode": "dry_run",
                "applied_cells": [],
                "note": "Dry run only. No live cell updates performed.",
            }

        client = GoogleClientFactory.create_client()
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        applied_cells = []
        batch_payload = []

        for item in updates:
            row = item["row"]
            col = item["col"]
            value = item["value"]

            a1_ref = gspread.utils.rowcol_to_a1(row, col)

            batch_payload.append({
                "range": a1_ref,
                "values": [[value]],
            })

            applied_cells.append({
                "row": row,
                "col": col,
                "a1": a1_ref,
                "value": value,
                "metric": item.get("metric"),
                "asin": item.get("asin"),
                "date": item.get("date"),
            })

        if batch_payload:
            worksheet.batch_update(batch_payload, value_input_option="USER_ENTERED")

        return {
            "updates_attempted": len(updates),
            "updates_applied": len(batch_payload),
            "mode": "live",
            "applied_cells": applied_cells,
            "note": "Live planned updates applied successfully.",
        }

    def create_week_columns(
        self,
        spreadsheet_id: str,
        worksheet_name: str,
        planned_new_weeks: list[dict],
        dry_run: bool = True,
    ) -> dict:
        """
        Create new week columns by appending columns to the right and populating:
        - row 2: week label
        - row 3: week start
        - row 4: week end

        Assumes new weeks are appended to the right in chronological order.
        """
        if dry_run:
            return {
                "weeks_attempted": len(planned_new_weeks),
                "weeks_created": 0,
                "mode": "dry_run",
                "created_weeks": [],
                "note": "Dry run only. No live week columns created.",
            }

        client = GoogleClientFactory.create_client()
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        created_weeks = []

        # Sort by target column just to keep execution deterministic
        sorted_weeks = sorted(
            planned_new_weeks,
            key=lambda w: w.get("column_index_1based", 0)
        )

        for week in sorted_weeks:
            target_col = week["column_index_1based"]

            # Insert a blank column before target_col.
            # Since planner appends to the right, this effectively creates the new rightmost column.
            worksheet.insert_cols([[""]], col=target_col)

            batch_payload = [
                {
                    "range": gspread.utils.rowcol_to_a1(2, target_col),
                    "values": [[week["label"]]],
                },
                {
                    "range": gspread.utils.rowcol_to_a1(3, target_col),
                    "values": [[week["start"]]],
                },
                {
                    "range": gspread.utils.rowcol_to_a1(4, target_col),
                    "values": [[week["end"]]],
                },
            ]

            worksheet.batch_update(batch_payload, value_input_option="USER_ENTERED")

            created_weeks.append({
                "label": week["label"],
                "start": week["start"],
                "end": week["end"],
                "column_index_1based": target_col,
                "insert_after_column_index_1based": week.get("insert_after_column_index_1based"),
            })

        return {
            "weeks_attempted": len(planned_new_weeks),
            "weeks_created": len(created_weeks),
            "mode": "live",
            "created_weeks": created_weeks,
            "note": "Live week columns created successfully.",
        }
    
    def create_asin_blocks(
        self,
        spreadsheet_id: str,
        worksheet_name: str,
        planned_new_asin_blocks: list[dict],
        dry_run: bool = True,
    ) -> dict:
        if dry_run:
            return {
                "blocks_attempted": len(planned_new_asin_blocks),
                "blocks_created": 0,
                "mode": "dry_run",
                "note": "Dry run only. No ASIN blocks created.",
            }

        client = GoogleClientFactory.create_client()
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        created_blocks = []

        # IMPORTANT: process from bottom → top to avoid row shifting issues
        sorted_blocks = sorted(
            planned_new_asin_blocks,
            key=lambda b: b["insert_after_row"],
            reverse=True
        )

        for block in sorted_blocks:
            insert_after = block["insert_after_row"]
            total_rows = block["total_rows_required"]

            # Insert blank rows
            worksheet.insert_rows(
                [[""] * worksheet.col_count] * total_rows,
                row=insert_after + 1
            )

            batch_payload = []

            # Product row
            batch_payload.append({
                "range": f"A{block['product_row']}",
                "values": [[block["product_label"]]],
            })

            # ASIN row
            batch_payload.append({
                "range": f"A{block['asin_row']}",
                "values": [[block["asin_label"]]],
            })
            batch_payload.append({
                "range": f"B{block['asin_row']}",
                "values": [[block["asin"]]],
            })

            # Metric labels go in column B
            for metric in block["metric_rows"]:
                batch_payload.append({
                    "range": f"B{metric['row']}",
                    "values": [[metric["display_label"]]],
                })

            if batch_payload:
                worksheet.batch_update(batch_payload, value_input_option="USER_ENTERED")

            created_blocks.append({
                "asin": block["asin"],
                "rows_inserted": total_rows,
                "insert_after_row": insert_after,
            })

        return {
            "blocks_attempted": len(planned_new_asin_blocks),
            "blocks_created": len(created_blocks),
            "mode": "live",
            "created_blocks": created_blocks,
        }    