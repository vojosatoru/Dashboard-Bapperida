# views/tab3_kmeans/ui_settings.py
import streamlit as st
from utils.state_manager import muat_config_kmeans, simpan_config_kmeans
from views.tab3_kmeans.ai_core import proses_kmeans

def render_pengaturan_ai(df_untuk_ai, df_master, fitur_tersedia):
    """Merender panel pengaturan AI di kolom kiri dan menjalankan algoritma."""
    st.markdown("#### ⚙️ Pengaturan AI")
    
    config_ai = muat_config_kmeans()
    
    # Saring history memori agar tidak error jika ada data yang dihapus di Tab 1
    saved_features = config_ai.get('ai_selected_features', fitur_tersedia)
    valid_features = [f for f in saved_features if f in fitur_tersedia]
    if not valid_features and fitur_tersedia:
        valid_features = fitur_tersedia

    # --- PERBAIKAN BUG DOUBLE CLICK ---
    # 1. Inisialisasi memori internal Streamlit (Hanya berjalan sekali saat awal)
    if 'ms_fitur_ai' not in st.session_state:
        st.session_state['ms_fitur_ai'] = valid_features
    else:
        # Sanitasi memastikan pilihan lama yang sudah dihapus tidak nyangkut
        st.session_state['ms_fitur_ai'] = [f for f in st.session_state['ms_fitur_ai'] if f in fitur_tersedia]

    # 2. Fungsi seketika (Callback) saat user mengklik Multiselect
    def update_fitur_config():
        config_ai['ai_selected_features'] = st.session_state['ms_fitur_ai']
        simpan_config_kmeans(config_ai)

    # 3. Multiselect kini dikendalikan oleh 'key', bukan 'default'
    fitur_terpilih = st.multiselect(
        "Pilih Indikator yang Dianalisis:", 
        fitur_tersedia, 
        key='ms_fitur_ai',
        on_change=update_fitur_config
    )
    # ----------------------------------
    
    saved_cluster = config_ai.get('ai_n_clusters', 3)
    n_clusters = st.slider("Jumlah Zona Prioritas (Klaster)", min_value=2, max_value=4, value=saved_cluster)
    
    if n_clusters != config_ai.get('ai_n_clusters'):
        config_ai['ai_n_clusters'] = n_clusters
        simpan_config_kmeans(config_ai)
        
    saved_sensitivity = config_ai.get('ai_sensitivity', 1.0)
    sensitivitas = st.slider(
        "Ketegasan Batas Zona (Sensitivity)", 
        min_value=1.0, max_value=3.0, value=float(saved_sensitivity), step=0.5,
        help="1.0 = Normal. Semakin tinggi nilainya, semakin sulit sebuah kecamatan masuk ke Zona 3 & 4."
    )
    
    if sensitivitas != config_ai.get('ai_sensitivity'):
        config_ai['ai_sensitivity'] = sensitivitas
        simpan_config_kmeans(config_ai)
    
    bobot_indikator = config_ai.get('ai_weights', {})
    bobot_baru = {}
    
    if fitur_terpilih:
        with st.expander("⚖️ Atur Bobot (Weighting) per Indikator", expanded=False):
            st.caption("0.0 = Diabaikan | 1.0 = Normal | 10.0 = Sangat Dominan")
            for fitur in fitur_terpilih:
                nilai_awal = bobot_indikator.get(fitur, 1.0)
                label_singkat = f"{fitur[:35]}..." if len(fitur) > 35 else fitur
                
                bobot_baru[fitur] = st.slider(
                    label_singkat, 
                    min_value=0.0, max_value=10.0, value=float(nilai_awal), step=0.1,
                    key=f"weight_{fitur}",
                    help=f"Nama Penuh: {fitur}"
                )
                
        if bobot_baru != bobot_indikator:
            config_ai['ai_weights'] = bobot_baru
            simpan_config_kmeans(config_ai)

    # --- TOMBOL EKSEKUSI ---
    st.write("")
    col_run, col_reset = st.columns([5, 3])
    
    if col_reset.button("🔄 Reset Default", help="Kembalikan semua slider ke angka standar (1.0)"):
        simpan_config_kmeans({}) 
        # Hapus state agar indikator kembali penuh saat di-reset
        if 'ms_fitur_ai' in st.session_state:
            del st.session_state['ms_fitur_ai']
        if 'hasil_kmeans' in st.session_state:
            del st.session_state['hasil_kmeans']
        st.rerun()

    if col_run.button("🚀 Jalankan AI K-Means", type="primary") or 'hasil_kmeans' not in st.session_state:
        if len(fitur_terpilih) >= 1:
            df_hasil_ai, error_msg = proses_kmeans(df_untuk_ai, df_master, fitur_terpilih, n_clusters, bobot_baru, sensitivitas)
            
            if error_msg:
                st.error(error_msg)
            else:
                st.session_state.hasil_kmeans = df_hasil_ai
                
    return fitur_terpilih