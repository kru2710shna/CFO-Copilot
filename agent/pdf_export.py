from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import pandas as pd
import io

def export_pdf(filepath, combined_df, cash_df):
    """
    Create a simple 2-page PDF with:
    - Revenue vs Budget (latest month)
    - Cash Balance trend with runway
    """
    # --- Setup ---
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # --- Latest month ---
    latest_month = combined_df["month"].max().to_period("M")
    rev_data = combined_df[
        (combined_df["month"].dt.to_period("M") == latest_month) &
        (combined_df["account_category"] == "Revenue")
    ]

    actual = rev_data.loc[rev_data["type"] == "actual", "amount_usd"].sum()
    budget = rev_data.loc[rev_data["type"] == "budget", "amount_usd"].sum()
    variance = actual - budget
    variance_pct = (variance / budget * 100) if budget != 0 else 0

    # --- Revenue vs Budget chart ---
    fig, ax = plt.subplots()
    ax.bar(["Actual", "Budget"], [actual, budget], color=["#2b83ba", "#abdda4"])
    ax.set_title(f"Revenue vs Budget ({latest_month})")
    ax.set_ylabel("USD")
    for i, v in enumerate([actual, budget]):
        ax.text(i, v + (v*0.02), f"${v:,.0f}", ha="center")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    # --- Add to PDF ---
    elements.append(Paragraph(f"<b>Revenue vs Budget ({latest_month})</b>", styles['Title']))
    elements.append(Paragraph(
        f"Revenue = ${actual:,.0f}, Budget = ${budget:,.0f}, Variance = {variance:,.0f} ({variance_pct:.1f}%).",
        styles['Normal']
    ))
    elements.append(Spacer(1, 12))
    elements.append(Image(buf, width=400, height=250))
    elements.append(Spacer(1, 24))

    # --- Cash trend ---
    latest_cash_month = cash_df["month"].max().to_period("M")
    cash_now = cash_df.loc[cash_df["month"].dt.to_period("M") == latest_cash_month, "cash_usd"].sum()

    fig, ax = plt.subplots()
    ax.plot(cash_df["month"], cash_df["cash_usd"], marker="o")
    ax.set_title("Cash Balance Trend")
    ax.set_ylabel("USD")
    plt.xticks(rotation=45)

    buf2 = io.BytesIO()
    plt.savefig(buf2, format="png")
    buf2.seek(0)
    plt.close(fig)

    elements.append(Paragraph("<b>Cash Balance Trend</b>", styles['Title']))
    elements.append(Paragraph(f"Current Cash Balance ({latest_cash_month}) = ${cash_now:,.0f}", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Image(buf2, width=400, height=250))

    # --- Build PDF ---
    doc.build(elements)
    return filepath
