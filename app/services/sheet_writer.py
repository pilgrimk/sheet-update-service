class SheetWriter:
    def update_rows(self, spreadsheet_id: str, worksheet_name: str, rows: list[dict], dry_run: bool = True) -> dict:
        if dry_run:
            return {
                "rows_updated": len(rows),
                "mode": "dry_run",
                "note": "No real sheet update performed.",
            }

        # Real Google Sheets update logic goes here later.
        return {
            "rows_updated": len(rows),
            "mode": "live",
            "note": "Stub live response. Real implementation pending.",
        }