from typing import Optional


def normalize_label(value: Optional[str]) -> str:
    """
    Normalize sheet labels for case-insensitive, whitespace-tolerant matching.
    """
    if value is None:
        return ""
    return " ".join(str(value).strip().lower().split())


STRUCTURE_LABEL_ALIASES = {
    "product_label": {
        "product",
    },
    "asin_label": {
        "parent asin",
        "product asin",
    },
}


METRIC_LABEL_ALIASES = {
    "parent_pageviews": {
        "parent pageviews",
    },
    "parent_units_ordered": {
        "parent units ordered",
    },
    "parent_conversion_rate": {
        "parent conversion rate",
    },
    "sub_category_bsr": {
        "sub category bsr",
        "subcategory bsr",
    },
    "average_price": {
        "average price",
    },
    "best_deal": {
        "best deal",
    },
    "coupon": {
        "coupon",
    },
    "sales": {
        "sales",
    },
    "sales_ly": {
        "sales ly",
    },
    "sales_yoy_change": {
        "sales yoy change",
    },
    "spend": {
        "spend",
    },
    "impressions": {
        "impressions",
    },
    "clicks": {
        "clicks",
    },
    "advertising_sales": {
        "advertising sales",
    },
    "organic_sales": {
        "organic sales",
    },
    "cpc": {
        "cpc",
    },
    "revenue_per_click": {
        "revenue per click",
    },
    "roas": {
        "roas",
    },
    "cost_per_acquisition": {
        "cost per acquisition",
    },
    "tacos": {
        "tacos",
    },
    "profitability": {
        "profitability",
        "profitablity",
    },
}


METRIC_ROW_ORDER = [
    "parent_pageviews",
    "parent_units_ordered",
    "parent_conversion_rate",
    "sub_category_bsr",
    "average_price",
    "best_deal",
    "coupon",
    "sales",
    "sales_ly",
    "sales_yoy_change",
    "spend",
    "impressions",
    "clicks",
    "advertising_sales",
    "organic_sales",
    "cpc",
    "revenue_per_click",
    "roas",
    "cost_per_acquisition",
    "tacos",
    "profitability",
]

PREFERRED_METRIC_DISPLAY_LABELS = {
    "parent_pageviews": "Parent Pageviews",
    "parent_units_ordered": "Parent Units Ordered",
    "parent_conversion_rate": "Parent Conversion Rate",
    "sub_category_bsr": "Sub Category BSR",
    "average_price": "Average Price",
    "best_deal": "Best Deal",
    "coupon": "Coupon",
    "sales": "Sales",
    "sales_ly": "Sales LY",
    "sales_yoy_change": "Sales YoY Change",
    "spend": "Spend",
    "impressions": "Impressions",
    "clicks": "Clicks",
    "advertising_sales": "Advertising Sales",
    "organic_sales": "Organic Sales",
    "cpc": "CPC",
    "revenue_per_click": "Revenue Per Click",
    "roas": "ROAS",
    "cost_per_acquisition": "Cost Per Acquisition",
    "tacos": "TACoS",
    "profitability": "Profitability",
}


def get_preferred_metric_label(metric_key: str) -> str:
    return PREFERRED_METRIC_DISPLAY_LABELS.get(metric_key, metric_key)


def match_structure_label(cell_value: Optional[str]) -> Optional[str]:
    """
    Return the canonical structure key if the cell matches one of our known aliases.
    """
    normalized = normalize_label(cell_value)

    for canonical_key, aliases in STRUCTURE_LABEL_ALIASES.items():
        if normalized in aliases:
            return canonical_key

    return None


def match_metric_label(cell_value: Optional[str]) -> Optional[str]:
    """
    Return the canonical metric key if the cell matches one of our known metric aliases.
    """
    normalized = normalize_label(cell_value)

    for canonical_key, aliases in METRIC_LABEL_ALIASES.items():
        if normalized in aliases:
            return canonical_key

    return None