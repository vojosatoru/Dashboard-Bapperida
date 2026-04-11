# views/tab3_kmeans/__init__.py
import streamlit as st

# Mengimpor sub-modul yang telah dipisah
from views.tab3_kmeans.data_prep import siapkan_data_koleksi
from views.tab3_kmeans.ui_settings import render_pengaturan_ai
from views.tab3_kmeans.ui_results import render_peta_zonasi, render_tabel_zonasi

def render_tab3():
    st.subheader("🤖 Peta Zonasi AI (K-Means Clustering)")
    st.markdown("AI membaca indikator yang dipilih dan **menyelaraskan nilainya secara otomatis**, lalu mengelompokkan kecamatan ke dalam zona prioritas menggunakan Machine Learning.")
    
    # Validasi Keberadaan Data
    if not st.session_state.koleksi_tabel:
        st.warning("⚠️ Tambahkan data di Tab 1 terlebih dahulu agar AI bisa mulai belajar (Training).")
        return
        
    # 1. Tahap Persiapan Data
    df_master, df_untuk_ai, fitur_tersedia = siapkan_data_koleksi(st.session_state.koleksi_tabel)
    
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