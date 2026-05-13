# app.py
import streamlit as st
from utils.state_manager import init_session_state

# --- IMPORT SEMUA VIEW ---
from views.home import render_home
from views.tab1_input import render_tab1
from views.tab2_scoring import render_tab2
from views.tab3_kmeans import render_tab3
from views.panduan import render_panduan

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="MURIA Bapperida", page_icon="🏔️", layout="wide", initial_sidebar_state="expanded")

# --- INJEKSI CSS KUSTOM (MENGECILKAN SIDEBAR) ---
st.markdown("""
    <style>
        /* Mengecilkan lebar sidebar HANYA saat posisinya terbuka (expanded) */
        [data-testid="stSidebar"][aria-expanded="true"] {
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
        "🗺️ AI Peta Zonasi",
        "📖 Panduan Sistem"
    ]

    # MENGAMBIL PARAMETER URL (Untuk mendeteksi tombol Back Browser)
    try:
        url_menu = st.query_params.get("menu", menu_list[0])
    except AttributeError:
        url_params = st.experimental_get_query_params()
        url_menu = url_params.get("menu", [menu_list[0]])[0]

    # Validasi menu dari URL
    if url_menu not in menu_list:
        url_menu = menu_list[0]
        
    # Sinkronisasi state internal dengan URL yang baru dibaca
    st.session_state.active_menu_selector = url_menu

    # Callback untuk tombol menu
    def set_menu(menu_tujuan):
        st.session_state.active_menu_selector = menu_tujuan
        try:
            st.query_params["menu"] = menu_tujuan
            # Bersihkan subpage jika berpindah menu utama
            if "subpage" in st.query_params:
                del st.query_params["subpage"]
        except AttributeError:
            st.experimental_set_query_params(menu=menu_tujuan)

    # Membuat tombol native Streamlit
    for menu in menu_list:
        tipe_tombol = "primary" if st.session_state.active_menu_selector == menu else "secondary"
        
        # Ganti logika ke on_click agar state ter-update sebelum halaman dimuat ulang
        st.button(menu, type=tipe_tombol, use_container_width=True, on_click=set_menu, args=(menu,))
    
    st.markdown("---")
    
    # --- FITUR PROJECT KEY (RUANG KERJA) ---
    with st.expander("⚙️ Pengaturan Ruang Kerja Lanjutan", expanded=False):
        pj_key = st.text_input(
            "🔑 Kunci Proyek:", 
            value=st.session_state.get('project_key', 'publik'),
            help="Gunakan kunci yang sama dengan rekan Anda untuk berkolaborasi pada data yang sama."
        )
        # Jika user mengubah kunci proyek
        if pj_key.strip().lower() != st.session_state.get('project_key', 'publik'):
            st.session_state['project_key'] = pj_key.strip().lower()
            # Hapus cache memori agar data baru dimuat dari file JSON yang sesuai
            if 'koleksi_tabel' in st.session_state:
                del st.session_state['koleksi_tabel']
            if 'hasil_kmeans' in st.session_state:
                del st.session_state['hasil_kmeans']
            st.rerun()

    st.caption("✨ MURIA - Kabupaten Kudus")

selected_menu = st.session_state.active_menu_selector

# --- HEADER APLIKASI (KONTEN UTAMA) ---
st.title("📊 MURIA: Multidimensional Regional Intelligent Analytics")
st.markdown("Aplikasi ini menggabungkan metode *Scoring* tradisional dengan *Machine Learning* (K-Means) untuk menentukan prioritas wilayah secara cerdas.")
st.markdown("---")

# --- ROUTING HALAMAN APLIKASI ---
if selected_menu == menu_list[0]:
    render_home()
elif selected_menu == menu_list[1]:
    render_tab1()
elif selected_menu == menu_list[2]:
    render_tab2()
elif selected_menu == menu_list[3]:
    render_tab3()
elif selected_menu == menu_list[4]:
    render_panduan() 

# FITUR BARU: GLOBAL FOOTER & WATERMARK
st.markdown("""
    <div style="margin-top: 5rem; padding-top: 2rem; border-top: 1px solid #e6e6e6; text-align: center; color: #888;">
        <p style="margin-bottom: 0px; font-size: 0.9rem;">
            <b>MURIA (Multidimensional Regional Intelligent Analytics) v1.0.0</b>
        </p>
        <p style="font-size: 0.8rem; margin-top: 5px;">
            &copy; 2026 Badan Perencanaan Pembangunan, Riset, dan Inovasi Daerah (Bapperida) Kabupaten Kudus.<br>
            <i>Sistem Pendukung Keputusan Berbasis Machine Learning.</i>
        </p>
    </div>
""", unsafe_allow_html=True)