# views/tab1_input/profil_dasar_import.py
import streamlit as st
import pandas as pd
from utils.constants import DAFTAR_KECAMATAN
from utils.state_manager import simpan_profil_dasar

def render_tab_import():
    with st.container(border=True):
        if st.session_state.get('import_profil_sukses', False):
            st.success("✅ File berhasil diimpor! Silakan cek tab '🟢 Profil Aktif' untuk melihat hasilnya.")
            st.session_state.import_profil_sukses = False

        st.markdown("Karena BPS biasanya memisah data Luas dan Penduduk dalam file berbeda, silakan pilih dan perbarui datanya satu per satu.")
        
        jenis_pembaruan_ui = st.radio(
            "Pilih jenis data yang ingin diperbarui:",
            ["Luas Wilayah (km²)", "Jumlah Penduduk (Jiwa)"],
            horizontal=True
        )
        
        tahun_penduduk = None
        if "Penduduk" in jenis_pembaruan_ui:
            st.write("")
            tahun_penduduk = st.number_input(
                "📅 Data ini untuk tahun berapa?", 
                min_value=2000, max_value=2100, value=2026, step=1,
                help="Tahun akan ditambahkan sebagai nama kolom baru."
            )
            jenis_pembaruan = f"Jumlah Penduduk {tahun_penduduk}"
            target_nama = "Jumlah Penduduk"
        else:
            jenis_pembaruan = "Luas Wilayah (km2)"
            target_nama = "Luas Wilayah"
        
        st.markdown("---")
        col_hdr1, _ = st.columns([2, 3])
        with col_hdr1:
            header_row_ui = st.number_input(
                "📌 Baris Judul Kolom (Header):", 
                min_value=1, value=1, key="hdr_profil_input"
            )
        header_index = header_row_ui - 1

        uploader_key = "upload_file_profil_" + str(st.session_state.get('upload_profil_key_counter', 0))
        uploaded_file = st.file_uploader(f"Pilih file CSV / Excel untuk {target_nama}", type=['csv', 'xlsx'], key=uploader_key)

        if uploaded_file is not None and not st.session_state.clear_profil_uploader:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_import = pd.read_csv(uploaded_file, header=header_index)
                else:
                    df_import = pd.read_excel(uploaded_file, header=header_index)
                    
                st.success("✅ File berhasil dibaca!")
                
                with st.expander("👀 Pratinjau Tabel Mentah", expanded=True):
                    df_preview = df_import.head(4).astype(str)
                    st.dataframe(df_preview, use_container_width=True)
                    
                cols_lower = [str(c).lower() for c in df_import.columns]
                kec_idx = next((i for i, c in enumerate(cols_lower) if 'kecamatan' in c or 'wilayah' in c or 'nama' in c), 0)
                
                target_idx = 0
                if "Luas" in target_nama:
                    target_idx = next((i for i, c in enumerate(cols_lower) if 'luas' in c), 0)
                else:
                    target_idx = next((i for i, c in enumerate(cols_lower) if 'penduduk' in c or 'populasi' in c or 'jiwa' in c), 0)
                
                st.markdown(f"#### ⚙️ Pemetaan Kolom {target_nama}")
                col_sel1, col_sel2 = st.columns(2)
                kecamatan_col = col_sel1.selectbox("Pilih Kolom Kecamatan:", df_import.columns, index=kec_idx)
                nilai_col = col_sel2.selectbox(f"Pilih Kolom {target_nama}:", df_import.columns, index=target_idx)
                
                is_ribu = False
                if "Penduduk" in jenis_pembaruan_ui:
                    is_ribu = st.checkbox("Kalikan Angka dengan 1.000 (Centang jika data berformat Ribuan)", value=True)
                
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                
                if st.button(f"➡️ Finalisasi & Simpan {target_nama}", type="primary"):
                    temp_df = st.session_state.data_dasar.copy()
                    import_kec_list = df_import[kecamatan_col].astype(str).str.lower().str.strip().tolist()
                    
                    for i, kec in enumerate(DAFTAR_KECAMATAN):
                        kec_lower = kec.lower()
                        try:
                            row_idx = next(idx for idx, v in enumerate(import_kec_list) if kec_lower in v)
                            raw_val = df_import.iloc[row_idx][nilai_col]
                            
                            def clean_num(val):
                                if pd.isna(val) or str(val).strip() in ["", "-", ".", "NaN", "null"]:
                                    return 0.0
                                try:
                                    clean_val = str(val).replace(',', '').strip()
                                    return float(clean_val)
                                except ValueError:
                                    return 0.0
                                    
                            final_val = clean_num(raw_val)
                            if is_ribu: final_val *= 1000
                                
                            temp_df.at[i, jenis_pembaruan] = final_val
                            
                        except StopIteration:
                            pass
                            
                    base_cols = ["Kecamatan", "Luas Wilayah (km2)"]
                    penduduk_cols = sorted([col for col in temp_df.columns if str(col).startswith("Jumlah Penduduk")])
                    
                    temp_df = temp_df[base_cols + penduduk_cols]
                            
                    sumber_baru = f"Custom (Diperbarui: {target_nama})"
                    st.session_state.data_dasar = temp_df
                    st.session_state.sumber_profil = sumber_baru
                    
                    if "Penduduk" in jenis_pembaruan_ui:
                        st.session_state.tahun_penduduk_aktif = jenis_pembaruan
                        st.session_state.pop('hasil_kmeans', None)
                    
                    simpan_profil_dasar(temp_df, sumber_baru)
                    
                    st.session_state.import_profil_sukses = True
                    st.session_state.clear_profil_uploader = True
                    st.session_state.upload_profil_key_counter = st.session_state.get('upload_profil_key_counter', 0) + 1
                    
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Gagal memproses file: {e}")
        
        if st.session_state.get('clear_profil_uploader', False):
             st.session_state.clear_profil_uploader = False