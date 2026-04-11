# app.py
import streamlit as st
from utils.state_manager import init_session_state

# --- IMPORT SEMUA VIEW ---
from views.home import render_home
from views.tab1_input import render_tab1
from views.tab2_scoring import render_tab2
from views.tab3_kmeans import render_tab3

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="MURIA Bapperida", layout="wide", initial_sidebar_state="expanded")

# --- INJEKSI CSS KUSTOM (MENGECILKAN SIDEBAR) ---
st.markdown("""
    <style>
        /* Mengecilkan lebar sidebar bawaan Streamlit */
        [data-testid="stSidebar"] {
            min-width: 265px !important;
            max-width: 265px !important;
        }
        
        /* Merapikan sedikit padding di dalam sidebar agar tidak terlalu sesak */
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- INISIALISASI MEMORI ---
init_session_state()

# --- SIDEBAR NAVIGASI BAWAAN (STABIL) ---
with st.sidebar:
    st.title("🏔️ MURIA Bapperida")
    st.markdown("Pilih menu di bawah ini untuk berpindah halaman.")
    st.markdown("---")

    # Daftar menu dengan emoji sebagai ikon
    menu_list = [
        "🏠 Beranda Executive",
        "📝 Input Data Indikator", 
        "🏆 Peringkat Akumulasi",
        "🗺️ AI Peta Zonasi"
    ]

    # Menangani URL Query Parameters agar saat direfresh tidak kembali ke awal
    try:
        query_params = st.query_params
        default_menu = query_params.get("menu", menu_list[0])
        if default_menu not in menu_list:
            default_menu = menu_list[0]
    except AttributeError:
        query_params = st.experimental_get_query_params()
        default_menu = query_params.get("menu", [menu_list[0]])[0]
        if default_menu not in menu_list:
            default_menu = menu_list[0]

    if "active_menu_selector" not in st.session_state:
        st.session_state.active_menu_selector = default_menu

    def ganti_menu(menu_baru):
        st.session_state.active_menu_selector = menu_baru
        try:
            st.query_params["menu"] = menu_baru
        except AttributeError:
            st.experimental_set_query_params(menu=menu_baru)

    # Membuat tombol native Streamlit yang dijamin responsif (tanpa double click)
    for menu in menu_list:
        tipe_tombol = "primary" if st.session_state.active_menu_selector == menu else "secondary"
        
        if st.button(menu, type=tipe_tombol, use_container_width=True):
            ganti_menu(menu)
            st.rerun() # Memaksa halaman langsung dimuat ulang seketika
    
    st.markdown("---")
    st.caption("✨ MURIA - Kabupaten Kudus")

selected_menu = st.session_state.active_menu_selector

# --- HEADER APLIKASI (KONTEN UTAMA) ---
st.title("📊 MURIA: Multidimensional Regional Intelligent Analytics")
st.markdown("Aplikasi ini menggabungkan metode *Scoring* tradisional dengan *Machine Learning* (K-Means) untuk menentukan prioritas wilayah secara cerdas.")
st.markdown("---")

# --- MEMANGGIL TAMPILAN BERDASARKAN MENU ---
if selected_menu == menu_list[0]:
    render_home()
elif selected_menu == menu_list[1]:
    render_tab1()
elif selected_menu == menu_list[2]:
    render_tab2()
elif selected_menu == menu_list[3]:
    render_tab3()