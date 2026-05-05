# views/tab1_input/profil_dasar.py
import streamlit as st
from utils.state_manager import simpan_profil_dasar

# Mengimpor modul yang sudah dipecah
from views.tab1_input.profil_dasar_aktif import render_tab_aktif
from views.tab1_input.profil_dasar_import import render_tab_import

def render_profil_dasar():
    st.subheader("🏢 Bagian A: Profil Dasar Wilayah")
    st.markdown("Data **Luas Daerah** dan **Jumlah Penduduk** wajib ada dan akan digunakan sebagai patokan rasio (pembagi) oleh mesin AI K-Means untuk mencegah *Size Bias* (bias ukuran kewilayahan).")

    # Inisialisasi state untuk mengontrol Tab yang aktif
    if 'active_tab_profil' not in st.session_state:
        st.session_state.active_tab_profil = "🟢 Profil Aktif"
        
    if 'clear_profil_uploader' not in st.session_state:
        st.session_state.clear_profil_uploader = False

    # Deteksi dan konversi memori usang ke "Jumlah Penduduk 2026" jika ada
    if "Jumlah Penduduk (Jiwa)" in st.session_state.data_dasar.columns:
        st.session_state.data_dasar.rename(columns={"Jumlah Penduduk (Jiwa)": "Jumlah Penduduk 2026"}, inplace=True)
        simpan_profil_dasar(st.session_state.data_dasar, st.session_state.sumber_profil)

    # --- UI TERBAGI MENJADI 2 TAB ---
    tabs_list = ["🟢 Profil Aktif", "📁 Import File Custom (.xlsx / .csv)"]
    
    try:
        default_idx = tabs_list.index(st.session_state.active_tab_profil)
    except ValueError:
        default_idx = 0

    tab_aktif, tab_import = st.tabs(tabs_list)

    with tab_aktif:
        # Memanggil file logika tampilan tabel
        render_tab_aktif()

    with tab_import:
        # Memanggil file logika pengunggahan data
        render_tab_import()