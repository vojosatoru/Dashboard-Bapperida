# views/tab1_input/form_add_col.py
import streamlit as st
import copy
from utils.constants import DAFTAR_KECAMATAN
from utils.state_manager import init_history, simpan_data

def render_step_3(tabel_id, tabel):
    with st.container(border=True):
        butuh_dua_kolom = len(tabel['kolom_numerik']) == 0
        
        if butuh_dua_kolom:
            st.info(f"➕ Menambahkan indikator baru untuk tabel: **{tabel['judul']}**\n\n*Karena tabel ini sebelumnya adalah data tunggal (hanya memiliki 1 nilai/kolom Jumlah), Anda diwajibkan untuk menambahkan minimal 2 indikator yang akan dijumlahkan ulang secara otomatis.*")
            
            col_nama1, col_nama2 = st.columns(2)
            nama_kolom_1 = col_nama1.text_input("Judul Kolom Baru 1", key=f"new_col_name_1_{tabel_id}")
            nama_kolom_2 = col_nama2.text_input("Judul Kolom Baru 2", key=f"new_col_name_2_{tabel_id}")
            
            st.markdown("#### Nilai Kolom 1")
            grid_input_1 = st.columns(3)
            col_data_1 = []
            for k_idx, kec in enumerate(DAFTAR_KECAMATAN):
                val = grid_input_1[k_idx % 3].number_input(kec, value=st.session_state.get('angka_acak_kolom_baru', {}).get(kec, 0), step=1, key=f"new_val_1_{kec}_{tabel_id}")
                col_data_1.append(val)
                
            st.markdown("#### Nilai Kolom 2")
            grid_input_2 = st.columns(3)
            col_data_2 = []
            for k_idx, kec in enumerate(DAFTAR_KECAMATAN):
                val = grid_input_2[k_idx % 3].number_input(kec, value=st.session_state.get('angka_acak_kolom_baru_2', {}).get(kec, 0), step=1, key=f"new_val_2_{kec}_{tabel_id}")
                col_data_2.append(val)
                
        else:
            st.info(f"➕ Menambahkan indikator baru untuk tabel: **{tabel['judul']}**")
            nama_kolom = st.text_input("Judul Kolom Baru (misal: Anggaran Terealisasi)", key=f"new_col_name_{tabel_id}")
            
            grid_input = st.columns(3)
            col_data = []
            for k_idx, kec in enumerate(DAFTAR_KECAMATAN):
                nilai_def = st.session_state.get('angka_acak_kolom_baru', {}).get(kec, 0)
                val = grid_input[k_idx % 3].number_input(kec, value=nilai_def, step=1, key=f"new_val_{kec}_{tabel_id}")
                col_data.append(val)
            
        st.markdown("<br>", unsafe_allow_html=True)
        col_save_new, col_cancel_new = st.columns([1, 4])
        
        if col_save_new.button("💾 Simpan Kolom", type="primary", key=f"save_new_col_{tabel_id}"):
            if butuh_dua_kolom:
                if not nama_kolom_1.strip() or not nama_kolom_2.strip():
                    st.warning("Kedua judul kolom tidak boleh kosong!")
                elif nama_kolom_1.strip().lower() == nama_kolom_2.strip().lower():
                    st.warning("Kedua judul kolom tidak boleh sama!")
                elif nama_kolom_1.strip().lower() == "jumlah" or nama_kolom_2.strip().lower() == "jumlah":
                    st.warning("Judul kolom tidak boleh menggunakan nama 'Jumlah' yang dilindungi sistem!")
                else:
                    init_history(tabel)
                    tabel['history'] = tabel['history'][:tabel['history_index'] + 1]
                    
                    nama_final_1 = nama_kolom_1.strip()
                    nama_final_2 = nama_kolom_2.strip()
                    tabel['kolom_numerik'].extend([nama_final_1, nama_final_2])
                    tabel['data'][nama_final_1] = col_data_1
                    tabel['data'][nama_final_2] = col_data_2
                    
                    tabel['history'].append({
                        'data': copy.deepcopy(tabel['data']),
                        'kolom_numerik': copy.deepcopy(tabel['kolom_numerik']),
                        'hapus_jumlah': tabel.get('hapus_jumlah', False),
                        'active_sort_col': tabel['active_sort_col']
                    })
                    tabel['history_index'] += 1
                    
                    simpan_data(st.session_state.koleksi_tabel)
                    st.session_state.form_step = 0
                    st.session_state.edit_table_id = None
                    st.rerun()
            else:
                if not nama_kolom.strip():
                    st.warning("Judul kolom tidak boleh kosong!")
                elif nama_kolom.strip().lower() in [c.lower() for c in tabel['kolom_numerik']] or nama_kolom.strip().lower() == "jumlah":
                    st.warning("Judul kolom sudah ada atau menggunakan nama 'Jumlah' yang dilindungi sistem!")
                else:
                    init_history(tabel)
                    tabel['history'] = tabel['history'][:tabel['history_index'] + 1]
                    
                    nama_final = nama_kolom.strip()
                    tabel['kolom_numerik'].append(nama_final)
                    tabel['data'][nama_final] = col_data
                    
                    tabel['history'].append({
                        'data': copy.deepcopy(tabel['data']),
                        'kolom_numerik': copy.deepcopy(tabel['kolom_numerik']),
                        'hapus_jumlah': tabel.get('hapus_jumlah', False),
                        'active_sort_col': tabel['active_sort_col']
                    })
                    tabel['history_index'] += 1
                    
                    simpan_data(st.session_state.koleksi_tabel)
                    st.session_state.form_step = 0
                    st.session_state.edit_table_id = None
                    st.rerun()
                
        if col_cancel_new.button("❌ Batal", key=f"cancel_new_col_{tabel_id}"):
            st.session_state.form_step = 0
            st.session_state.edit_table_id = None
            st.rerun()