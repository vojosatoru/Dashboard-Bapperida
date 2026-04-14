# utils/state_manager.py
import streamlit as st
import json
import os
import copy

# Pindahkan file database ke dalam folder 'data' agar direktori root tetap bersih
DATA_DIR = "data"

def get_data_file():
    # Mengambil kunci proyek dari memori, jika kosong gunakan 'publik'
    key = st.session_state.get('project_key', 'publik')
    return os.path.join(DATA_DIR, f"data_{key}.json")

def get_config_file():
    key = st.session_state.get('project_key', 'publik')
    return os.path.join(DATA_DIR, f"config_{key}.json")

def pastikan_folder_ada():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

# --- FUNGSI MANAJEMEN DATA JSON ---
def muat_data():
    file_path = get_data_file()
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def simpan_data(data):
    pastikan_folder_ada()
    with open(get_data_file(), "w") as f:
        json.dump(data, f, indent=4)

def muat_config_kmeans():
    file_path = get_config_file()
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def simpan_config_kmeans(data):
    pastikan_folder_ada()
    with open(get_config_file(), "w") as f:
        json.dump(data, f, indent=4)

# --- INISIALISASI SESSION STATE & HISTORY UNDO/REDO ---
def init_session_state():
    if "koleksi_tabel" not in st.session_state: 
        st.session_state.koleksi_tabel = muat_data() 
        
    if "form_step" not in st.session_state: st.session_state.form_step = 0
    if "angka_acak_sementara" not in st.session_state: st.session_state.angka_acak_sementara = {}
    if "temp_judul" not in st.session_state: st.session_state.temp_judul = ""
    if "temp_jml_kolom" not in st.session_state: st.session_state.temp_jml_kolom = 1
    if "temp_kolom_names" not in st.session_state: st.session_state.temp_kolom_names = []

def init_history(tabel):
    if 'history' not in tabel:
        tabel['history'] = [{
            'data': copy.deepcopy(tabel['data']),
            'kolom_numerik': copy.deepcopy(tabel['kolom_numerik']),
            'hapus_jumlah': tabel.get('hapus_jumlah', False),
            'active_sort_col': tabel['active_sort_col']
        }]
        tabel['history_index'] = 0