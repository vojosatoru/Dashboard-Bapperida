# views/tab1_input/table_card.py
import streamlit as st
from utils.state_manager import init_history, simpan_data

# Mengimpor modul kecil yang telah dipisah
from views.tab1_input.form_add_col import render_step_3
from views.tab1_input.table_controls_top import render_top_controls
from views.tab1_input.table_controls_mid import render_mid_controls
from views.tab1_input.table_data_view import render_data_view

def render_single_table(i, tabel):
    """Router yang menyusun komponen UI menjadi satu buah tabel utuh."""
    init_history(st.session_state.koleksi_tabel[i])
    tabel = st.session_state.koleksi_tabel[i]
    
    # 1. Tampilkan Kontrol Atas (Judul, Toggle, Undo/Redo, Hapus, dll)
    render_top_controls(i, tabel)
    
    # Perbarui referensi tabel (berjaga-jaga jika state berubah namun belum re-run)
    try:
        tabel = st.session_state.koleksi_tabel[i]
    except IndexError:
        return # Menghentikan eksekusi sisa blok ini jika tabel baru saja dihapus

    tabel_id = tabel['id']
    kolom_numerik = tabel['kolom_numerik']
    hapus_jumlah = tabel.get('hapus_jumlah', False) 
    
    # 2. Tampilkan form tambah kolom jika di-klik (berada di antara tombol dan tabel)
    if st.session_state.form_step == 3 and st.session_state.get('edit_table_id') == tabel_id:
        render_step_3(tabel_id, tabel)

    # 3. Validasi Kolom Tersisa
    kolom_tampil = []
    if len(kolom_numerik) > 0:
        kolom_tampil.extend(kolom_numerik)
        if not hapus_jumlah:
            kolom_tampil.append("Jumlah")
    else:
        if not hapus_jumlah:
            kolom_tampil.append("Jumlah")

    # Jika tabel kosong secara tak sengaja (semua kolom dihapus), bersihkan seluruh tabel
    if not kolom_tampil:
        st.info("Semua kolom telah dihapus. Menghapus tabel secara otomatis...")
        st.session_state.koleksi_tabel.pop(i)
        simpan_data(st.session_state.koleksi_tabel)
        st.session_state.pop('hasil_kmeans', None)
        st.rerun()
        return

    # 4. Tampilkan Menu Pengaturan (Rename, Urutan, Normalisasi, Hapus Kolom)
    render_mid_controls(i, tabel, kolom_tampil)
    
    # Perbarui referensi lagi
    try:
        tabel = st.session_state.koleksi_tabel[i]
    except IndexError:
        return

    # 5. Tampilkan Tabel Data Utama (Editor)
    render_data_view(i, tabel, kolom_tampil)