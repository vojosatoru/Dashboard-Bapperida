# views/tab3_kmeans/data_prep.py
import pandas as pd
import streamlit as st
from utils.constants import DAFTAR_KECAMATAN

def siapkan_data_koleksi(koleksi_tabel, data_dasar=None):
    """Menyaring, menormalisasi, dan mempersiapkan raw data menjadi DataFrame untuk AI."""
    df_master = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
    df_untuk_ai = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
    fitur_tersedia = []
    
    map_penduduk = {}
    map_luas = {}
    if data_dasar is not None:
        # --- PERBAIKAN AI K-MEANS: MENGGUNAKAN TAHUN POPULASI AKTIF PILIHAN PENGGUNA ---
        penduduk_cols = sorted([col for col in data_dasar.columns if str(col).startswith("Jumlah Penduduk")])
        
        # Mengecek memori tahun_penduduk_aktif
        if 'tahun_penduduk_aktif' in st.session_state and st.session_state.tahun_penduduk_aktif in data_dasar.columns:
            kolom_acuan = st.session_state.tahun_penduduk_aktif
        elif penduduk_cols:
            kolom_acuan = penduduk_cols[-1] # Fallback: ambil yang paling baru jika belum ada state
        else:
            kolom_acuan = None
            
        if kolom_acuan:
            map_penduduk = dict(zip(data_dasar['Kecamatan'].str.lower(), data_dasar[kolom_acuan]))
        else:
            map_penduduk = {} # Mencegah error jika kolom terhapus
            
        if 'Luas Wilayah (km2)' in data_dasar.columns:
            map_luas = dict(zip(data_dasar['Kecamatan'].str.lower(), data_dasar['Luas Wilayah (km2)']))
    
    for tabel in koleksi_tabel:
        df_tabel = pd.DataFrame(tabel['data'])
        arah_panah_bawah = tabel.get('panah_bawah', False)
        
        jenis_normalisasi = tabel.get('normalisasi', 'Absolut')
        
        if jenis_normalisasi == "Per Kapita (Bagi Penduduk)": jenis_normalisasi = "Dibagi Penduduk"
        elif jenis_normalisasi == "Kepadatan (Bagi Luas Area)": jenis_normalisasi = "Dibagi Luas Area"
        elif jenis_normalisasi == "Rasio Ganda (Bagi Penduduk & Luas Area)": jenis_normalisasi = "Dibagi Keduanya"
        
        if jenis_normalisasi != "Absolut" and data_dasar is None:
            jenis_normalisasi = "Absolut"
            
        kolom_mati = tabel.get('kolom_mati', [])
        kolom_aktif = [c for c in tabel.get('kolom_numerik', []) if c not in kolom_mati]
            
        if len(tabel.get('kolom_numerik', [])) > 0:
            if not tabel.get('hapus_jumlah', False):
                if 'Jumlah' not in df_tabel.columns:
                    df_tabel['Jumlah'] = df_tabel[kolom_aktif].sum(axis=1) if kolom_aktif else 0
                kolom_analisis = kolom_aktif + (["Jumlah"] if "Jumlah" not in kolom_mati else [])
            else:
                kolom_analisis = kolom_aktif
        else:
            kolom_analisis = ["Jumlah"] if "Jumlah" not in kolom_mati else []
        
        for col in kolom_analisis:
            if col not in df_tabel.columns:
                continue
                
            nama_unik = f"{col} ({tabel['judul']})"
            nilai_asli = df_tabel[col].astype(float)
            
            pembagi = None
            is_normalized = False
            
            if jenis_normalisasi == "Dibagi Penduduk":
                pembagi = df_tabel['Kecamatan'].str.lower().map(map_penduduk).fillna(1).replace(0, 1)
                nilai_final = nilai_asli / pembagi
                nama_unik += " [Dibagi Penduduk]"
                is_normalized = True
                
            elif jenis_normalisasi == "Dibagi Luas Area":
                pembagi = df_tabel['Kecamatan'].str.lower().map(map_luas).fillna(1).replace(0, 1)
                nilai_final = nilai_asli / pembagi
                nama_unik += " [Dibagi Luas]"
                is_normalized = True
                
            elif jenis_normalisasi == "Dibagi Keduanya":
                pembagi_pend = df_tabel['Kecamatan'].str.lower().map(map_penduduk).fillna(1).replace(0, 1)
                pembagi_luas = df_tabel['Kecamatan'].str.lower().map(map_luas).fillna(1).replace(0, 1)
                pembagi = pembagi_pend * pembagi_luas
                nilai_final = nilai_asli / pembagi
                nama_unik += " [Dibagi Keduanya]"
                is_normalized = True
                
            else:
                nilai_final = nilai_asli
            
            df_master[nama_unik] = nilai_final
            
            if is_normalized and pembagi is not None:
                nama_human = nama_unik + " (Human Ratio)"
                df_human = pembagi / nilai_asli.replace(0, float('inf'))
                df_human = df_human.replace(0, 0)
                df_master[nama_human] = df_human
            
            if arah_panah_bawah:
                df_untuk_ai[nama_unik] = nilai_final
            else:
                df_untuk_ai[nama_unik] = nilai_final * -1 
                
            fitur_tersedia.append(nama_unik)
            
    return df_master, df_untuk_ai, fitur_tersedia