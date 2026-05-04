# views/tab3_kmeans/data_prep.py
import pandas as pd
from utils.constants import DAFTAR_KECAMATAN

def siapkan_data_koleksi(koleksi_tabel, jenis_normalisasi="Absolut", data_dasar=None):
    """Menyaring, menormalisasi, dan mempersiapkan raw data menjadi DataFrame untuk AI."""
    df_master = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
    df_untuk_ai = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
    fitur_tersedia = []
    
    # Mencegah error jika data dasar belum terisi penuh tapi user memilih normalisasi
    if jenis_normalisasi != "Absolut" and data_dasar is None:
        jenis_normalisasi = "Absolut"
        
    # Membuat dictionary (kamus) untuk mempercepat proses pencocokan wilayah
    if jenis_normalisasi != "Absolut":
        map_penduduk = dict(zip(data_dasar['Kecamatan'].str.lower(), data_dasar['Jumlah Penduduk (Jiwa)']))
        map_luas = dict(zip(data_dasar['Kecamatan'].str.lower(), data_dasar['Luas Wilayah (km2)']))
    
    for tabel in koleksi_tabel:
        df_tabel = pd.DataFrame(tabel['data'])
        arah_panah_bawah = tabel['panah_bawah'] 
        
        if len(tabel['kolom_numerik']) > 0:
            df_tabel['Jumlah'] = df_tabel[tabel['kolom_numerik']].sum(axis=1)
            kolom_analisis = tabel['kolom_numerik'] + ["Jumlah"]
        else:
            kolom_analisis = ["Jumlah"]
        
        for col in kolom_analisis:
            nama_unik = f"{col} ({tabel['judul']})"
            nilai_asli = df_tabel[col].astype(float)
            
            # --- PROSES MATEMATIS NORMALISASI (ANTI SIZE BIAS) ---
            if jenis_normalisasi == "Per Kapita (Bagi Penduduk)":
                pembagi = df_tabel['Kecamatan'].str.lower().map(map_penduduk).fillna(1).replace(0, 1)
                nilai_final = nilai_asli / pembagi
                nama_unik += " [Per Kapita]"
            elif jenis_normalisasi == "Kepadatan (Bagi Luas Area)":
                pembagi = df_tabel['Kecamatan'].str.lower().map(map_luas).fillna(1).replace(0, 1)
                nilai_final = nilai_asli / pembagi
                nama_unik += " [Kepadatan]"
            elif jenis_normalisasi == "Rasio Ganda (Bagi Penduduk & Luas Area)":
                # MENGHITUNG MENGGUNAKAN KEDUA DATA SEKALIGUS
                pembagi_pend = df_tabel['Kecamatan'].str.lower().map(map_penduduk).fillna(1).replace(0, 1)
                pembagi_luas = df_tabel['Kecamatan'].str.lower().map(map_luas).fillna(1).replace(0, 1)
                # Nilai dibagi penduduk, lalu dibagi lagi dengan luas wilayah
                nilai_final = nilai_asli / (pembagi_pend * pembagi_luas)
                nama_unik += " [Rasio Ganda]"
            else:
                # Absolut (Tanpa Normalisasi)
                nilai_final = nilai_asli
            
            # Data yang dimasukkan ke master adalah data yang sudah dinormalisasi
            df_master[nama_unik] = nilai_final
            
            # Logika invers/pembalikan untuk indikator benefit
            if arah_panah_bawah:
                df_untuk_ai[nama_unik] = nilai_final
            else:
                df_untuk_ai[nama_unik] = nilai_final * -1 
                
            fitur_tersedia.append(nama_unik)
            
    return df_master, df_untuk_ai, fitur_tersedia