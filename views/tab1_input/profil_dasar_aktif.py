# views/tab1_input/profil_dasar_aktif.py
import streamlit as st
import pandas as pd

def format_indo_desimal(val):
    """Mengubah titik desimal menjadi koma ala Indonesia untuk Luas Wilayah."""
    try:
        if pd.isna(val): return "0"
        val_float = float(val)
        if val_float.is_integer():
            return str(int(val_float))
        return str(val_float).replace('.', ',')
    except:
        return val

def format_indo_ribuan(val):
    """Menambahkan pemisah titik setiap 3 digit angka (ribuan) untuk Jumlah Penduduk."""
    try:
        if pd.isna(val): return "0"
        return f"{int(float(val)):,}".replace(',', '.')
    except:
        return val

def highlight_aktif(s, col_aktif):
    """Fungsi styling pandas untuk memberi warna hijau transparan pada kolom yang aktif"""
    return ['background-color: rgba(46, 204, 113, 0.15);'] * len(s) if s.name == col_aktif else [''] * len(s)

def render_tab_aktif():
    with st.container(border=True):
        df_dasar = st.session_state.data_dasar
        
        # --- TATA LETAK ATAS BAWAH ---
        st.markdown("**🗺️ Luas Wilayah (km²)**")
        df_luas = df_dasar[['Kecamatan', 'Luas Wilayah (km2)']]
        
        df_luas_styled = df_luas.style.format({"Luas Wilayah (km2)": format_indo_desimal})\
                                      .apply(highlight_aktif, col_aktif="Luas Wilayah (km2)", axis=0)
        
        st.dataframe(
            df_luas_styled, 
            use_container_width=True, 
            hide_index=True,
            column_config={"Luas Wilayah (km2)": "🟢 Luas Wilayah (km²)"}
        )
        
        st.write("") # Spasi pemisah
        
        st.markdown("**👥 Jumlah Penduduk (Berdasarkan Tahun)**")
        st.caption("Pilih tahun acuan di bawah ini untuk menentukan data populasi mana yang akan digunakan sebagai rasio pembagi (Normalisasi) pada mesin AI K-Means.")
        
        penduduk_cols = [col for col in df_dasar.columns if str(col).startswith("Jumlah Penduduk")]
        penduduk_cols = sorted(penduduk_cols)
        
        if penduduk_cols:
            if 'tahun_penduduk_aktif' not in st.session_state or st.session_state.tahun_penduduk_aktif not in penduduk_cols:
                st.session_state.tahun_penduduk_aktif = penduduk_cols[-1]

            def ubah_tahun_aktif():
                st.session_state.tahun_penduduk_aktif = st.session_state.radio_tahun_ui
                st.session_state.pop('hasil_kmeans', None)

            st.radio(
                "📅 Tahun Kependudukan Aktif:",
                options=penduduk_cols,
                index=penduduk_cols.index(st.session_state.tahun_penduduk_aktif),
                horizontal=True,
                key="radio_tahun_ui",
                on_change=ubah_tahun_aktif,
                format_func=lambda x: str(x).replace("Jumlah Penduduk ", "")
            )
        
        df_penduduk = df_dasar[['Kecamatan'] + penduduk_cols]
        
        formatter_penduduk = {col: format_indo_ribuan for col in penduduk_cols}
        tahun_aktif = st.session_state.get('tahun_penduduk_aktif', '')
        
        df_penduduk_styled = df_penduduk.style.format(formatter_penduduk)\
                                        .apply(highlight_aktif, col_aktif=tahun_aktif, axis=0)
        
        config_penduduk = {
            tahun_aktif: f"🟢 {tahun_aktif}"
        } if tahun_aktif else {}

        st.dataframe(
            df_penduduk_styled, 
            use_container_width=True, 
            hide_index=True,
            column_config=config_penduduk
        )