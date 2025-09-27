
# 💼 CFO Copilot – FP&A Agent Assignment  

An AI-powered **Financial Planning & Analysis (FP&A) assistant** that enables CFOs to query financial data in plain English and receive **board-ready answers with charts, KPIs, and reports**.  

This project was developed as part of a coding assignment to demonstrate **end-to-end agent design**, combining data ingestion, metric calculation, visualization, testing, and UX.  

---

## 📌 Problem Statement  

CFOs traditionally spend hours preparing financial summaries each month:  
- ⏳ Collecting data from ERP/finance systems  
- 🔄 Reconciling actuals vs. budget  
- 🧮 Calculating key metrics (Revenue, Gross Margin, Opex, Runway)  
- 📊 Designing charts for presentations  

The task was to **build a “CFO Copilot”** that allows natural questions like:  
- “What was June 2025 revenue vs budget?”  
- “Show me gross margin trends for the last 3 months”  
- “Break down Opex by category for March 2023”  
- “What is our cash runway right now?”  

The app should respond with **concise answers + visualizations**, and support exporting a **PDF summary** for board use.  

---

## 🛠️ Approach & Methodology  

We structured the project into **5 major phases**:  

### **1️⃣ Data Ingestion**
- Input provided: a single **Excel file (`data.xlsx`)** containing 4 sheets:  
  - `actuals` → Monthly actual financials  
  - `budget` → Budgeted financials  
  - `fx` → Currency exchange rates  
  - `cash` → Monthly cash balances  
- Implemented `agent/data_loader.py` to:  
  - Parse all sheets using **Pandas**  
  - Normalize and convert all values into **USD** (via FX)  
  - Combine into a single `combined_df` for metrics  
  - Keep `cash_df` separate for cash runway analysis  

---

### **2️⃣ Metric Functions** (📂 `agent/metrics.py`)  

- **Revenue vs Budget** → Actual vs budget with absolute + % variance  
- **Gross Margin %** → `(Revenue - COGS) / Revenue`  
- **Opex Breakdown** → Grouped by `Opex:*` categories  
- **Cash Runway** → `Cash ÷ Avg monthly net burn (last 3 months)`  

Each function returns **structured results**, consumable by both charts and text answers.  

---

### **3️⃣ Agent Layer (Intent Classification)** (📂 `agent/planner.py`)  

- Implemented a **lightweight intent classifier** based on keyword matching:  
  - `"revenue vs budget"` → `revenue_vs_budget`  
  - `"gross margin"` → `gross_margin_trend`  
  - `"opex"` → `opex_breakdown`  
  - `"cash runway"` → `cash_runway`  
- Helpers:  
  - `extract_month(query)` → Parses “June 2025”, “March 2023”  
  - `extract_n_months(query)` → Parses “last 3 months”, “last 6 months”  

---

### **4️⃣ Streamlit Frontend** (📂 `app.py`)  

- 🔍 **Text Input Box** → CFO asks natural questions  
- 🧠 **Planner** → Classifies intent & extracts parameters  
- 📊 **Visualization & KPIs**  
  - **KPI Summary Cards** (always visible): Revenue, GM%, Opex, Runway  
  - **Interactive Charts** via **Plotly Express**  
- 📑 **Sidebar → Export PDF** (using `agent/pdf_export.py`)  

---

### **5️⃣ Testing** (📂 `tests/test_metrics.py`)  

- Implemented **10 test cases** with `pytest`  
- Covered both **happy paths** and **edge cases**  

✅ **All 10 tests passed successfully**  

```bash
PYTHONPATH=. pytest -v
===========================================================
collected 10 items
===========================================================
10 passed in 0.70s
```  

---

## 🧪 Test Case List  

### 🔹 Revenue vs Budget  
1. **Basic case** (Jan 2023: actual 1000 vs budget 1200)  
2. **Favorable variance** (Feb 2023: actual > budget)  
3. **No budget available** → Handles gracefully  

### 🔹 Gross Margin %  
4. **Column existence check** → Ensures GM% field present  
5. **Correct GM% calculation** (March 2023 = 50%)  
6. **Zero revenue handling** → No division errors  

### 🔹 Cash Runway  
7. **Standard calculation** (burning cash → finite runway)  
8. **Negative burn** (increasing cash → infinite runway)  
9. **Single month of data** → Should not crash  
10. **Zero burn** (flat cash → infinite runway)  

---

## 📊 Example Queries (UI)  

- “What was **Feb 2023 revenue vs budget**?”  
- “Show me the **gross margin % trend** for the last 4 months”  
- “Break down **Opex by category** for March 2023”  
- “What is our **cash runway right now**?”  
- “Did we beat budget in any month this quarter?” (advanced phrasing)  

---

## 🧑‍💻 Tech Stack  

- **Python 3.11** 🐍  
- **Streamlit** 🎛️ → UI & dashboard  
- **Plotly Express** 📊 → Interactive charts  
- **Pandas** 🐼 → Data wrangling & metrics  
- **Pytest** ✅ → Testing & validation  
- **ReportLab** 📄 → PDF export  
- **Excel (xlsx)** 📑 → Input financial data  

---

## 📂 Project Structure  

```
hassment/
│── app.py                 # Streamlit frontend
│── fixtures/
│    └── data.xlsx          # Provided financial data
│── agent/
│    ├── data_loader.py     # Excel → combined dataset
│    ├── metrics.py         # Revenue, GM, Opex, Runway
│    ├── planner.py         # Intent classification
│    ├── pdf_export.py      # Export summary PDF
│── tests/
│    └── test_metrics.py    # 10 test cases
└── README.md
```

---

## ▶️ How to Run  

1. **Clone Repo**
```bash
git clone <repo_url>
cd hassment
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run Tests**
```bash
PYTHONPATH=. pytest -v
```

4. **Launch App**
```bash
streamlit run app.py
```

5. **Export PDF (optional)**  
- In the sidebar, click **“📑 Reports → Export CFO Summary PDF”**  

---

## 🎥 Demo (Suggested Flow)  

1. Ask: *“What was Feb 2023 revenue vs budget?”* → Bar chart  
2. Ask: *“Show me gross margin % trend for last 3 months”* → Line chart  
3. Ask: *“Break down Opex for March 2023”* → Pie chart  
4. Ask: *“What is our cash runway right now?”* → Line chart + KPI  
5. Export PDF → Share CFO Summary  

---

## 🌟 Outcomes  

- ✅ Built an **end-to-end financial assistant**  
- ✅ Added **KPI cards** + **visual dashboards**  
- ✅ Implemented **10 passing unit tests**  
- ✅ Delivered **PDF export for board reporting**  
- ✅ Provided **intuitive UX** for CFO-level queries  

---

## 🔮 Future Improvements  

- 🤖 **NLP-based intent classification** (LLM / spaCy instead of keyword rules)  
- 🗄️ **Database integration** (Postgres/BigQuery for scale)  
- 🌍 **Multi-entity & consolidation logic** (ParentCo + subsidiaries)  
- 📊 **More metrics** (EBITDA, Net Income, Working Capital)  
- ☁️ **Deploy on Streamlit Cloud / Hugging Face Spaces**  

---

## 👨‍💻 Author  

**Krushna Thakkar**  
Graduate Student – Artificial Intelligence (MSAI), San José State University  
🔗 [LinkedIn](https://www.linkedin.com/in/krushnathakkar/) | [GitHub](https://github.com/kru2710shna)  

---
