# Nama file: utils.py
import streamlit as st
import json
import os

# Nama file tempat data akan disimpan secara permanen di komputer Anda
DATA_FILE = "data_bapperida.json"

def muat_data():
    """Memuat data dari file JSON lokal jika ada"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return [] # Jika file rusak, kembalikan list kosong
    return []

def simpan_data(data):
    """Menyimpan data ke file JSON lokal secara otomatis"""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- KOORDINAT & DAFTAR KECAMATAN ---
KECAMATAN_KUDUS_MAP = {
    "Kaliwungu": [-6.8058, 110.8143],
    "Kota": [-6.8048, 110.8405],
    "Jati": [-6.8378, 110.8483],
    "Undaan": [-6.9158, 110.8143],
    "Mejobo": [-6.8288, 110.8844],
    "Jekulo": [-6.7978, 110.9172],
    "Bae": [-6.7828, 110.8544],
    "Gebog": [-6.7328, 110.8355],
    "Dawe": [-6.6978, 110.8922]
}
DAFTAR_KECAMATAN = list(KECAMATAN_KUDUS_MAP.keys())

# --- INISIALISASI SESSION STATE ---
def init_session_state():
    """Fungsi untuk memastikan memori aplikasi selalu siap sedia"""
    if "koleksi_tabel" not in st.session_state: 
        # Modifikasi: Mengisi tabel awal dari file JSON yang tersimpan, bukan list kosong
        st.session_state.koleksi_tabel = muat_data() 
        
    if "form_step" not in st.session_state: st.session_state.form_step = 0
    if "angka_acak_sementara" not in st.session_state: st.session_state.angka_acak_sementara = {}
    if "temp_judul" not in st.session_state: st.session_state.temp_judul = ""
    if "temp_jml_kolom" not in st.session_state: st.session_state.temp_jml_kolom = 1
    if "temp_current_col_idx" not in st.session_state: st.session_state.temp_current_col_idx = 0
    if "temp_data" not in st.session_state: st.session_state.temp_data = {}
    if "temp_kolom_names" not in st.session_state: st.session_state.temp_kolom_names = []

# --- FUNGSI PEWARNAAN ---
def konversi_hex_ke_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def beri_warna_tabel(df, warna_hex, arah_panah_bawah, target_col):
    """Memberikan background transparan HANYA pada kolom Kecamatan berdasarkan target_col"""
    r, g, b = konversi_hex_ke_rgb(warna_hex)
    nilai_min = df[target_col].min()
    nilai_max = df[target_col].max()

    def style_row(row):
        nilai = row[target_col]
        if nilai_max == nilai_min:
            opacity = 0.5 
        else:
            rasio = (nilai - nilai_min) / (nilai_max - nilai_min)
            if not arah_panah_bawah:
                rasio = 1.0 - rasio
            opacity = 0.1 + (rasio * 0.9)

        color_style = f'background-color: rgba({r}, {g}, {b}, {opacity}); font-weight: 600;'
        return [color_style if col == 'Kecamatan' else '' for col in df.columns]

    return df.style.apply(style_row, axis=1)