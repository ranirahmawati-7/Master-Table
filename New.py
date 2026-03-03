import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard Master Table",
    layout="wide"
)

def bagian_1_proyeksi():
    import plotly.express as px
    import plotly.graph_objects as go
    import re

    # ===============================
    # HEADER DENGAN LOGO
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
                Analisis Nilai perkiraan Outstanding Pertanggungan, GWP, Total Pertanggungan, Total Recoveries, Loss Ratio, Cadangan Klaim, Cadangan Premi, Claim Outstanding, Claim Paid, Klaim dan Proporsi jumlah klaim berbasis data periodik
            </p>
            """,
            unsafe_allow_html=True
        )

        st.info("Website ini akan otomatis menampilkan dashboard untuk perhitungan nilai dan Summary Data setelah anda mengupload file dengan format xlxs atau csv, dan pastikan format tabel yang akan diinput sesuai dengan contoh")
        st.image(
        "gambar/xlsxPic2.png",
        caption="Contoh format file Excel (.xlsx) yang didukung",
        use_container_width=True
    )

        st.title("📊 Dashboard Master Table")
    
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
    # GET SHEET NAMES
    # ===============================
    if uploaded_file.name.endswith(".xlsx"):
        sheet_names = pd.ExcelFile(uploaded_file).sheet_names
    else:
        sheet_names = ["CSV"]

    # Skip sheet Proyeksi
    #sheet_names = [s for s in sheet_names if s.lower() != "proyeksi"]
    
    # ===============================
    # LOAD DATA
    # ===============================
    @st.cache_data(show_spinner=False)
    def load_data(file, sheet=None):
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        return pd.read_excel(file, sheet_name=sheet)
    
    # ===============================
    # PARSE VALUE (FORMAT INDONESIA)
    # ===============================
    def parse_value(val):
        if pd.isna(val):
            return None
        if isinstance(val, (int, float)):
            return float(val)
    
        text = str(val).strip()
        if "." in text and "," in text:
            text = text.replace(".", "").replace(",", ".")
        elif "." in text:
            text = text.replace(".", "")
    
        try:
            return float(text)
        except:
            return None
    
    # ===============================
    # LOOP PER SHEET
    # ===============================
    for sheet in sheet_names:
    
        st.divider()
        st.header(f"📘 by {sheet}")
    
        df_raw = load_data(uploaded_file, sheet if sheet != "CSV" else None)
    
        if df_raw.empty:
            st.warning("Sheet kosong")
            continue
    
        # ===============================
        # VALIDASI STRUKTUR MINIMAL
        # ===============================
        cols = list(df_raw.columns)
    
        if len(cols) < 5:
            st.warning("Struktur kolom tidak memenuhi standar → dilewati")
            continue
    
        # ===============================
        # MAPPING BERDASARKAN POSISI KOLOM
        # ===============================

        COL_PERIODE = cols [0]
        COL_Institusi = cols[1]
        COL_DIMENSI = cols[2]   # <<< KUNCI UTAMA
        COL_METRICS = "Metrics"
        COL_VALUE = "Value"
    
        dimensi_label = COL_DIMENSI  # Untuk UI
    
        df = df_raw.rename(columns={
            COL_PERIODE: "Periode",
            COL_Institusi: "Institusi",
            COL_DIMENSI: "Dimensi"
        })

        # ===============================
        # CLEAN VALUE
        # ===============================
        if "Value" in df.columns:
            df["Value"] = df["Value"].apply(parse_value)
        else:
            st.warning("Kolom Value tidak ditemukan")
            continue
    
        # ===============================
        # PREVIEW DATA
        # ===============================
        with st.expander("👀 Preview Data", expanded=False):
            df_prev = df.copy()
    
            if "Metrics" in df_prev.columns:
                def fmt(row):
                    if "debitur" in str(row["Metrics"]).lower():
                        return f"{row['Value']:,.0f}" if pd.notna(row["Value"]) else ""
                    return f"Rp {row['Value']:,.2f}" if pd.notna(row["Value"]) else ""
    
                df_prev["Value"] = df_prev.apply(fmt, axis=1)
    
            st.dataframe(df_prev, use_container_width=True)
    
        # ===============================
        # FILTER (STRUKTURAL)
        # ===============================
        c1, c2, c3 = st.columns(3)
    
        with c1:
            per = st.multiselect(
                "📅 Periode",
                sorted(df["Periode"].dropna().unique()),
                default=sorted(df["Periode"].dropna().unique()),
                key=f"per_{sheet}"
            )

        with c2:
            kp = st.multiselect(
                "🏦 Institusi",
                sorted(df["Institusi"].dropna().unique()),
                default=sorted(df["Institusi"].dropna().unique()),
                key=f"kp_{sheet}"
            )

        with c3:
            dim = st.multiselect(
                f"🏷️ {dimensi_label}",
                sorted(df["Dimensi"].dropna().unique()),
                default=sorted(df["Dimensi"].dropna().unique()),
                key=f"dim_{sheet}"
            )

        df_f = df[
            df["Periode"].isin(per) &
            df["Institusi"].isin(kp) &
            df["Dimensi"].isin(dim)
        ]
    
        if df_f.empty:
            st.warning("Data kosong setelah filter")
            continue
        #=============================================================================
        # ===============================
# ==============================
# DATA PREPARATION
# ==============================
        df["Tahun"] = df["Tahun"].astype(str)

# ==============================
# SIDEBAR FILTER
# ==============================
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

# ==============================
# TOTAL OUTSTANDING
# ==============================
total_outstanding = df_filtered["Total_Nilai_Pertanggungan"].sum()

st.metric("Total Outstanding Pertanggungan",
          f"Rp {total_outstanding:,.0f}")

# ==============================
# CHART 1 - OUTSTANDING PER TAHUN
# ==============================
st.markdown("### 📈 Outstanding per Tahun")

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

fig_year.update_layout(yaxis_title="Total Outstanding")

st.plotly_chart(fig_year, use_container_width=True)

# ==============================
# CHART 2 - OUTSTANDING PER INSTITUSI
# ==============================
st.markdown("### 🏦 Outstanding per Institusi")

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

fig_inst.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig_inst, use_container_width=True)

# ==============================
# CHART 3 - TREND PER INSTITUSI
# ==============================
st.markdown("### 📊 Trend Outstanding per Tahun & Institusi")

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
