from app.config import settings
from app.services.google_client import GoogleClientFactory


class SheetAccessService:
    def test_access(self) -> dict:
        client = GoogleClientFactory.create_client()

        spreadsheet = client.open_by_key(settings.default_spreadsheet_id)
        worksheet = spreadsheet.worksheet(settings.default_worksheet_name)

        headers = worksheet.row_values(1)

        return {
            "spreadsheet_title": spreadsheet.title,
            "worksheet_title": worksheet.title,
            "header_count": len(headers),
            "headers": headers,
        }