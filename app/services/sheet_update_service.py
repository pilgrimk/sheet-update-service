from app.config import settings
from app.models.payloads import SheetUpdateRequest
from app.models.responses import RejectedRecord, SheetUpdateResult
from app.services.sheet_resolver import SheetResolver
from app.services.sheet_writer import SheetWriter


class SheetUpdateService:
    def __init__(self) -> None:
        self.resolver = SheetResolver()
        self.writer = SheetWriter()

    def _validate_record(self, record, index: int):
        if not record.asin:
            return RejectedRecord(index=index, reason="Missing asin", asin=None, date=record.date)

        if not record.date:
            return RejectedRecord(index=index, reason="Missing date", asin=record.asin, date=None)

        return None

    def _map_record_to_row(self, record) -> dict:
        return {
            "date": record.date,
            "asin": record.asin,
            "parent_asin": record.parent_asin,
            "parent_asin_attempted": record.parent_asin_attempted,
            "sales_price": record.sales_price,
            "currency": record.currency,
            "sales_rank": record.sales_rank,
            "category": record.category,
            "sub_category": record.sub_category,
            "sub_category_rank": record.sub_category_rank,
            "bsr_present": record.bsr_present,
            "fail_reason": record.fail_reason,
            "selected_price": record.selected_price,
            "selected_currency": record.selected_currency,
            "avg_offer_price": record.avg_offer_price,
            "min_offer_price": record.min_offer_price,
            "offer_count": record.offer_count,
        }

    def process(self, payload: SheetUpdateRequest) -> SheetUpdateResult:
        rejected = []
        valid_rows = []

        for index, record in enumerate(payload.records):
            rejection = self._validate_record(record, index)
            if rejection:
                rejected.append(rejection)
                continue

            valid_rows.append(self._map_record_to_row(record))

        target = self.resolver.resolve_target(valid_rows)

        writer_result = self.writer.update_rows(
            spreadsheet_id=target["spreadsheet_id"],
            worksheet_name=target["worksheet_name"],
            rows=valid_rows,
            dry_run=settings.dry_run,
        )

        return SheetUpdateResult(
            dry_run=settings.dry_run,
            spreadsheet_id=target["spreadsheet_id"],
            worksheet_name=target["worksheet_name"],
            rows_prepared=len(valid_rows),
            rows_updated=writer_result["rows_updated"],
            rows_rejected=len(rejected),
            rejected=rejected,
            details=writer_result,
        )