# views/tab1_input/form_import.py
import streamlit as st
import pandas as pd
import uuid
import re
from utils.constants import DAFTAR_KECAMATAN
from utils.state_manager import simpan_data, init_history

def render_step_4():
    st.markdown("### 📥 Import Data dari Excel / CSV")
    st.info("Unggah file Anda, lalu sistem akan memetakan data wilayah secara otomatis.")

    # Layout pengaturan file
    col1, col2 = st.columns([3, 1])
    with col2:
        header_row = st.number_input(
            "📌 Baris Judul (Header):", 
            min_value=1, value=1, 
            help="Jika tabel Anda memiliki Kop Surat/Judul di atasnya, naikkan angka ini hingga menyentuh baris nama kolom."
        )
    with col1:
        uploaded_file = st.file_uploader("Pilih file .xlsx atau .csv:", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:
            # Membaca file
            header_idx = header_row - 1
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, header=header_idx)
            else:
                df = pd.read_excel(uploaded_file, header=header_idx)

            # Pratinjau Tabel Mentah
            with st.expander("👀 Pratinjau File Mentah", expanded=False):
                st.dataframe(df.head(5).astype(str))

            cols_lower = [str(c).lower() for c in df.columns]

            # Prediksi otomatis kolom kecamatan
            kec_idx = next((i for i, c in enumerate(cols_lower) if 'kecamatan' in c or 'wilayah' in c or 'nama' in c), 0)

            col_k1, col_k2 = st.columns(2)
            kolom_kecamatan = col_k1.selectbox("Pilih Kolom 'Kecamatan':", df.columns, index=kec_idx)

            # Memfilter kolom numerik saja (mengabaikan teks)
            numeric_cols = []
            for col in df.columns:
                if col != kolom_kecamatan and pd.api.types.is_numeric_dtype(df[col]):
                    numeric_cols.append(col)

            # Jika pandas gagal mendeteksi numerik (biasanya karena format koma string), tampilkan semua
            if not numeric_cols:
                for col in df.columns:
                    if col != kolom_kecamatan:
                        numeric_cols.append(col)

            kolom_terpilih = st.multiselect(
                "Pilih Kolom Indikator yang Ingin Diambil:",
                numeric_cols,
                default=numeric_cols
            )

            st.markdown("<hr style='margin: 15px 0'>", unsafe_allow_html=True)
            st.markdown("#### ⚙️ Pengaturan Pemisahan Tabel")

            # --- FITUR BARU: MENGAMBIL TAHUN DARI NAMA FILE ---
            file_name_clean = uploaded_file.name.rsplit('.', 1)[0]
            # Algoritma Regex untuk mencari 4 angka berurutan yang merupakan tahun (diawali 19 atau 20)
            match_tahun = re.search(r'\b(19|20)\d{2}\b', file_name_clean)
            tahun_file = match_tahun.group(0) if match_tahun else ""

            # --- MODE PEMISAHAN TERBARU ---
            mode_simpan = st.radio(
                "Pilih Metode Penyimpanan untuk kolom-kolom di atas:",
                [
                    "📦 Gabungkan (Semua Kolom ke dalam 1 Tabel yang Sama)",
                    "🗂️ Pemisahan Otomatis (1 Kolom = 1 Tabel Terpisah)",
                    "✂️ Pemisahan Kustom (Atur sendiri jumlah tabel & kolomnya)"
                ],
                help="Gunakan 'Pemisahan Kustom' untuk mengelompokkan beberapa kolom tertentu ke tabel spesifik menggunakan Checkbox."
            )

            # --- UI PEMISAHAN KUSTOM ---
            kustom_configs = []
            if "Kustom" in mode_simpan:
                with st.container(border=True):
                    # Max table disesuaikan dengan jumlah kolom terpilih agar logis
                    max_tbl = len(kolom_terpilih) if len(kolom_terpilih) > 1 else 2
                    jml_tabel = st.number_input("1. Ingin membagi menjadi berapa tabel?", min_value=2, max_value=max_tbl, value=2)
                    
                    if tahun_file:
                        st.info(f"💡 Tahun terdeteksi: **{tahun_file}**. Tahun ini akan disematkan secara otomatis di belakang nama tabel baru Anda.")
                    else:
                        st.info("💡 Tidak ada tahun yang terdeteksi dari nama file unggahan. Nama tabel akan digunakan apa adanya.")

                    st.markdown("2. Tentukan Nama Tabel & Centang Kolom yang Ingin Dimasukkan:")
                    for i in range(int(jml_tabel)):
                        st.markdown(f"**Tabel {i+1}**")
                        nama_tabel = st.text_input(f"Nama Tabel {i+1} (Contoh: Kesehatan / Pendidikan):", key=f"cust_nama_{i}")
                        
                        kolom_dipilih = []
                        # Menampilkan checkbox grid yang rapi
                        cols = st.columns(3)
                        for j, col in enumerate(kolom_terpilih):
                            with cols[j % 3]:
                                if st.checkbox(col, key=f"cust_chk_{i}_{j}"):
                                    kolom_dipilih.append(col)
                        
                        kustom_configs.append({"nama": nama_tabel, "kolom": kolom_dipilih})
                        st.markdown("<hr style='margin: 5px 0'>", unsafe_allow_html=True)

            col_btn, _ = st.columns([2, 3])
            
            if col_btn.button("💾 Ekstrak & Simpan Data", type="primary", use_container_width=True):
                # Validasi Dasar
                if not kolom_terpilih:
                    st.error("⚠️ Pilih minimal 1 kolom indikator!")
                    return
                
                # Validasi Khusus Mode Kustom
                if "Kustom" in mode_simpan:
                    for c in kustom_configs:
                        if not c["nama"].strip():
                            st.error("⚠️ Semua kolom nama tabel pada Pemisahan Kustom wajib diisi!")
                            return
                        if not c["kolom"]:
                            st.error(f"⚠️ Tabel '{c['nama']}' belum memiliki data! Silakan centang minimal 1 kolom indikator.")
                            return

                # Membersihkan dan memetakan data dengan DAFTAR_KECAMATAN agar urutannya absolut
                cleaned_data = []
                import_kec_list = df[kolom_kecamatan].astype(str).str.lower().str.strip().tolist()

                for kec in DAFTAR_KECAMATAN:
                    row_data = {"Kecamatan": kec}
                    try:
                        # Mencari index kecamatan pada data yang diimpor
                        kec_lower = kec.lower()
                        idx = next(i for i, v in enumerate(import_kec_list) if kec_lower in v)

                        for col in kolom_terpilih:
                            raw_val = df.iloc[idx][col]
                            # --- PERBAIKAN: Konversi Cerdas ke Integer (Bilangan Bulat) ---
                            try:
                                if pd.isna(raw_val) or str(raw_val).strip() in ['-', '', 'NaN', 'null']:
                                    val = 0
                                else:
                                    # Hapus koma pemisah ribuan, jadikan float dulu (untuk antisipasi desimal), lalu bulatkan ke integer
                                    val = int(round(float(str(raw_val).replace(',', ''))))
                            except:
                                val = 0
                            row_data[col] = val
                            
                    except StopIteration:
                        # Jika kecamatan (misal: "Kota Kudus") tidak ada di file, beri nilai 0
                        for col in kolom_terpilih:
                            row_data[col] = 0

                    cleaned_data.append(row_data)


                # --- LOGIKA PENYIMPANAN BERDASARKAN MODE YANG DIPILIH ---
                if "Gabungkan" in mode_simpan:
                    # Mode 1: 1 Tabel berisi banyak kolom
                    if len(kolom_terpilih) == 1:
                        # --- PERBAIKAN: Jika hanya 1 kolom, jadikan "Jumlah" ---
                        col_name = kolom_terpilih[0]
                        for row in cleaned_data:
                            row["Jumlah"] = row.pop(col_name)
                            
                        tabel_baru = {
                            'id': str(uuid.uuid4()),
                            'judul': file_name_clean,
                            'data': cleaned_data,
                            'kolom_numerik': [],
                            'warna': '#FF4B4B',
                            'hapus_jumlah': False,
                            'panah_bawah': False,
                            'active_sort_col': "Jumlah"
                        }
                    else:
                        tabel_baru = {
                            'id': str(uuid.uuid4()),
                            'judul': file_name_clean,
                            'data': cleaned_data,
                            'kolom_numerik': kolom_terpilih,
                            'warna': '#FF4B4B',
                            'hapus_jumlah': False,
                            'panah_bawah': False,
                            'active_sort_col': kolom_terpilih[0] if kolom_terpilih else ""
                        }
                    init_history(tabel_baru)
                    st.session_state.koleksi_tabel.append(tabel_baru)
                    
                elif "Otomatis" in mode_simpan:
                    # Mode 2: Memecah Data Menjadi Banyak Tabel secara individual
                    for col in kolom_terpilih:
                        single_col_data = []
                        # --- PERBAIKAN: Kolom otomatis dinamakan "Jumlah" ---
                        for row in cleaned_data:
                            single_col_data.append({
                                "Kecamatan": row["Kecamatan"],
                                "Jumlah": row[col]
                            })

                        tabel_baru = {
                            'id': str(uuid.uuid4()),
                            'judul': f"{file_name_clean} - {col}", 
                            'data': single_col_data,
                            'kolom_numerik': [],
                            'warna': '#FF4B4B',
                            'hapus_jumlah': False,
                            'panah_bawah': False,
                            'active_sort_col': "Jumlah"
                        }
                        init_history(tabel_baru)
                        st.session_state.koleksi_tabel.append(tabel_baru)
                        
                elif "Kustom" in mode_simpan:
                    # Mode 3: Memecah berdasarkan rancangan checkbox user
                    for conf in kustom_configs:
                        nama_final = f"{conf['nama'].strip()} {tahun_file}".strip()
                        kolom_custom_terpilih = conf["kolom"]
                        
                        custom_data = []
                        
                        # --- PERBAIKAN: Jika tabel kustom hanya 1 kolom, jadikan "Jumlah" ---
                        if len(kolom_custom_terpilih) == 1:
                            col_name = kolom_custom_terpilih[0]
                            for row in cleaned_data:
                                custom_data.append({
                                    "Kecamatan": row["Kecamatan"],
                                    "Jumlah": row[col_name]
                                })
                                
                            tabel_baru = {
                                'id': str(uuid.uuid4()),
                                'judul': nama_final,
                                'data': custom_data,
                                'kolom_numerik': [],
                                'warna': '#FF4B4B',
                                'hapus_jumlah': False,
                                'panah_bawah': False,
                                'active_sort_col': "Jumlah"
                            }
                        else:
                            for row in cleaned_data:
                                new_row = {"Kecamatan": row["Kecamatan"]}
                                for col in kolom_custom_terpilih:
                                    new_row[col] = row[col]
                                custom_data.append(new_row)
                                
                            tabel_baru = {
                                'id': str(uuid.uuid4()),
                                'judul': nama_final,
                                'data': custom_data,
                                'kolom_numerik': kolom_custom_terpilih,
                                'warna': '#FF4B4B',
                                'hapus_jumlah': False,
                                'panah_bawah': False,
                                'active_sort_col': kolom_custom_terpilih[0] if kolom_custom_terpilih else ""
                            }
                        init_history(tabel_baru)
                        st.session_state.koleksi_tabel.append(tabel_baru)

                # Simpan perubahan permanen ke Memori & JSON
                simpan_data(st.session_state.koleksi_tabel)
                st.session_state.form_step = 0
                st.rerun()

        except Exception as e:
            st.error(f"Gagal memproses file: {str(e)}")

    st.write("")
    if st.button("⬅️ Batalkan & Kembali", key="btn_cancel_import"):
        st.session_state.form_step = 0
        st.rerun()