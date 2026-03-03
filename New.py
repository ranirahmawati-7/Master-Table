import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Master Table",
    layout="wide"
)

# ===============================
# HEADER
# ===============================
col_logo, col_title = st.columns([1, 8])

with col_logo:
    st.image("gambar/OIP.jpg", width=90)

with col_title:
    st.markdown(
        """
        <h1 style="margin-bottom:0; color:#1f4e79;">
            Dashboard Master Table
        </h1>
        <p style="margin-top:0; font-size:16px; color:gray;">
            Analisis Outstanding Pertanggungan & Summary Data
        </p>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ===============================
# UPLOAD FILE
# ===============================
uploaded_file = st.file_uploader(
    "📥 Upload file Excel / CSV",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.info("Silakan upload file terlebih dahulu")
    st.stop()

# ===============================
# LOAD DATA
# ===============================
if uploaded_file.name.endswith(".xlsx"):
    sheet_names = pd.ExcelFile(uploaded_file).sheet_names
    selected_sheet = st.selectbox("Pilih Sheet", sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
else:
    df = pd.read_csv(uploaded_file)

# ===============================
# VALIDASI KOLOM WAJIB
# ===============================
required_cols = ["Institusi", "Tahun", "Total_Nilai_Pertanggungan"]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Kolom '{col}' tidak ditemukan dalam file.")
        st.stop()

df["Tahun"] = df["Tahun"].astype(str)

# ===============================
# SIDEBAR FILTER
# ===============================
st.sidebar.header("Filter Data")

institusi = st.sidebar.multiselect(
    "Pilih Institusi",
    options=df["Institusi"].unique(),
    default=df["Institusi"].unique()
)

tahun = st.sidebar.multiselect(
    "Pilih Tahun",
    options=df["Tahun"].unique(),
    default=df["Tahun"].unique()
)

df_filtered = df[
    (df["Institusi"].isin(institusi)) &
    (df["Tahun"].isin(tahun))
]

if df_filtered.empty:
    st.warning("Data kosong setelah filter")
    st.stop()

# ===============================
# METRIC
# ===============================
total_outstanding = df_filtered["Total_Nilai_Pertanggungan"].sum()

st.metric(
    "Total Outstanding Pertanggungan",
    f"Rp {total_outstanding:,.0f}"
)

st.divider()

# ===============================
# CHART 1 - PER TAHUN
# ===============================
st.subheader("📈 Outstanding per Tahun")

year_summary = (
    df_filtered
    .groupby("Tahun")["Total_Nilai_Pertanggungan"]
    .sum()
    .reset_index()
)

fig_year = px.bar(
    year_summary,
    x="Tahun",
    y="Total_Nilai_Pertanggungan",
    text_auto=True
)

st.plotly_chart(fig_year, use_container_width=True)

# ===============================
# CHART 2 - PER INSTITUSI
# ===============================
st.subheader("🏦 Outstanding per Institusi")

inst_summary = (
    df_filtered
    .groupby("Institusi")["Total_Nilai_Pertanggungan"]
    .sum()
    .reset_index()
)

fig_inst = px.bar(
    inst_summary,
    x="Institusi",
    y="Total_Nilai_Pertanggungan",
    text_auto=True
)

st.plotly_chart(fig_inst, use_container_width=True)

# ===============================
# CHART 3 - TREND
# ===============================
st.subheader("📊 Trend Outstanding")

trend_data = (
    df_filtered
    .groupby(["Tahun", "Institusi"])["Total_Nilai_Pertanggungan"]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    trend_data,
    x="Tahun",
    y="Total_Nilai_Pertanggungan",
    color="Institusi",
    markers=True
)

st.plotly_chart(fig_trend, use_container_width=True)
