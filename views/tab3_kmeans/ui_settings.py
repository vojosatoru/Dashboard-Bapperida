# views/tab3_kmeans/ui_settings.py
import streamlit as st
import streamlit.components.v1 as components
from utils.state_manager import muat_config_kmeans, simpan_config_kmeans
from views.tab3_kmeans.ai_core import proses_kmeans

def render_pengaturan_ai(df_untuk_ai, df_master, fitur_tersedia):
    """Merender panel pengaturan AI di kolom kiri dan menjalankan algoritma."""
    st.markdown("#### ⚙️ Pengaturan AI")
    
    config_ai = muat_config_kmeans()
    
    # --- DEFAULT MULTISELECT HANYA KOLOM ACUAN ---
    # Membaca Tab 1 untuk mendapatkan daftar kolom yang sedang dijadikan acuan
    default_acuan_features = []
    if 'koleksi_tabel' in st.session_state:
        for tabel in st.session_state.koleksi_tabel:
            col_acuan = tabel.get('active_sort_col', '')
            judul = tabel.get('judul', '')
            
            # Menambahkan Suffix agar cocok dengan nama fitur yang telah dinormalisasi di data_prep
            norm = tabel.get('normalisasi', 'Absolut')
            if norm == "Dibagi Penduduk":
                suffix = " [Dibagi Penduduk]"
            elif norm == "Dibagi Luas Area":
                suffix = " [Dibagi Luas]"
            elif norm == "Dibagi Keduanya":
                suffix = " [Dibagi Keduanya]"
            else:
                suffix = ""
                
            prefix = f"{col_acuan} ({judul}){suffix}"
            
            # Mencari fitur yang cocok di daftar fitur_tersedia
            for f in fitur_tersedia:
                if f == prefix or f.startswith(f"{col_acuan} ({judul})"):
                    default_acuan_features.append(f)
                    break

    # Saring history memori agar tidak error jika ada data yang dihapus di Tab 1
    saved_features = config_ai.get('ai_selected_features', None)
    
    if saved_features is not None:
        valid_features = [f for f in saved_features if f in fitur_tersedia]
        # Jika setelah disaring ternyata kosong (misal tabel dihapus semua), kembali ke default
        if not valid_features and default_acuan_features:
            valid_features = default_acuan_features
    else:
        # Jika belum ada pengaturan (pertama kali buka tab 3), gunakan default acuan
        valid_features = default_acuan_features
        
    # Fallback terakhir jika somehow tabel tidak memiliki acuan tapi fitur tersedia
    if not valid_features and fitur_tersedia:
        valid_features = fitur_tersedia

    # Inisialisasi memori internal Streamlit (Hanya berjalan sekali saat awal)
    if 'ms_fitur_ai' not in st.session_state:
        st.session_state['ms_fitur_ai'] = valid_features
    else:
        # Sanitasi memastikan pilihan lama yang sudah dihapus tidak nyangkut
        st.session_state['ms_fitur_ai'] = [f for f in st.session_state['ms_fitur_ai'] if f in fitur_tersedia]

    # Fungsi seketika (Callback) saat user mengklik Multiselect
    def update_fitur_config():
        config_ai['ai_selected_features'] = st.session_state['ms_fitur_ai']
        simpan_config_kmeans(config_ai)
        # Menghapus peta saat indikator diganti agar memaksakan update
        if 'hasil_kmeans' in st.session_state:
            del st.session_state['hasil_kmeans']

    # --- PENGGUNAAN FITUR SEARCH NATIVE DARI STREAMLIT ---
    # Multiselect Streamlit otomatis memiliki fitur pencarian saat diklik dan diketik.
    fitur_terpilih = st.multiselect(
        "Pilih Indikator yang Dianalisis:", 
        fitur_tersedia, 
        key='ms_fitur_ai',
        on_change=update_fitur_config,
        placeholder="Klik dan ketik untuk mencari indikator..."
    )
    
    # --- MENCEGAH BACKSPACE MENGHAPUS INDIKATOR (PERBAIKAN OBSERVER) ---
    components.html(
        """
        <script>
        function cegahBackspace() {
            const doc = window.parent.document;
            const inputs = doc.querySelectorAll('[data-baseweb="select"] input');
            inputs.forEach(input => {
                if (!input.dataset.kebalBackspace) {
                    input.addEventListener('keydown', function(e) {
                        if (e.key === 'Backspace' && this.value === '') {
                            e.stopPropagation();
                        }
                    }, true); 
                    input.dataset.kebalBackspace = 'true';
                }
            });
        }
        
        cegahBackspace();
        const observer = new MutationObserver(() => {
            cegahBackspace();
        });
        observer.observe(window.parent.document.body, { childList: true, subtree: true });
        </script>
        """,
        height=0,
        width=0
    )
    
    saved_cluster = config_ai.get('ai_n_clusters', 3)
    n_clusters = st.slider("Jumlah Zona Prioritas (Klaster)", min_value=2, max_value=4, value=saved_cluster)
    
    # Tambahkan st.rerun() agar slider tidak mantul (bouncing)
    if n_clusters != saved_cluster:
        config_ai['ai_n_clusters'] = n_clusters
        simpan_config_kmeans(config_ai)
        if 'hasil_kmeans' in st.session_state:
            del st.session_state['hasil_kmeans']
        st.rerun()
        
    saved_sensitivity = config_ai.get('ai_sensitivity', 1.0)
    sensitivitas = st.slider(
        "Ketegasan Batas Zona (Sensitivity)", 
        min_value=1.0, max_value=3.0, value=float(saved_sensitivity), step=0.5,
        help="1.0 = Normal. Semakin tinggi nilainya, semakin sulit sebuah kecamatan masuk ke Zona 3 & 4."
    )
    
    if sensitivitas != saved_sensitivity:
        config_ai['ai_sensitivity'] = sensitivitas
        simpan_config_kmeans(config_ai)
        if 'hasil_kmeans' in st.session_state:
            del st.session_state['hasil_kmeans']
        st.rerun()
    
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
            if 'hasil_kmeans' in st.session_state:
                del st.session_state['hasil_kmeans']
            st.rerun()

    # --- TOMBOL EKSEKUSI ---
    st.write("")
    col_run, col_reset = st.columns([5, 3])
    
    if col_reset.button("🔄 Reset Default", help="Kembalikan semua pengaturan ke standar awal"):
        simpan_config_kmeans({}) 
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