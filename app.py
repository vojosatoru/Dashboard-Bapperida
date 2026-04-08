# Nama file: app.py
import streamlit as st
from utils import init_session_state

# --- Mengimpor modul dari file lain ---
import tab1_input
import tab2_scoring
import tab3_kmeans

# --- PENGATURAN HALAMAN (Harus di awal file utama) ---
st.set_page_config(page_title="DSS & AI Clustering Bapperida", layout="wide")

# --- HEADER APLIKASI ---
st.title("📊 Sistem Pendukung Keputusan & AI Spasial")
st.markdown("Aplikasi ini menggabungkan metode *Scoring* tradisional dengan *Machine Learning* (K-Means) untuk menentukan prioritas wilayah secara cerdas.")
st.markdown("---")

# --- INISIALISASI MEMORI ---
init_session_state()

# --- NAVIGASI TABS ---
tab1, tab2, tab3 = st.tabs([
    "📝 Tab 1: Input Data Indikator", 
    "🏆 Tab 2: Peringkat Akumulasi (Scoring)",
    "🗺️ Tab 3: AI Peta Zonasi (K-Means)"
])

# --- MEMANGGIL FUNGSI DARI MASING-MASING FILE ---
with tab1:
    tab1_input.render_tab1()

with tab2:
    tab2_scoring.render_tab2()

with tab3:
    tab3_kmeans.render_tab3()