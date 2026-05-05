# views/tab1_input/profil_dasar.py
import streamlit as st
import pandas as pd
from utils.constants import DAFTAR_KECAMATAN
from utils.state_manager import simpan_profil_dasar

def render_profil_dasar():
    st.subheader("🏢 Bagian A: Profil Dasar Wilayah")
    st.markdown("Data **Luas Daerah** dan **Jumlah Penduduk** wajib ada dan akan digunakan sebagai patokan rasio (pembagi) oleh mesin AI K-Means untuk mencegah *Size Bias* (bias ukuran kewilayahan).")

    # Inisialisasi state untuk mengontrol Tab yang aktif
    if 'active_tab_profil' not in st.session_state:
        st.session_state.active_tab_profil = "🟢 Profil Aktif"
        
    # Inisialisasi state untuk membersihkan uploader
    if 'clear_profil_uploader' not in st.session_state:
        st.session_state.clear_profil_uploader = False

    # --- UI TERBAGI MENJADI 2 TAB ---
    # Daftar tab yang tersedia
    tabs_list = ["🟢 Profil Aktif", "📁 Import File Custom (.xlsx / .csv)"]
    
    # Mencari index dari tab yang aktif di session state, default ke 0 jika tidak ada
    try:
        default_idx = tabs_list.index(st.session_state.active_tab_profil)
    except ValueError:
        default_idx = 0

    tab_aktif, tab_import = st.tabs(tabs_list)

    with tab_aktif:
        with st.container(border=True):
            col_luas, col_penduduk = st.columns(2)
            
            df_dasar = st.session_state.data_dasar
            
            with col_luas:
                st.markdown("**🗺️ Luas Wilayah (km²)**")
                # Di balik layar kita tetap memanggil "km2" agar tidak error
                df_luas = df_dasar[['Kecamatan', 'Luas Wilayah (km2)']]
                
                # Di antarmuka, kita pasangkan topeng nama menggunakan column_config agar tampil "km²"
                st.dataframe(
                    df_luas, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Luas Wilayah (km2)": "Luas Wilayah (km²)"
                    }
                )
                
            with col_penduduk:
                st.markdown("**👥 Jumlah Penduduk (Jiwa)**")
                df_penduduk = df_dasar[['Kecamatan', 'Jumlah Penduduk (Jiwa)']]
                st.dataframe(df_penduduk, use_container_width=True, hide_index=True)

    with tab_import:
        with st.container(border=True):
            # Pesan Sukses jika baru saja berhasil import
            if st.session_state.get('import_profil_sukses', False):
                st.success("✅ File berhasil diimpor! Silakan cek tab '🟢 Profil Aktif' untuk melihat hasilnya.")
                st.session_state.import_profil_sukses = False

            st.markdown("Karena BPS biasanya memisah data Luas dan Penduduk dalam file berbeda, silakan pilih dan perbarui datanya satu per satu.")
            
            # MEMILIH JENIS TARGET FILE DULUAN
            # Tampilan di layar memakai "km²"
            jenis_pembaruan_ui = st.radio(
                "Pilih jenis data yang ingin diperbarui:",
                ["Luas Wilayah (km²)", "Jumlah Penduduk (Jiwa)"],
                horizontal=True
            )
            
            # Konversi kembali ke nama internal "km2" untuk digunakan oleh mesin di balik layar
            jenis_pembaruan = "Luas Wilayah (km2)" if "Luas" in jenis_pembaruan_ui else "Jumlah Penduduk (Jiwa)"
            target_nama = "Luas Wilayah" if "Luas" in jenis_pembaruan else "Jumlah Penduduk"
            
            col_hdr1, _ = st.columns([2, 3])
            with col_hdr1:
                header_row_ui = st.number_input(
                    "📌 Baris Judul Kolom (Header):", 
                    min_value=1, value=1, key="hdr_profil_input",
                    help="Ubah jika file Excel BPS Anda memiliki kop/judul laporan di baris atas."
                )
            header_index = header_row_ui - 1

            # Trik untuk mereset file uploader: gunakan key yang dinamis
            uploader_key = "upload_file_profil_" + str(st.session_state.get('upload_profil_key_counter', 0))
            uploaded_file = st.file_uploader(f"Pilih file CSV / Excel untuk {target_nama}", type=['csv', 'xlsx'], key=uploader_key)

            if uploaded_file is not None and not st.session_state.clear_profil_uploader:
                try:
                    # Membaca file dengan pandas
                    if uploaded_file.name.endswith('.csv'):
                        df_import = pd.read_csv(uploaded_file, header=header_index)
                    else:
                        df_import = pd.read_excel(uploaded_file, header=header_index)
                        
                    st.success("✅ File berhasil dibaca!")
                    
                    # Pratinjau Tabel Mentah
                    with st.expander("👀 Pratinjau Tabel Mentah", expanded=True):
                        st.caption("Jika muncul kolom 'Unnamed', harap atur ulang **Baris Judul Kolom** di atas.")
                        df_preview = df_import.head(4).astype(str)
                        st.dataframe(df_preview, use_container_width=True)
                        
                    # Pendeteksian kolom otomatis (Guessing Algorithm)
                    cols_lower = [str(c).lower() for c in df_import.columns]
                    kec_idx = next((i for i, c in enumerate(cols_lower) if 'kecamatan' in c or 'wilayah' in c or 'nama' in c), 0)
                    
                    target_idx = 0
                    if "Luas" in target_nama:
                        target_idx = next((i for i, c in enumerate(cols_lower) if 'luas' in c), 0)
                    else:
                        target_idx = next((i for i, c in enumerate(cols_lower) if 'penduduk' in c or 'populasi' in c or 'jiwa' in c), 0)
                    
                    st.markdown(f"#### ⚙️ Pemetaan Kolom {target_nama}")
                    st.info("Abaikan kolom lain yang tidak terkait. Sistem hanya akan mengambil 1 kolom target yang Anda pilih di bawah ini.")
                    
                    col_sel1, col_sel2 = st.columns(2)
                    kecamatan_col = col_sel1.selectbox("Pilih Kolom Kecamatan:", df_import.columns, index=kec_idx)
                    nilai_col = col_sel2.selectbox(f"Pilih Kolom {target_nama}:", df_import.columns, index=target_idx)
                    
                    is_ribu = False
                    if "Penduduk" in jenis_pembaruan:
                        is_ribu = st.checkbox("Kalikan Angka dengan 1.000 (Centang jika data berformat Ribuan)", value=True)
                    
                    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                    
                    if st.button(f"➡️ Finalisasi & Timpa {target_nama}", type="primary"):
                        # Mengambil data dasar yang sudah ada (jangan ditimpa semua)
                        temp_df = st.session_state.data_dasar.copy()
                        import_kec_list = df_import[kecamatan_col].astype(str).str.lower().str.strip().tolist()
                        
                        for i, kec in enumerate(DAFTAR_KECAMATAN):
                            kec_lower = kec.lower()
                            try:
                                # Mencari baris wilayah yang sesuai
                                row_idx = next(idx for idx, v in enumerate(import_kec_list) if kec_lower in v)
                                raw_val = df_import.iloc[row_idx][nilai_col]
                                
                                # Fungsi Sanitasi Angka Cerdas (Menghilangkan koma, string, NaN)
                                def clean_num(val):
                                    if pd.isna(val) or str(val).strip() in ["", "-", ".", "NaN", "null"]:
                                        return 0.0
                                    try:
                                        clean_val = str(val).replace(',', '').strip()
                                        return float(clean_val)
                                    except ValueError:
                                        return 0.0
                                        
                                final_val = clean_num(raw_val)
                                
                                if is_ribu:
                                    final_val *= 1000
                                    
                                # Timpa HANYA kolom yang dipilih (berdasarkan key internal)
                                temp_df.at[i, jenis_pembaruan] = final_val
                                
                            except StopIteration:
                                # Jika kecamatan tidak ditemukan pada file, beri peringatan tapi lanjutkan
                                pass
                                
                        # Simpan pembaruan ke memori
                        sumber_baru = f"Custom (Diperbarui: {target_nama})"
                        st.session_state.data_dasar = temp_df
                        st.session_state.sumber_profil = sumber_baru
                        
                        # SIMPAN KE FILE JSON
                        simpan_profil_dasar(temp_df, sumber_baru)
                        
                        # Berikan tanda bahwa import sukses
                        st.session_state.import_profil_sukses = True
                        
                        # Aktifkan flag untuk membersihkan uploader pada render berikutnya
                        st.session_state.clear_profil_uploader = True
                        
                        # Ubah key uploader agar widget di-reset oleh Streamlit
                        st.session_state.upload_profil_key_counter = st.session_state.get('upload_profil_key_counter', 0) + 1
                        
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Gagal memproses file: {e}")
            
            # Jika uploader baru saja dibersihkan, kembalikan flag ke False untuk interaksi selanjutnya
            if st.session_state.get('clear_profil_uploader', False):
                 st.session_state.clear_profil_uploader = False