from app.config import settings


class SheetResolver:
    def resolve_target(self, records: list[dict]) -> dict:
        # Stub logic for now.
        # Later this can inspect the records and decide spreadsheet/tab internally.
        return {
            "spreadsheet_id": settings.default_spreadsheet_id,
            "worksheet_name": settings.default_worksheet_name,
        }