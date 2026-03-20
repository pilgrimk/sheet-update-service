from typing import Any, List, Optional
from pydantic import BaseModel


class RejectedRecord(BaseModel):
    index: int
    reason: str
    asin: Optional[str] = None
    date: Optional[str] = None


class SheetUpdateResult(BaseModel):
    dry_run: bool
    spreadsheet_id: str
    worksheet_name: str
    rows_prepared: int
    rows_updated: int
    rows_rejected: int
    rejected: List[RejectedRecord]
    details: dict[str, Any] = {}
