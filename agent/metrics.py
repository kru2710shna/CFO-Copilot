import pandas as pd


def get_revenue_vs_budget(combined_df: pd.DataFrame, month: str):
    """
    Calculate revenue vs budget for a given month.

    Args:
        combined_df: DataFrame from load_data()
        month: e.g., "2023-01"

    Returns:
        dict with actual, budget, variance, variance_pct
    """
    month = pd.to_datetime(month).to_period("M")
    data = combined_df[
        (combined_df["month"].dt.to_period("M") == month)
        & (combined_df["account_category"] == "Revenue")
    ]

    actual = data.loc[data["type"] == "actual", "amount_usd"].sum()
    budget = data.loc[data["type"] == "budget", "amount_usd"].sum()

    variance = actual - budget
    variance_pct = (variance / budget * 100) if budget != 0 else None

    return {
        "month": str(month),
        "actual": round(actual, 2),
        "budget": round(budget, 2),
        "variance": round(variance, 2),
        "variance_pct": round(variance_pct, 2) if variance_pct is not None else None,
    }


def get_gross_margin_trend(combined_df: pd.DataFrame, n_months: int = 3):
    """
    Compute Gross Margin % trend for last n_months.

    Returns:
        DataFrame with [month, revenue, cogs, gm_pct]
    """
    df = combined_df.copy()
    df["month"] = df["month"].dt.to_period("M")

    # Aggregate actuals only
    df = df[df["type"] == "actual"]

    summary = (
        df.groupby(["month", "account_category"])["amount_usd"]
        .sum()
        .unstack(fill_value=0)
    )
    summary["revenue"] = summary.get("Revenue", 0)
    summary["cogs"] = summary.get("COGS", 0)
    summary["gm_pct"] = (
        (summary["revenue"] - summary["cogs"]) / summary["revenue"] * 100
    ).replace([pd.NA, float("inf")], 0)

    trend = (
        summary[["revenue", "cogs", "gm_pct"]]
        .reset_index()
        .sort_values("month")
        .tail(n_months)
    )
    trend["month"] = trend["month"].astype(str)

    return trend


def get_opex_breakdown(combined_df: pd.DataFrame, month: str):
    """
    Opex breakdown by category for a given month.

    Returns:
        DataFrame with [category, amount_usd]
    """
    month = pd.to_datetime(month).to_period("M")
    df = combined_df[
        (combined_df["month"].dt.to_period("M") == month)
        & (combined_df["type"] == "actual")
        & (combined_df["account_category"].str.startswith("Opex"))
    ]

    # Extract category name after "Opex:"
    df = df.assign(category=df["account_category"].str.split(":").str[1])
    breakdown = (
        df.groupby("category")["amount_usd"]
        .sum()
        .reset_index()
        .sort_values("amount_usd", ascending=False)
    )

    return breakdown


def get_cash_runway(combined_df, cash_df):
    cash_df = cash_df.sort_values("month")
    latest = cash_df.iloc[-1]
    latest_month = latest["month"].strftime("%Y-%m")  # format nicely
    cash_now = latest["cash_usd"]

    # Compute avg burn (last 3 months)
    cash_df["delta"] = cash_df["cash_usd"].diff()
    recent_deltas = cash_df["delta"].tail(3)
    avg_burn = -recent_deltas.mean()  # negative change = burn

    if avg_burn <= 0 or pd.isna(avg_burn):
        runway = "∞ (profitable / not burning)"
        avg_burn_val = 0
    else:
        months_left = round(cash_now / avg_burn, 1)
        runway = months_left 
        avg_burn_val = avg_burn

    return {
        "latest_month": latest_month,
        "cash_now": cash_now,
        "avg_burn": avg_burn_val,
        "runway_months": runway,
    }
