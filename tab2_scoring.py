# Nama file: tab2_scoring.py
import streamlit as st
import pandas as pd
from utils import DAFTAR_KECAMATAN

def render_tab2():
    st.subheader("🏆 Peringkat Akumulasi Prioritas Kecamatan")
    st.markdown("Skor ini dihitung **berdasarkan Kolom Acuan (yang bertombol merah)** pada masing-masing tabel di Tab 1. Kecamatan di posisi ke-1 pada suatu tabel mendapat 9 poin, ke-2 mendapat 8 poin, dst.")
    
    if not st.session_state.koleksi_tabel:
        st.info("Tambahkan minimal 1 tabel di 'Tab 1' untuk melihat perhitungan akumulasi poin.")
    else:
        # Menyiapkan kerangka data
        rekap_data = [{"Kecamatan": kec, "Total Poin": 0} for kec in DAFTAR_KECAMATAN]
        df_rekap = pd.DataFrame(rekap_data).set_index("Kecamatan")
        
        # Menghitung poin dari SETIAP TABEL (hanya berpatokan pada kolom aktif)
        for tabel in st.session_state.koleksi_tabel:
            judul, active_col, kolom_numerik = tabel['judul'], tabel['active_sort_col'], tabel['kolom_numerik']
            
            df_temp_full = pd.DataFrame(tabel['data'])
            df_temp_full['Jumlah'] = df_temp_full[kolom_numerik].sum(axis=1)
            df_temp = df_temp_full[['Kecamatan', active_col]]
            
            df_temp = df_temp.sort_values(by=active_col, ascending=not tabel['panah_bawah']).reset_index(drop=True)
            df_temp['Posisi'] = range(1, len(DAFTAR_KECAMATAN) + 1)
            df_temp['Poin'] = range(len(DAFTAR_KECAMATAN), 0, -1)
            
            nama_kolom_posisi = f"Pos: {judul} ({active_col})"
            
            for _, row in df_temp.iterrows():
                df_rekap.at[row['Kecamatan'], nama_kolom_posisi] = row['Posisi']
                df_rekap.at[row['Kecamatan'], "Total Poin"] += row['Poin']
                
        df_rekap = df_rekap.reset_index().sort_values(by="Total Poin", ascending=False).reset_index(drop=True)
        kolom_posisi = [col for col in df_rekap.columns if col.startswith("Pos:")]
        
        for col in kolom_posisi:
            df_rekap[col] = df_rekap[col].fillna(0).astype(int)
            
        df_rekap = df_rekap[["Kecamatan"] + kolom_posisi + ["Total Poin"]]
        st.dataframe(df_rekap.style.background_gradient(subset=["Total Poin"], cmap="Blues"), use_container_width=True, hide_index=True)