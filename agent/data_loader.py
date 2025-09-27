import pandas as pd

def load_data(filepath: str):
    """
    Load and normalize actuals, budget, cash, and fx data from Excel.

    Returns:
        combined_df (pd.DataFrame): unified actuals + budget data
            Columns: [month, entity, account_category, type, amount_usd]
        cash_df (pd.DataFrame): cash balances
            Columns: [month, entity, cash_usd]
    """

    # --- Load sheets ---
    actuals = pd.read_excel(filepath, sheet_name="actuals")
    budget = pd.read_excel(filepath, sheet_name="budget")
    cash = pd.read_excel(filepath, sheet_name="cash")
    fx = pd.read_excel(filepath, sheet_name="fx")

    # --- Normalize months: force all to YYYY-MM period ---
    for df in [actuals, budget, cash, fx]:
        df["month"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce").dt.to_period("M")

    # --- Ensure USD is present in FX table ---
    if not ((fx["currency"] == "USD") & (fx["rate_to_usd"] == 1.0)).any():
        usd_months = fx["month"].unique()
        fx = pd.concat([
            fx,
            pd.DataFrame({
                "month": usd_months,
                "currency": "USD",
                "rate_to_usd": 1.0
            })
        ], ignore_index=True)

    # --- Convert actuals to USD ---
    actuals = actuals.merge(fx, on=["month", "currency"], how="left")
    actuals["amount_usd"] = actuals["amount"] * actuals["rate_to_usd"]
    actuals["type"] = "actual"

    # --- Convert budget to USD ---
    budget = budget.merge(fx, on=["month", "currency"], how="left")
    budget["amount_usd"] = budget["amount"] * budget["rate_to_usd"]
    budget["type"] = "budget"

    # --- Combine actuals + budget ---
    combined = pd.concat([actuals, budget], ignore_index=True)
    combined = combined[["month", "entity", "account_category", "type", "amount_usd"]]

    # --- Clean cash ---
    cash["cash_usd"] = cash["cash_usd"].astype(float)
    cash = cash[["month", "entity", "cash_usd"]]

    # --- Convert Period back to timestamp for easy plotting ---
    combined["month"] = combined["month"].dt.to_timestamp()
    cash["month"] = cash["month"].dt.to_timestamp()

    return combined, cash


if __name__ == "__main__":
    combined_df, cash_df = load_data("../fixtures/data.xlsx")
    print("Combined head:\n", combined_df.head(10))
    print("\nCash head:\n", cash_df.head(10))
