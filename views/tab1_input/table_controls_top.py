# views/tab1_input/table_controls_top.py
import streamlit as st
import copy
import random
from utils.constants import DAFTAR_KECAMATAN
from utils.state_manager import simpan_data

def render_top_controls(i, tabel):
    """Menampilkan dan menangani aksi pada barisan tombol paling atas."""
    tabel_id = tabel['id']
    is_form_open = st.session_state.form_step == 3
    is_active = tabel.get('is_active', True)
    
    top_col1, top_col_tog, top_col2, top_col_undo, top_col_redo, top_col_add, top_col3 = st.columns([2.9, 1.1, 0.4, 1, 1, 1, 1])
    
    if is_active:
        top_col1.markdown(f"### {tabel['judul']}")
    else:
        top_col1.markdown(f"### <span style='color:#777777;'><s>{tabel['judul']}</s> (Mati)</span>", unsafe_allow_html=True)
    
    new_is_active = top_col_tog.toggle(
        "🟢 Aktif" if is_active else "⚫ Mati", 
        value=is_active, 
        key=f"tog_{tabel_id}", 
        help="Matikan untuk mengecualikan tabel ini dari perhitungan AI dan Peringkat tanpa menghapusnya."
    )
    
    if new_is_active != is_active:
        st.session_state.koleksi_tabel[i]['is_active'] = new_is_active
        simpan_data(st.session_state.koleksi_tabel) 
        st.session_state.pop('hasil_kmeans', None)
        st.rerun()

    warna_baru = top_col2.color_picker("Warna", value=tabel['warna'], key=f"btn_warna_{tabel_id}", label_visibility="collapsed", disabled=(is_form_open or not is_active))
    if warna_baru != tabel['warna']:
        st.session_state.koleksi_tabel[i]['warna'] = warna_baru
        simpan_data(st.session_state.koleksi_tabel) 
        st.rerun()

    can_undo = (tabel['history_index'] > 0) and not is_form_open and is_active
    can_redo = (tabel['history_index'] < len(tabel['history']) - 1) and not is_form_open and is_active
    
    if top_col_undo.button("↩️ Undo", key=f"undo_{tabel_id}", disabled=not can_undo, help="Mundurkan riwayat kolom", use_container_width=True):
        tabel['history_index'] -= 1
        state = tabel['history'][tabel['history_index']]
        tabel['data'] = copy.deepcopy(state['data'])
        tabel['kolom_numerik'] = copy.deepcopy(state['kolom_numerik'])
        tabel['hapus_jumlah'] = state['hapus_jumlah']
        tabel['active_sort_col'] = state['active_sort_col']
        tabel['kolom_mati'] = copy.deepcopy(state.get('kolom_mati', []))
        simpan_data(st.session_state.koleksi_tabel)
        st.session_state.pop('hasil_kmeans', None)
        st.rerun()

    if top_col_redo.button("↪️ Redo", key=f"redo_{tabel_id}", disabled=not can_redo, help="Majukan riwayat kolom", use_container_width=True):
        tabel['history_index'] += 1
        state = tabel['history'][tabel['history_index']]
        tabel['data'] = copy.deepcopy(state['data'])
        tabel['kolom_numerik'] = copy.deepcopy(state['kolom_numerik'])
        tabel['hapus_jumlah'] = state['hapus_jumlah']
        tabel['active_sort_col'] = state['active_sort_col']
        tabel['kolom_mati'] = copy.deepcopy(state.get('kolom_mati', []))
        simpan_data(st.session_state.koleksi_tabel)
        st.session_state.pop('hasil_kmeans', None)
        st.rerun()
        
    if top_col_add.button("➕ Kolom", key=f"add_col_{tabel_id}", help="Tambah indikator baru", use_container_width=True, disabled=(is_form_open or not is_active)):
        st.session_state.form_step = 3
        st.session_state.edit_table_id = tabel_id
        st.session_state.angka_acak_kolom_baru = {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN}
        st.session_state.angka_acak_kolom_baru_2 = {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN}
        st.rerun()
        
    if top_col3.button("❌ Hapus", key=f"btn_hapus_tabel_{tabel_id}", help="Hapus Tabel Total", disabled=is_form_open, use_container_width=True):
        st.session_state.koleksi_tabel.pop(i)
        simpan_data(st.session_state.koleksi_tabel) 
        st.session_state.pop('hasil_kmeans', None)
        st.rerun()