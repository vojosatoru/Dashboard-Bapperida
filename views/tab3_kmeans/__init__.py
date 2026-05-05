# views/tab3_kmeans/__init__.py
import streamlit as st
from utils.state_manager import muat_config_kmeans

# Mengimpor sub-modul yang telah dipisah
from views.tab3_kmeans.data_prep import siapkan_data_koleksi
from views.tab3_kmeans.ui_settings import render_pengaturan_ai
from views.tab3_kmeans.ui_results import render_peta_zonasi, render_tabel_zonasi

def render_tab3():
    st.subheader("🤖 Peta Zonasi AI (K-Means Clustering)")
    st.markdown("AI membaca indikator yang dipilih dan **menyelaraskan nilainya secara otomatis** berdasarkan metode normalisasi pada masing-masing tabel, lalu mengelompokkan kecamatan ke dalam zona prioritas menggunakan Machine Learning.")
    
    # --- Menyaring Hanya Tabel yang Aktif ---
    tabel_aktif = [t for t in st.session_state.get('koleksi_tabel', []) if t.get('is_active', True)]
    
    # Validasi Keberadaan Data
    if not tabel_aktif:
        if not st.session_state.get('koleksi_tabel'):
            st.warning("⚠️ Tambahkan data di Tab 1 terlebih dahulu agar AI bisa mulai belajar (Training).")
        else:
            st.warning("⚠️ Semua tabel saat ini berstatus 'Mati/Nonaktif'. Silakan aktifkan minimal 1 tabel di Tab 1 agar AI dapat bekerja.")
        return
        
    # --- MENGAMBIL PROFIL DASAR ---
    data_dasar = st.session_state.get('data_dasar', None)
        
    # 1. Tahap Persiapan Data (Terintegrasi dengan Normalisasi per Tabel)
    # Kita HANYA mengirimkan "tabel_aktif" ke dalam mesin persiapan data
    df_master, df_untuk_ai, fitur_tersedia = siapkan_data_koleksi(
        tabel_aktif,
        data_dasar=data_dasar
    )
    
    if len(fitur_tersedia) < 1:
        st.info("⚠️ AI K-Means membutuhkan minimal 1 indikator (kolom) untuk bisa mengelompokkan wilayah.")
        return

    # 2. Tahap Tata Letak UI (Dua Kolom)
    col_ai1, col_ai2 = st.columns([1, 2])
    
    with col_ai1:
        # Menampilkan Setingan Kiri & Mendapatkan daftar fitur yang dipilih user
        fitur_terpilih = render_pengaturan_ai(df_untuk_ai, df_master, fitur_tersedia)
        
    with col_ai2:
        # Menampilkan Peta WebGIS di Kanan
        render_peta_zonasi(fitur_terpilih)
        
    # 3. Tahap Hasil Akhir
    # Menampilkan Tabel di bagian paling bawah
    render_tabel_zonasi(fitur_terpilih)