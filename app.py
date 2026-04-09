# Nama file: app.py
import streamlit as st
from utils import init_session_state

# --- Mengimpor modul dari file lain ---
import tab1_input
import tab2_scoring
import tab3_kmeans

# --- PENGATURAN HALAMAN (Harus di awal file utama) ---
# Mengubah initial_sidebar_state menjadi "collapsed" agar sidebar tersembunyi secara default saat refresh
st.set_page_config(page_title="DSS & AI Clustering Bapperida", layout="wide", initial_sidebar_state="collapsed")

# --- INISIALISASI MEMORI ---
init_session_state()

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.title("🧭 Navigasi Menu")
    st.markdown("Pilih menu di bawah ini untuk berpindah halaman.")
    st.markdown("---")

    menu_list = [
        "📝 Input Data Indikator", 
        "🏆 Peringkat Akumulasi (Scoring)",
        "🗺️ AI Peta Zonasi (K-Means)"
    ]

    # Mencoba membaca URL parameters untuk mengingat menu terakhir yang dibuka pengguna
    try:
        query_params = st.query_params
        default_menu = query_params.get("menu", menu_list[0])
        if default_menu not in menu_list:
            default_menu = menu_list[0]
    except AttributeError:
        # Fallback/cadangan apabila menggunakan Streamlit versi lama (< 1.30)
        query_params = st.experimental_get_query_params()
        default_menu = query_params.get("menu", [menu_list[0]])[0]
        if default_menu not in menu_list:
            default_menu = menu_list[0]

    # Pastikan memori menu aktif sinkron dengan URL
    if "active_menu_selector" not in st.session_state:
        st.session_state.active_menu_selector = default_menu

    def ganti_menu(menu_baru):
        """Fungsi yang dipanggil untuk mengubah memori dan URL saat tombol ditekan"""
        st.session_state.active_menu_selector = menu_baru
        try:
            st.query_params["menu"] = menu_baru
        except AttributeError:
            st.experimental_set_query_params(menu=menu_baru)

    # Widget Tombol sebagai pengganti Radio
    for menu in menu_list:
        # Jika menu ini adalah menu yang sedang aktif, jadikan tombolnya berwarna (primary)
        tipe_tombol = "primary" if st.session_state.active_menu_selector == menu else "secondary"
        
        if st.button(menu, type=tipe_tombol, use_container_width=True):
            ganti_menu(menu)
            st.rerun()
    
    st.markdown("---")
    st.caption("✨ DSS & AI Spasial Bapperida")

# Ambil menu yang sedang aktif dari session state
selected_menu = st.session_state.active_menu_selector

# --- HEADER APLIKASI (KONTEN UTAMA) ---
st.title("📊 Sistem Pendukung Keputusan & AI Spasial")
st.markdown("Aplikasi ini menggabungkan metode *Scoring* tradisional dengan *Machine Learning* (K-Means) untuk menentukan prioritas wilayah secara cerdas.")
st.markdown("---")

# --- MEMANGGIL FUNGSI DARI MASING-MASING FILE BERDASARKAN MENU ---
if selected_menu == menu_list[0]:
    tab1_input.render_tab1()
elif selected_menu == menu_list[1]:
    tab2_scoring.render_tab2()
elif selected_menu == menu_list[2]:
    tab3_kmeans.render_tab3()