# views/tab1_input/table_data_view.py
import streamlit as st
import pandas as pd
import copy
from utils.constants import DAFTAR_KECAMATAN
from utils.state_manager import simpan_data
from utils.styling import beri_warna_tabel

def render_data_view(i, tabel, kolom_tampil):
    """Menyusun dan merender Dataframe ke dalam tabel interaktif."""
    tabel_id = tabel['id']
    is_active = tabel.get('is_active', True)
    kolom_numerik = tabel['kolom_numerik']
    kolom_mati = tabel.get('kolom_mati', [])
    hapus_jumlah = tabel.get('hapus_jumlah', False) 
    kolom_aktif = [c for c in kolom_numerik if c not in kolom_mati]
    
    df = pd.DataFrame(tabel['data'])
    
    # Validasi dan kalibrasi index urutan kecamatan
    if list(df['Kecamatan']) != DAFTAR_KECAMATAN:
        df = df.set_index('Kecamatan').reindex(DAFTAR_KECAMATAN).reset_index()
        st.session_state.koleksi_tabel[i]['data'] = df.to_dict(orient='list')
        simpan_data(st.session_state.koleksi_tabel)
        tabel['data'] = st.session_state.koleksi_tabel[i]['data'] 
    
    # Menghitung subtotal
    if len(kolom_numerik) > 0:
        disabled_cols = ["Kecamatan"]
        edit_cols = ["Kecamatan"] + kolom_numerik
        if not hapus_jumlah:
            if len(kolom_aktif) > 0:
                df['Jumlah'] = df[kolom_aktif].sum(axis=1)
            else:
                df['Jumlah'] = 0
            disabled_cols.append("Jumlah")
    else:
        disabled_cols = ["Kecamatan"]
        edit_cols = ["Kecamatan", "Jumlah"] if not hapus_jumlah else ["Kecamatan"]
        
    active_col = tabel.get('active_sort_col', 'Jumlah')
    render_cols = ["Kecamatan"] + kolom_tampil
    df_view = df[render_cols].sort_values(by=active_col, ascending=not tabel['panah_bawah']).reset_index(drop=True)
    
    # --- RENDER TABEL (HIDUP vs MATI) ---
    if is_active:
        df_berwarna = beri_warna_tabel(df_view, tabel['warna'], tabel['panah_bawah'], target_col=active_col)
        
        # Menerapkan efek redup untuk kolom yang mati
        if kolom_mati:
            def style_kolom_mati(row):
                return ['background-color: rgba(128, 128, 128, 0.05); color: #6c757d;' if col in kolom_mati else '' for col in df_view.columns]
            df_berwarna = df_berwarna.apply(style_kolom_mati, axis=1)

        col_config = {
            "Kecamatan": st.column_config.TextColumn("Kecamatan")
        }
        for c in render_cols:
            if c in kolom_mati:
                col_config[c] = st.column_config.NumberColumn(f"{c} (Mati)", disabled=True)
                
        disabled_cols.extend(kolom_mati) 
        
        edited_df = st.data_editor(
            df_berwarna, 
            use_container_width=True, 
            hide_index=True, 
            disabled=disabled_cols, 
            key=f"editor_{tabel_id}", 
            column_config=col_config
        )
        
        # Menyimpan jika ada sel yang diketik/diedit pengguna
        df_kembali_standar = edited_df[edit_cols].set_index('Kecamatan').reindex(DAFTAR_KECAMATAN).reset_index()
        data_baru = df_kembali_standar.to_dict(orient='list')
        
        if data_baru != tabel['data']:
            st.session_state.koleksi_tabel[i]['data'] = data_baru
            if 'history' in st.session_state.koleksi_tabel[i] and st.session_state.koleksi_tabel[i]['history_index'] >= 0:
                idx_hist = st.session_state.koleksi_tabel[i]['history_index']
                st.session_state.koleksi_tabel[i]['history'][idx_hist]['data'] = copy.deepcopy(data_baru)
            simpan_data(st.session_state.koleksi_tabel) 
            st.session_state.pop('hasil_kmeans', None)
            st.rerun()
    else:
        def style_inactive(row):
            return ['background-color: rgba(128, 128, 128, 0.05); color: #6c757d;' for _ in row]
        
        df_mati = df_view.style.apply(style_inactive, axis=1)
        st.dataframe(df_mati, use_container_width=True, hide_index=True)

    st.write("")