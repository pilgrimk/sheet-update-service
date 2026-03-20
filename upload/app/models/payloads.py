from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal


class SheetMetricRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    date: str
    asin: str

    parent_pageviews: Optional[float] = None
    parent_units_ordered: Optional[float] = None
    parent_conversion_rate: Optional[float] = None
    sub_category_bsr: Optional[float] = None
    average_price: Optional[float] = None
    best_deal: Optional[float] = None
    coupon: Optional[float] = None
    sales: Optional[float] = None
    sales_ly: Optional[float] = None
    sales_yoy_change: Optional[float] = None
    spend: Optional[float] = None
    impressions: Optional[float] = None
    clicks: Optional[float] = None
    advertising_sales: Optional[float] = None
    organic_sales: Optional[float] = None
    cpc: Optional[float] = None
    revenue_per_click: Optional[float] = None
    roas: Optional[float] = None
    cost_per_acquisition: Optional[float] = None
    tacos: Optional[float] = None
    profitability: Optional[float] = None


class SheetUpdateRequest(BaseModel):
    records: List[SheetMetricRecord] = Field(default_factory=list)


class TestMutationRequest(BaseModel):
    mode: Literal[
        "plan_only",
        "apply_existing_updates",
        "apply_with_new_weeks",
        "apply_full",
    ]
    records: List[SheetMetricRecord] = Field(default_factory=list)