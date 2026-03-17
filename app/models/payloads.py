from typing import List, Optional, Union
from pydantic import BaseModel, Field


Number = Union[int, float]


class SheetUpdateRecord(BaseModel):
    date: str
    asin: str
    parent_asin: Optional[str] = ""
    parent_asin_attempted: Optional[str] = ""
    sales_price: Optional[Number] = None
    currency: Optional[str] = None
    sales_rank: Optional[int] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    sub_category_rank: Optional[int] = None
    bsr_present: Optional[str] = None
    fail_reason: Optional[str] = ""
    selected_price: Optional[Number] = None
    selected_currency: Optional[str] = None
    avg_offer_price: Optional[Number] = None
    min_offer_price: Optional[Number] = None
    offer_count: Optional[int] = None


class SheetUpdateRequest(BaseModel):
    records: List[SheetUpdateRecord] = Field(default_factory=list)