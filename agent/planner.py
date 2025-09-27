import re
import pandas as pd

def classify_query(query: str):
    """
    Very simple rule-based classifier.
    Returns a string label identifying which metric function to call.
    """
    q = query.lower()

    if "revenue" in q and "budget" in q:
        return "revenue_vs_budget"
    elif "gross margin" in q or "gm" in q:
        return "gross_margin_trend"
    elif "opex" in q:
        return "opex_breakdown"
    elif "cash" in q and "runway" in q:
        return "cash_runway"
    else:
        return None


def extract_month(query: str):
    """
    Try to extract a month/year (e.g. 'June 2025', '2023-01') from query.
    Returns YYYY-MM string or None if not found.
    """
    # Try to find patterns like YYYY-MM
    m = re.search(r"(\d{4})[-/](\d{1,2})", query)
    if m:
        year, month = int(m.group(1)), int(m.group(2))
        return pd.Period(year=year, month=month, freq="M").strftime("%Y-%m")

    # Try to find formats like 'June 2025'
    m = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})", query.lower())
    if m:
        month_str, year = m.group(1), int(m.group(2))
        month_num = {
            "jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
            "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12
        }[month_str[:3]]
        return pd.Period(year=year, month=month_num, freq="M").strftime("%Y-%m")

    return None


def extract_n_months(query: str, default: int = 3):
    """
    Detect if CFO asked for 'last N months'.
    """
    m = re.search(r"last\s+(\d+)\s+month", query.lower())
    if m:
        return int(m.group(1))
    return default
