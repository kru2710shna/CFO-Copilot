import pandas as pd
import pytest
from agent.metrics import (
    get_revenue_vs_budget,
    get_gross_margin_trend,
    get_cash_runway,
    get_opex_ratio,
    get_revenue_growth,
    get_burn_multiple,
    get_entity_revenue,
    get_ebitda_trend
)


def make_fake_data():
    data = [
        ("2023-01", "ParentCo", "Revenue", "actual", 1000),
        ("2023-01", "ParentCo", "Revenue", "budget", 1200),
        ("2023-01", "ParentCo", "COGS", "actual", 400),
        ("2023-01", "ParentCo", "Opex:Sales", "actual", 200),

        ("2023-02", "ParentCo", "Revenue", "actual", 1500),
        ("2023-02", "ParentCo", "Revenue", "budget", 1400),
        ("2023-02", "ParentCo", "COGS", "actual", 500),
        ("2023-02", "ParentCo", "Opex:Sales", "actual", 300),

        ("2023-03", "ParentCo", "Revenue", "actual", 800),
        ("2023-03", "ParentCo", "COGS", "actual", 400),
        ("2023-03", "ParentCo", "Opex:Sales", "actual", 600),
    ]
    df = pd.DataFrame(data, columns=["month", "entity", "account_category", "type", "amount_usd"])
    df["month"] = pd.to_datetime(df["month"])

    cash_data = [
        ("2023-01", "Consolidated", 10000),
        ("2023-02", "Consolidated", 9000),
        ("2023-03", "Consolidated", 8000),
    ]
    cash_df = pd.DataFrame(cash_data, columns=["month", "entity", "cash_usd"])
    cash_df["month"] = pd.to_datetime(cash_df["month"])
    return df, cash_df


# ---------------- REVENUE VS BUDGET ----------------

def test_revenue_vs_budget_basic():
    df, _ = make_fake_data()
    result = get_revenue_vs_budget(df, "2023-01")
    assert result["actual"] == 1000
    assert result["budget"] == 1200
    assert result["variance"] == -200
    assert round(result["variance_pct"], 1) == -16.7


def test_revenue_vs_budget_favorable_variance():
    df, _ = make_fake_data()
    result = get_revenue_vs_budget(df, "2023-02")
    assert result["actual"] == 1500
    assert result["budget"] == 1400
    assert result["variance"] == 100
    assert result["variance_pct"] > 0


def test_revenue_vs_budget_no_budget_data():
    df, _ = make_fake_data()
    df = df[df["type"] != "budget"]  # remove budgets
    result = get_revenue_vs_budget(df, "2023-01")
    assert result["budget"] == 0
    assert result["variance_pct"] in [None, 0]


# ---------------- GROSS MARGIN ----------------

def test_gross_margin_trend_contains_gm_pct():
    df, _ = make_fake_data()
    trend = get_gross_margin_trend(df, 2)
    assert "gm_pct" in trend.columns


def test_gross_margin_last_month_calculation():
    df, _ = make_fake_data()
    trend = get_gross_margin_trend(df, 3)
    last_row = trend.iloc[-1]
    # GM% = (800-400)/800 = 50%
    assert round(last_row["gm_pct"], 1) == 50.0


def test_gross_margin_handles_zero_revenue():
    df, _ = make_fake_data()
    # Add a row with 0 revenue, ensure month is datetime
    new_row = pd.DataFrame(
        [["2023-04", "ParentCo", "Revenue", "actual", 0]], 
        columns=df.columns
    )
    new_row["month"] = pd.to_datetime(new_row["month"])
    df = pd.concat([df, new_row])

    trend = get_gross_margin_trend(df, 4)
    # Ensure no division error (should safely handle zero revenue)
    assert "gm_pct" in trend.columns
    assert not trend["gm_pct"].isna().all()


# ---------------- CASH RUNWAY ----------------

def test_cash_runway_basic():
    df, cash_df = make_fake_data()
    result = get_cash_runway(df, cash_df)
    assert "cash_now" in result
    assert "runway_months" in result


def test_cash_runway_negative_burn():
    df, cash_df = make_fake_data()
    cash_df["cash_usd"] = [10000, 11000, 12000]  # increasing cash
    result = get_cash_runway(df, cash_df)
    assert result["runway_months"] in [float("inf"), "∞ (profitable / not burning)"]


def test_cash_runway_handles_single_month():
    df, cash_df = make_fake_data()
    cash_df = cash_df.iloc[:1]  # keep one row
    result = get_cash_runway(df, cash_df)
    assert "runway_months" in result


def test_cash_runway_exactly_zero_burn():
    df, cash_df = make_fake_data()
    cash_df["cash_usd"] = [10000, 10000, 10000]
    result = get_cash_runway(df, cash_df)
    assert result["avg_burn"] == 0
    assert result["runway_months"] in [float("inf"), "∞ (profitable / not burning)"]

# OTHER TESTING 


def test_opex_ratio_basic():
    df, _ = make_fake_data()
    result = get_opex_ratio(df, "2023-01")
    # Opex = 200, Revenue = 1000 → Ratio = 20%
    assert result["opex"] == 200
    assert result["revenue"] == 1000
    assert round(result["opex_ratio_pct"], 1) == 20.0


def test_opex_ratio_no_revenue():
    df, _ = make_fake_data()
    # Remove revenue rows
    df = df[df["account_category"] != "Revenue"]
    result = get_opex_ratio(df, "2023-01")
    assert result["revenue"] == 0
    assert result["opex_ratio_pct"] is None


def test_revenue_growth_trend():
    df, _ = make_fake_data()
    growth = get_revenue_growth(df, 3)
    assert "growth_pct" in growth.columns
    # Growth from Jan (1000) → Feb (1500) = +50%
    feb = growth[growth["month"] == "2023-02"].iloc[0]
    assert round(feb["growth_pct"], 1) == 50.0


def test_burn_multiple_basic():
    df, cash_df = make_fake_data()
    result = get_burn_multiple(df, cash_df, n_months=2)
    assert "burn_multiple" in result
    # Should return a finite or None value depending on data
    assert result["burn_multiple"] is None or isinstance(result["burn_multiple"], float)


# Test prompts
# What was revenue vs budget in January 2023?
# What was revenue vs budget in January 2023?
#  