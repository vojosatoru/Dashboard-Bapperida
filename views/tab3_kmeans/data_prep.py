# views/tab3_kmeans/data_prep.py
import pandas as pd
from utils.constants import DAFTAR_KECAMATAN

def siapkan_data_koleksi(koleksi_tabel):
    """Menyaring dan mempersiapkan raw data menjadi DataFrame untuk AI."""
    df_master = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
    df_untuk_ai = pd.DataFrame({"Kecamatan": DAFTAR_KECAMATAN})
    fitur_tersedia = []
    
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
            df_master[nama_unik] = df_tabel[col]
            
            # Logika invers/pembalikan untuk indikator benefit
            if arah_panah_bawah:
                df_untuk_ai[nama_unik] = df_tabel[col]
            else:
                df_untuk_ai[nama_unik] = df_tabel[col] * -1 
                
            fitur_tersedia.append(nama_unik)
            
    return df_master, df_untuk_ai, fitur_tersedia