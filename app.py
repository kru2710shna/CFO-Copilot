import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile

from agent.data_loader import load_data
from agent.metrics import (
    get_revenue_vs_budget,
    get_gross_margin_trend,
    get_opex_breakdown,
    get_cash_runway,
)
from agent.planner import classify_query, extract_month, extract_n_months
from agent.pdf_export import export_pdf

# --- Load data once ---
@st.cache_data
def get_data():
    combined, cash = load_data("fixtures/data.xlsx")
    return combined, cash

combined_df, cash_df = get_data()

# --- Streamlit Layout ---
st.set_page_config(page_title="CFO Copilot", layout="wide")
st.title("💼 CFO Copilot")
st.caption("Talk to your financials *or* explore an always-on analytics dashboard.")

# ----------------- KPI Cards -----------------
latest_month = combined_df["month"].max().strftime("%Y-%m")
rvb_latest = get_revenue_vs_budget(combined_df, latest_month)
gm_latest = get_gross_margin_trend(combined_df, 1)
gm_value = f"{gm_latest['gm_pct'].iloc[-1]:.1f}%" if not gm_latest.empty else "N/A"
opex_latest = get_opex_breakdown(combined_df, latest_month)["amount_usd"].sum()
cash_latest = get_cash_runway(combined_df, cash_df)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    delta = rvb_latest["variance"]
    st.metric(
        label=f"💰 Revenue ({latest_month})",
        value=f"${rvb_latest['actual']:,.0f}",
        delta=f"{delta:,.0f} vs Budget",
        delta_color="normal",
    )
with kpi2:
    st.metric(label="📈 Gross Margin", value=gm_value)
with kpi3:
    st.metric(label=f"🏢 Opex ({latest_month})", value=f"${opex_latest:,.0f}")
with kpi4:
    st.metric(
        label="💵 Cash Runway",
        value=f"{cash_latest['runway_months']} mo",
        delta=f"${cash_latest['cash_now']:,.0f}",
        delta_color="off",
    )

st.divider()

# ----------------- Dual Mode -----------------
tab1, tab2 = st.tabs(["🤖 Ask the CFO Agent", "📊 Explore Dashboard"])

with tab1:
    st.subheader("Ask me a finance question")
    query = st.text_input(
        "e.g., 'What was June 2025 revenue vs budget?' or 'Show last 3 months gross margin'"
    )

    if query:
        intent = classify_query(query)

        if not intent:
            st.warning("⚠️ I didn’t understand that. Try revenue, margin, opex, or cash runway.")
        else:
            # ---------------- Revenue vs Budget ----------------
            if intent == "revenue_vs_budget":
                month = extract_month(query) or latest_month
                result = get_revenue_vs_budget(combined_df, month)
                st.success(
                    f"💰 Revenue ({result['month']}) = **${result['actual']:,.0f}** "
                    f"vs Budget **${result['budget']:,.0f}** → "
                    f"Variance = {result['variance']:,.0f} ({result['variance_pct']}%)."
                )
                df_chart = pd.DataFrame(
                    {"Type": ["Actual", "Budget"], "Revenue": [result["actual"], result["budget"]]}
                )
                fig = px.bar(df_chart, x="Type", y="Revenue", text="Revenue")
                fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
                st.plotly_chart(fig, use_container_width=True)

            # ---------------- Gross Margin ----------------
            elif intent == "gross_margin_trend":
                n = extract_n_months(query, default=3)
                trend = get_gross_margin_trend(combined_df, n)
                if trend.empty:
                    st.warning("No gross margin data available.")
                else:
                    st.success(f"📈 Gross Margin % trend for last {n} months.")
                    fig = px.line(trend, x="month", y="gm_pct", markers=True)
                    fig.update_yaxes(title="GM %")
                    st.plotly_chart(fig, use_container_width=True)

            # ---------------- Opex Breakdown ----------------
            elif intent == "opex_breakdown":
                month = extract_month(query) or latest_month
                breakdown = get_opex_breakdown(combined_df, month)
                if breakdown.empty:
                    st.warning(f"No Opex data for {month}.")
                else:
                    st.success(f"🏢 Opex Breakdown ({month}).")
                    fig = px.pie(
                        breakdown,
                        names="category",
                        values="amount_usd",
                        title=f"Opex Breakdown ({month})",
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # ---------------- Cash Runway ----------------
            elif intent == "cash_runway":
                result = get_cash_runway(combined_df, cash_df)
                st.success(
                    f"💵 Cash Balance ({result['latest_month']}) = **${result['cash_now']:,.0f}**. "
                    f"📉 Avg Burn = **${result['avg_burn']:,.0f}** "
                    f"➡️ Runway = **{result['runway_months']} months**."
                )
                fig = px.line(
                    cash_df.assign(month=pd.to_datetime(cash_df["month"].astype(str))),
                    x="month", y="cash_usd", markers=True, line_shape="spline"
                )
                st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📊 Financial Dashboard")
    col1, col2 = st.columns(2)

    with col1:
        trend = get_gross_margin_trend(combined_df, 6)
        fig = px.line(trend, x="month", y="gm_pct", markers=True, title="Gross Margin Trend")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        month = latest_month
        breakdown = get_opex_breakdown(combined_df, month)
        fig = px.pie(breakdown, names="category", values="amount_usd", title="Opex Breakdown")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    fig_cash = px.line(
        cash_df.assign(month=pd.to_datetime(cash_df["month"].astype(str))),
        x="month", y="cash_usd", markers=True, line_shape="spline", title="Cash Balance Over Time"
    )
    st.plotly_chart(fig_cash, use_container_width=True)

# ---------------- Sidebar ----------------
st.sidebar.header("📑 Reports")
if st.sidebar.button("Export CFO Summary PDF"):
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    export_pdf(tmp_file.name, combined_df, cash_df)
    with open(tmp_file.name, "rb") as f:
        st.sidebar.download_button(
            "⬇️ Download CFO Summary",
            f,
            file_name="cfo_summary.pdf",
            mime="application/pdf",
        )
