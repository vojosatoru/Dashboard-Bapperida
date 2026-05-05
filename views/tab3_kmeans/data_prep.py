# views/tab3_kmeans/data_prep.py
import pandas as pd
from utils.constants import DAFTAR_KECAMATAN

def siapkan_data_koleksi(koleksi_tabel, data_dasar=None):
    """Menyaring, menormalisasi, dan mempersiapkan raw data menjadi DataFrame untuk AI."""
    df_master = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
    df_untuk_ai = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
    fitur_tersedia = []
    
    # Membuat dictionary (kamus) untuk mempercepat proses pencocokan wilayah
    map_penduduk = {}
    map_luas = {}
    if data_dasar is not None:
        map_penduduk = dict(zip(data_dasar['Kecamatan'].str.lower(), data_dasar['Jumlah Penduduk (Jiwa)']))
        map_luas = dict(zip(data_dasar['Kecamatan'].str.lower(), data_dasar['Luas Wilayah (km2)']))
    
    for tabel in koleksi_tabel:
        df_tabel = pd.DataFrame(tabel['data'])
        arah_panah_bawah = tabel.get('panah_bawah', False)
        
        jenis_normalisasi = tabel.get('normalisasi', 'Absolut')
        
        # Penyesuaian nama legacy
        if jenis_normalisasi == "Bagi Penduduk": jenis_normalisasi = "Dibagi Penduduk"
        elif jenis_normalisasi == "Bagi Luas Area": jenis_normalisasi = "Dibagi Luas Area"
        elif jenis_normalisasi == "Bagi Penduduk & Luas Area": jenis_normalisasi = "Dibagi Keduanya"
        
        if jenis_normalisasi != "Absolut" and data_dasar is None:
            jenis_normalisasi = "Absolut"
            
        if len(tabel.get('kolom_numerik', [])) > 0:
            if not tabel.get('hapus_jumlah', False):
                if 'Jumlah' not in df_tabel.columns:
                    df_tabel['Jumlah'] = df_tabel[tabel['kolom_numerik']].sum(axis=1)
                kolom_analisis = tabel['kolom_numerik'] + ["Jumlah"]
            else:
                kolom_analisis = tabel['kolom_numerik']
        else:
            kolom_analisis = ["Jumlah"]
        
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
            
            # --- FITUR BARU: MENYIMPAN NILAI "RASIO MANUSIA" SECARA TERSEMBUNYI ---
            # Jika dinormalisasi, kita simpan juga kebalikan angkanya di df_master (namun AI tidak menggunakannya)
            if is_normalized and pembagi is not None:
                nama_human = nama_unik + " (Human Ratio)"
                
                # Mencegah division by zero
                # Jika nilai asli 0, rasionya kita anggap 0 (misal: 0 sekolah untuk x penduduk)
                df_human = pembagi / nilai_asli.replace(0, float('inf'))
                df_human = df_human.replace(0, 0) # Membersihkan inf
                
                df_master[nama_human] = df_human
            
            # Logika invers/pembalikan untuk indikator benefit
            if arah_panah_bawah:
                df_untuk_ai[nama_unik] = nilai_final
            else:
                df_untuk_ai[nama_unik] = nilai_final * -1 
                
            fitur_tersedia.append(nama_unik)
            
    return df_master, df_untuk_ai, fitur_tersedia