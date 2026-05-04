# utils/state_manager.py
import streamlit as st
import json
import os
import copy
import pandas as pd
from utils.constants import DAFTAR_KECAMATAN

# Pindahkan file database ke dalam folder 'data' agar direktori root tetap bersih
DATA_DIR = "data"

def get_data_file():
    # Mengambil kunci proyek dari memori, jika kosong gunakan 'publik'
    key = st.session_state.get('project_key', 'publik')
    return os.path.join(DATA_DIR, f"data_{key}.json")

def get_config_file():
    key = st.session_state.get('project_key', 'publik')
    return os.path.join(DATA_DIR, f"config_{key}.json")

def get_profil_file():
    # File profil dasar statis, tidak terpengaruh oleh project_key
    return os.path.join(DATA_DIR, "profil_dasar.json")

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

def muat_profil_dasar():
    file_path = get_profil_file()
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                # Kembalikan DataFrame dan sumber
                return pd.DataFrame(data['data']), data.get('sumber', 'Custom File')
        except:
            pass # Jika gagal, kembalikan default di bawah
            
    # Data Aproksimasi Kabupaten Kudus 2025/2026 (DEFAULT)
    data_luas = [32.71, 10.47, 26.30, 71.77, 36.77, 82.92, 23.33, 55.01, 85.84]
    data_penduduk = [105.2, 91.5, 112.8, 80.4, 78.1, 110.3, 73.6, 100.2, 108.5]
    
    df_default = pd.DataFrame({
        "Kecamatan": DAFTAR_KECAMATAN,
        "Luas Wilayah (km2)": data_luas,
        "Jumlah Penduduk (Jiwa)": [x * 1000 for x in data_penduduk]
    })
    return df_default, "Data Statis BPS Kudus 2025/2026"

def simpan_profil_dasar(df, sumber):
    pastikan_folder_ada()
    data_to_save = {
        'data': df.to_dict(orient='list'),
        'sumber': sumber
    }
    with open(get_profil_file(), "w") as f:
        json.dump(data_to_save, f, indent=4)
        
def reset_profil_dasar():
    file_path = get_profil_file()
    if os.path.exists(file_path):
        os.remove(file_path)

# --- INISIALISASI SESSION STATE & HISTORY UNDO/REDO ---
def init_session_state():
    if "koleksi_tabel" not in st.session_state: 
        st.session_state.koleksi_tabel = muat_data() 
        
    if "data_dasar" not in st.session_state:
        df_profil, sumber_profil = muat_profil_dasar()
        st.session_state.data_dasar = df_profil
        st.session_state.sumber_profil = sumber_profil
        
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