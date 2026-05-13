# views/tab1_input/form_manual.py
import streamlit as st
import random
import uuid
from utils.constants import DAFTAR_KECAMATAN
from utils.state_manager import simpan_data

def render_step_0():
    col1, col2, _ = st.columns([2, 2, 6])
    if col1.button("➕ Tambah Data Manual", type="primary", use_container_width=True):
        st.session_state.form_step = 1
        st.session_state.temp_judul = ""
        st.session_state.temp_jml_kolom = 1
        st.session_state.temp_kolom_names = []
        st.rerun()
        
    if col2.button("📁 Auto Import", type="primary", use_container_width=True):
        st.session_state.form_step = 4
        st.session_state.temp_judul_import = "" 
        st.session_state.temp_kolom_names = []
        st.session_state.last_uploaded_filename = None
        st.rerun()

def render_step_1():
    with st.container(border=True):
        st.subheader("Langkah 1: Pengaturan Tabel")
        judul_input = st.text_input("Judul Tabel (misal: Infrastruktur 2024)", value=st.session_state.temp_judul)
        
        val_awal = st.session_state.temp_jml_kolom if st.session_state.temp_jml_kolom >= 1 else 1
        jml_kolom = st.number_input("Berapa jumlah indikator/kolom? (Isi 1 jika data tunggal)", min_value=1, max_value=10, value=val_awal, step=1)
        
        col_btn1, col_btn2 = st.columns([1, 4])
        if col_btn1.button("➡️ Mulai Isi Kolom", type="primary"):
            if judul_input.strip() == "":
                st.warning("Judul tabel tidak boleh kosong!")
            else:
                st.session_state.temp_judul = judul_input
                st.session_state.temp_jml_kolom = jml_kolom
                st.session_state.angka_acak_sementara = {
                    idx: {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN} 
                    for idx in range(jml_kolom)
                }
                st.session_state.temp_kolom_names = []
                st.session_state.form_step = 2
                st.rerun()
        if col_btn2.button("Batal"):
            st.session_state.form_step = 0
            st.rerun()

def render_step_2():
    total_kolom = st.session_state.temp_jml_kolom
    with st.container(border=True):
        st.subheader("Langkah 2: Mengisi Data Indikator")
        st.markdown("Lengkapi seluruh data di bawah ini, lalu klik **Simpan Tabel**.")
        
        all_names = []
        all_data = {}
        
        for idx in range(total_kolom):
            st.markdown(f"#### Kolom {idx + 1}")
            if total_kolom == 1:
                st.info("Judul Kolom: **Jumlah** (Data Tunggal otomatis)")
                nama_kolom = "Jumlah"
            else:
                default_name = st.session_state.get('temp_kolom_names', [])[idx] if idx < len(st.session_state.get('temp_kolom_names', [])) else ""
                nama_kolom = st.text_input(f"Judul Kolom {idx + 1} (misal: Panjang Jalan)", value=default_name, key=f"col_name_input_{idx}")
            
            grid_input = st.columns(3)
            col_data = []
            for i, kec in enumerate(DAFTAR_KECAMATAN):
                nilai_def = st.session_state.angka_acak_sementara.get(idx, {}).get(kec, 0)
                step_val = 1.0 if isinstance(nilai_def, float) else 1
                val = grid_input[i % 3].number_input(kec, value=nilai_def, step=step_val, key=f"val_{idx}_{kec}")
                col_data.append(val)
            
            all_names.append(nama_kolom)
            all_data[idx] = col_data
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        
        col_back, col_save, col_cancel = st.columns([1, 1, 3])
        
        if col_back.button("⬅️ Kembali"):
            if st.session_state.get('temp_kolom_names'):
                st.session_state.form_step = 4
            else:
                st.session_state.form_step = 1 
            st.rerun()
            
        if col_save.button("💾 Simpan Tabel", type="primary"):
            error_msg = None
            if total_kolom > 1:
                names_lower = [n.strip().lower() for n in all_names]
                if "" in names_lower:
                    error_msg = "Semua judul kolom harus diisi!"
                elif len(set(names_lower)) != len(names_lower):
                    error_msg = "Terdapat judul kolom ganda! Gunakan nama berbeda."
                elif "jumlah" in names_lower:
                    error_msg = "Nama 'Jumlah' dilindungi sistem. Pilih nama lain!"
            
            if error_msg:
                st.warning(error_msg)
            else:
                final_data = {"Kecamatan": DAFTAR_KECAMATAN.copy()}
                if total_kolom == 1:
                    final_data["Jumlah"] = all_data[0]
                    kolom_numerik = []
                    active_sort = "Jumlah"
                else:
                    for idx, name in enumerate(all_names):
                        final_data[name] = all_data[idx]
                    kolom_numerik = all_names.copy()
                    active_sort = all_names[0]
                    
                tabel_baru = {
                    "id": str(uuid.uuid4()),
                    "judul": st.session_state.temp_judul,
                    "data": final_data,
                    "kolom_numerik": kolom_numerik,
                    "warna": "#FF4B4B", 
                    "active_sort_col": active_sort,
                    "panah_bawah": True,
                    "hapus_jumlah": False 
                }
                st.session_state.koleksi_tabel.append(tabel_baru)
                simpan_data(st.session_state.koleksi_tabel)
                st.session_state.form_step = 0
                st.rerun()
                
        if col_cancel.button("❌ Batalkan Total"):
            st.session_state.form_step = 0
            st.rerun()