# Nama file: tab1_input.py
import streamlit as st
import pandas as pd
import uuid
import random
import copy  # Ditambahkan untuk keperluan deepcopy histori Undo/Redo

# Mengimpor fungsi dari utils
from utils import DAFTAR_KECAMATAN, beri_warna_tabel, simpan_data

def init_history(tabel):
    """Menginisialisasi riwayat (history) pada tabel jika belum ada."""
    if 'history' not in tabel:
        tabel['history'] = [{
            'data': copy.deepcopy(tabel['data']),
            'kolom_numerik': copy.deepcopy(tabel['kolom_numerik']),
            'hapus_jumlah': tabel.get('hapus_jumlah', False),
            'active_sort_col': tabel['active_sort_col']
        }]
        tabel['history_index'] = 0

def render_tab1():
    # --- FITUR TAMBAH DATA (WIZARD) ---
    if st.session_state.form_step == 0:
        col1, col2, _ = st.columns([2, 2, 6])
        if col1.button("➕ Tambah Data Manual", type="primary", use_container_width=True):
            st.session_state.form_step = 1
            st.session_state.temp_judul = ""
            st.session_state.temp_jml_kolom = 1 # Default diatur ke 1
            st.session_state.temp_kolom_names = []
            st.rerun()
            
        if col2.button("📁 Auto Import", type="primary", use_container_width=True):
            st.session_state.form_step = 4
            st.session_state.temp_judul_import = "" # Variabel memori khusus import
            st.session_state.temp_kolom_names = []
            st.session_state.last_uploaded_filename = None
            st.rerun()

    # LANGKAH 1 (INPUT MANUAL)
    if st.session_state.form_step == 1:
        with st.container(border=True):
            st.subheader("Langkah 1: Pengaturan Tabel")
            judul_input = st.text_input("Judul Tabel (misal: Infrastruktur 2024)", value=st.session_state.temp_judul)
            
            val_awal = st.session_state.temp_jml_kolom if st.session_state.temp_jml_kolom >= 1 else 1
            jml_kolom = st.number_input("Berapa jumlah indikator/kolom? (Isi 1 jika hanya ada satu data tunggal)", min_value=1, max_value=10, value=val_awal, step=1)
            
            col_btn1, col_btn2 = st.columns([1, 4])
            if col_btn1.button("➡️ Mulai Isi Kolom", type="primary"):
                if judul_input.strip() == "":
                    st.warning("Judul tabel tidak boleh kosong!")
                else:
                    st.session_state.temp_judul = judul_input
                    st.session_state.temp_jml_kolom = jml_kolom
                    
                    # Generate angka acak untuk SETIAP kolom agar angkanya berbeda-beda
                    st.session_state.angka_acak_sementara = {
                        idx: {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN} 
                        for idx in range(jml_kolom)
                    }
                    st.session_state.temp_kolom_names = []
                    st.session_state.form_step = 2
                    st.rerun()
            if col_btn2.button("Batal"):
                st.session_state.form_step = 0
                st.rerun()

    # LANGKAH 4 (AUTO IMPORT)
    if st.session_state.form_step == 4:
        with st.container(border=True):
            st.subheader("📁 Auto Import Data")
            st.markdown("Unggah file CSV atau Excel (.xlsx). Program akan mendeteksi dan mengambil data secara otomatis.")
            
            # 1. Tampilkan Uploader Terlebih Dahulu
            uploaded_file = st.file_uploader("Pilih file CSV / Excel", type=['csv', 'xlsx'])
            
            # 2. Logika Pengecekan Nama File & Pengisian Otomatis
            if uploaded_file is not None:
                if st.session_state.get('last_uploaded_filename') != uploaded_file.name:
                    # Ambil nama tanpa ekstensi, lalu rapikan garis bawah/tanda hubung agar cantik
                    nama_tanpa_ext = uploaded_file.name.rsplit('.', 1)[0]
                    nama_rapi = nama_tanpa_ext.replace('_', ' ').replace('-', ' ').title()
                    
                    st.session_state.temp_judul_import = nama_rapi
                    st.session_state.last_uploaded_filename = uploaded_file.name
                    st.rerun() # Refresh agar field judul terupdate langsung
            else:
                st.session_state.last_uploaded_filename = None
                
            if 'temp_judul_import' not in st.session_state:
                st.session_state.temp_judul_import = ""
            
            # 3. Tampilkan Field Judul Tabel yang diikat ke key memori (bisa diedit pengguna)
            judul_input = st.text_input("Judul Tabel (Bisa diedit jika tidak sesuai)", key="temp_judul_import")
            
            if uploaded_file is not None:
                try:
                    # Membaca data menggunakan pandas
                    if uploaded_file.name.endswith('.csv'):
                        df_import = pd.read_csv(uploaded_file)
                    else:
                        df_import = pd.read_excel(uploaded_file)
                        
                    st.success("✅ File berhasil dibaca!")
                    
                    # Mencoba menebak mana kolom yang berisi nama kecamatan
                    kec_col_guess = None
                    for col in df_import.columns:
                        if 'kecamatan' in col.lower() or 'wilayah' in col.lower() or 'nama' in col.lower():
                            kec_col_guess = col
                            break
                    
                    if not kec_col_guess and len(df_import.columns) > 0:
                        kec_col_guess = df_import.columns[0]
                        
                    kecamatan_col = st.selectbox("Pilih kolom yang berisi nama Kecamatan:", options=df_import.columns, index=list(df_import.columns).index(kec_col_guess) if kec_col_guess else 0)
                    
                    st.markdown("#### Pilih Kolom Data yang Ingin Diimpor:")
                    kolom_tersedia = [col for col in df_import.columns if col != kecamatan_col]
                    kolom_terpilih = []
                    
                    # Menampilkan checkbox untuk setiap kolom data yang tersedia
                    cols = st.columns(3)
                    for i, col in enumerate(kolom_tersedia):
                        with cols[i % 3]:
                            if st.checkbox(col, value=True, key=f"chk_import_{col}"):
                                kolom_terpilih.append(col)
                                
                    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                    col_save, col_cancel = st.columns([1, 4])
                    
                    if col_save.button("➡️ Finalisasi Data", type="primary"):
                        if judul_input.strip() == "":
                            st.warning("Judul tabel tidak boleh kosong!")
                        elif not kolom_terpilih:
                            st.warning("Pilih minimal 1 kolom data untuk diimpor!")
                        else:
                            st.session_state.temp_judul = judul_input.strip() # Salin ke variabel global langkah 2
                            st.session_state.temp_jml_kolom = len(kolom_terpilih)
                            st.session_state.temp_kolom_names = kolom_terpilih
                            
                            extracted_data = {}
                            # Menyiapkan list kecamatan dari file untuk dicocokkan (dijadikan lowercase agar tahan case-sensitive)
                            import_kec_list = df_import[kecamatan_col].astype(str).str.lower().str.strip().tolist()
                            
                            for idx, col_name in enumerate(kolom_terpilih):
                                extracted_data[idx] = {}
                                for kec in DAFTAR_KECAMATAN:
                                    kec_lower = kec.lower()
                                    try:
                                        # Mencari kecocokan substring nama kecamatan
                                        row_idx = next(i for i, v in enumerate(import_kec_list) if kec_lower in v)
                                        raw_val = df_import.iloc[row_idx][col_name]
                                        
                                        # Konversi data ke angka (int/float)
                                        try:
                                            val = float(raw_val)
                                            if val.is_integer():
                                                val = int(val)
                                        except:
                                            val = 0
                                    except StopIteration:
                                        # Jika kecamatan tidak ditemukan di file import, isi dengan 0
                                        val = 0
                                        
                                    extracted_data[idx][kec] = val
                                    
                            st.session_state.angka_acak_sementara = extracted_data
                            st.session_state.form_step = 2
                            st.rerun()
                            
                    if col_cancel.button("❌ Batal"):
                        st.session_state.form_step = 0
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Gagal memproses file: {e}")
            else:
                if st.button("⬅️ Kembali"):
                    st.session_state.form_step = 0
                    st.rerun()

    # LANGKAH 2 (FORM VERTIKAL PANJANG)
    if st.session_state.form_step == 2:
        total_kolom = st.session_state.temp_jml_kolom
        
        with st.container(border=True):
            st.subheader("Langkah 2: Mengisi Data Indikator")
            st.markdown("Silakan lengkapi seluruh data di bawah ini, lalu klik **Simpan Tabel** di bagian paling bawah.")
            
            all_names = []
            all_data = {}
            
            for idx in range(total_kolom):
                st.markdown(f"#### Kolom {idx + 1}")
                if total_kolom == 1:
                    st.info("Judul Kolom: **Jumlah** (Data Tunggal otomatis)")
                    nama_kolom = "Jumlah"
                else:
                    # Mengambil judul kolom dari file import jika ada
                    default_name = st.session_state.get('temp_kolom_names', [])[idx] if idx < len(st.session_state.get('temp_kolom_names', [])) else ""
                    nama_kolom = st.text_input(f"Judul Kolom {idx + 1} (misal: Panjang Jalan Rusak)", value=default_name, key=f"col_name_input_{idx}")
                
                grid_input = st.columns(3)
                col_data = []
                for i, kec in enumerate(DAFTAR_KECAMATAN):
                    # Data akan otomatis terisi dengan angka dari file import atau dari random
                    nilai_def = st.session_state.angka_acak_sementara.get(idx, {}).get(kec, 0)
                    step_val = 1.0 if isinstance(nilai_def, float) else 1
                    val = grid_input[i % 3].number_input(kec, value=nilai_def, step=step_val, key=f"val_{idx}_{kec}")
                    col_data.append(val)
                
                all_names.append(nama_kolom)
                all_data[idx] = col_data
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            
            col_back, col_save, col_cancel = st.columns([1, 1, 3])
            
            if col_back.button("⬅️ Kembali"):
                # Jika berasal dari import, kembalikan ke langkah 4, jika manual kembalikan ke langkah 1
                if st.session_state.get('temp_kolom_names'):
                    st.session_state.form_step = 4
                else:
                    st.session_state.form_step = 1 
                st.rerun()
                
            if col_save.button("💾 Simpan Tabel", type="primary"):
                error_msg = None
                if total_kolom > 1:
                    names_lower = [n.strip().lower() for n in all_names]
                    if "" in names_lower:
                        error_msg = "Semua judul kolom harus diisi!"
                    elif len(set(names_lower)) != len(names_lower):
                        error_msg = "Terdapat judul kolom yang ganda/sama! Silakan gunakan nama yang berbeda."
                    elif "jumlah" in names_lower:
                        error_msg = "Nama 'Jumlah' otomatis digunakan sistem. Silakan pilih nama lain!"
                
                if error_msg:
                    st.warning(error_msg)
                else:
                    final_data = {"Kecamatan": DAFTAR_KECAMATAN.copy()}
                    if total_kolom == 1:
                        final_data["Jumlah"] = all_data[0]
                        kolom_numerik = []
                        active_sort = "Jumlah"
                    else:
                        for idx, name in enumerate(all_names):
                            final_data[name] = all_data[idx]
                        kolom_numerik = all_names.copy()
                        active_sort = all_names[0]
                        
                    tabel_baru = {
                        "id": str(uuid.uuid4()),
                        "judul": st.session_state.temp_judul,
                        "data": final_data,
                        "kolom_numerik": kolom_numerik,
                        "warna": "#FF4B4B", 
                        "active_sort_col": active_sort,
                        "panah_bawah": True,
                        "hapus_jumlah": False 
                    }
                    st.session_state.koleksi_tabel.append(tabel_baru)
                    simpan_data(st.session_state.koleksi_tabel)
                    st.session_state.form_step = 0
                    st.rerun()
                    
            if col_cancel.button("❌ Batalkan Total"):
                st.session_state.form_step = 0
                st.rerun()

    st.markdown("---")

    # --- TAMPILAN TABEL YANG SUDAH DISIMPAN ---
    if not st.session_state.koleksi_tabel:
        st.info("Belum ada data yang ditambahkan. Klik '+ Tambah Data Baru' atau 'Auto Import' untuk memulai.")
    else:
        st.caption("💡 Tip: Gunakan menu '⚙️ Pengaturan Urutan' dan 'Hapus Kolom' di bawah judul tabel untuk mengelola data dengan rapi.")
        for i, tabel in enumerate(st.session_state.koleksi_tabel):
            # Inisialisasi riwayat (history) pada saat merender jika belum punya
            init_history(st.session_state.koleksi_tabel[i])
            tabel = st.session_state.koleksi_tabel[i]
            
            tabel_id = tabel['id']
            kolom_numerik = tabel['kolom_numerik']
            hapus_jumlah = tabel.get('hapus_jumlah', False) 
            
            # Status apakah form tambah kolom sedang terbuka
            is_form_open = st.session_state.form_step == 3
            
            # --- DERETAN TOMBOL KONTROL TABEL ---
            # Mengatur proporsi kolom agar ukuran keempat tombol sama persis (rasio 1:1:1:1)
            top_col1, top_col2, top_col_undo, top_col_redo, top_col_add, top_col3 = st.columns([4.6, 0.4, 1, 1, 1, 1])
            
            top_col1.markdown(f"### {tabel['judul']}")
            
            warna_baru = top_col2.color_picker("Warna", value=tabel['warna'], key=f"btn_warna_{tabel_id}", label_visibility="collapsed", disabled=is_form_open)
            if warna_baru != tabel['warna']:
                st.session_state.koleksi_tabel[i]['warna'] = warna_baru
                simpan_data(st.session_state.koleksi_tabel) 
                st.rerun()

            # Tombol Undo & Redo (Semua ditambahkan use_container_width=True agar lebarnya sama rata)
            can_undo = (tabel['history_index'] > 0) and not is_form_open
            can_redo = (tabel['history_index'] < len(tabel['history']) - 1) and not is_form_open
            
            if top_col_undo.button("↩️ Undo", key=f"undo_{tabel_id}", disabled=not can_undo, help="Mundurkan riwayat kolom", use_container_width=True):
                tabel['history_index'] -= 1
                state = tabel['history'][tabel['history_index']]
                tabel['data'] = copy.deepcopy(state['data'])
                tabel['kolom_numerik'] = copy.deepcopy(state['kolom_numerik'])
                tabel['hapus_jumlah'] = state['hapus_jumlah']
                tabel['active_sort_col'] = state['active_sort_col']
                simpan_data(st.session_state.koleksi_tabel)
                st.rerun()

            if top_col_redo.button("↪️ Redo", key=f"redo_{tabel_id}", disabled=not can_redo, help="Majukan riwayat kolom", use_container_width=True):
                tabel['history_index'] += 1
                state = tabel['history'][tabel['history_index']]
                tabel['data'] = copy.deepcopy(state['data'])
                tabel['kolom_numerik'] = copy.deepcopy(state['kolom_numerik'])
                tabel['hapus_jumlah'] = state['hapus_jumlah']
                tabel['active_sort_col'] = state['active_sort_col']
                simpan_data(st.session_state.koleksi_tabel)
                st.rerun()
                
            # Tombol Tambah Kolom
            if top_col_add.button("➕ Kolom", key=f"add_col_{tabel_id}", help="Tambah indikator baru ke tabel ini", use_container_width=True, disabled=is_form_open):
                st.session_state.form_step = 3
                st.session_state.edit_table_id = tabel_id
                st.session_state.angka_acak_kolom_baru = {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN}
                # Siapkan angka acak ekstra untuk berjaga-jaga jika butuh form 2 kolom
                st.session_state.angka_acak_kolom_baru_2 = {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN}
                st.rerun()
                
            # Tombol Hapus Tabel
            if top_col3.button("❌ Hapus", key=f"btn_hapus_tabel_{tabel_id}", help="Hapus Tabel Ini Total", disabled=is_form_open, use_container_width=True):
                st.session_state.koleksi_tabel.pop(i)
                simpan_data(st.session_state.koleksi_tabel) 
                st.rerun()

            # LANGKAH 3: TAMPILKAN FORM TAMBAH KOLOM TEPAT DI BAWAH JUDUL TABEL YANG DIPILIH
            if st.session_state.form_step == 3 and st.session_state.get('edit_table_id') == tabel_id:
                with st.container(border=True):
                    butuh_dua_kolom = len(tabel['kolom_numerik']) == 0
                    
                    if butuh_dua_kolom:
                        st.info(f"➕ Menambahkan indikator baru untuk tabel: **{tabel['judul']}**\n\n*Karena tabel ini sebelumnya adalah data tunggal (hanya memiliki 1 nilai/kolom Jumlah), Anda diwajibkan untuk menambahkan minimal 2 indikator yang akan dijumlahkan ulang secara otomatis.*")
                        
                        col_nama1, col_nama2 = st.columns(2)
                        nama_kolom_1 = col_nama1.text_input("Judul Kolom Baru 1", key=f"new_col_name_1_{tabel_id}")
                        nama_kolom_2 = col_nama2.text_input("Judul Kolom Baru 2", key=f"new_col_name_2_{tabel_id}")
                        
                        st.markdown("#### Nilai Kolom 1")
                        grid_input_1 = st.columns(3)
                        col_data_1 = []
                        for k_idx, kec in enumerate(DAFTAR_KECAMATAN):
                            val = grid_input_1[k_idx % 3].number_input(kec, value=st.session_state.get('angka_acak_kolom_baru', {}).get(kec, 0), step=1, key=f"new_val_1_{kec}_{tabel_id}")
                            col_data_1.append(val)
                            
                        st.markdown("#### Nilai Kolom 2")
                        grid_input_2 = st.columns(3)
                        col_data_2 = []
                        for k_idx, kec in enumerate(DAFTAR_KECAMATAN):
                            val = grid_input_2[k_idx % 3].number_input(kec, value=st.session_state.get('angka_acak_kolom_baru_2', {}).get(kec, 0), step=1, key=f"new_val_2_{kec}_{tabel_id}")
                            col_data_2.append(val)
                            
                    else:
                        st.info(f"➕ Menambahkan indikator baru untuk tabel: **{tabel['judul']}**")
                        nama_kolom = st.text_input("Judul Kolom Baru (misal: Anggaran Terealisasi)", key=f"new_col_name_{tabel_id}")
                        
                        grid_input = st.columns(3)
                        col_data = []
                        # Menggunakan k_idx agar tidak menimpa variabel 'i' dari loop tabel di luar
                        for k_idx, kec in enumerate(DAFTAR_KECAMATAN):
                            nilai_def = st.session_state.get('angka_acak_kolom_baru', {}).get(kec, 0)
                            val = grid_input[k_idx % 3].number_input(kec, value=nilai_def, step=1, key=f"new_val_{kec}_{tabel_id}")
                            col_data.append(val)
                        
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_save_new, col_cancel_new = st.columns([1, 4])
                    
                    if col_save_new.button("💾 Simpan Kolom", type="primary", key=f"save_new_col_{tabel_id}"):
                        if butuh_dua_kolom:
                            if not nama_kolom_1.strip() or not nama_kolom_2.strip():
                                st.warning("Kedua judul kolom tidak boleh kosong!")
                            elif nama_kolom_1.strip().lower() == nama_kolom_2.strip().lower():
                                st.warning("Kedua judul kolom tidak boleh sama!")
                            elif nama_kolom_1.strip().lower() == "jumlah" or nama_kolom_2.strip().lower() == "jumlah":
                                st.warning("Judul kolom tidak boleh menggunakan nama 'Jumlah' yang dilindungi sistem!")
                            else:
                                init_history(tabel)
                                tabel['history'] = tabel['history'][:tabel['history_index'] + 1]
                                
                                nama_final_1 = nama_kolom_1.strip()
                                nama_final_2 = nama_kolom_2.strip()
                                tabel['kolom_numerik'].extend([nama_final_1, nama_final_2])
                                tabel['data'][nama_final_1] = col_data_1
                                tabel['data'][nama_final_2] = col_data_2
                                
                                tabel['history'].append({
                                    'data': copy.deepcopy(tabel['data']),
                                    'kolom_numerik': copy.deepcopy(tabel['kolom_numerik']),
                                    'hapus_jumlah': tabel.get('hapus_jumlah', False),
                                    'active_sort_col': tabel['active_sort_col']
                                })
                                tabel['history_index'] += 1
                                
                                simpan_data(st.session_state.koleksi_tabel)
                                st.session_state.form_step = 0
                                st.session_state.edit_table_id = None
                                st.rerun()
                        else:
                            if not nama_kolom.strip():
                                st.warning("Judul kolom tidak boleh kosong!")
                            elif nama_kolom.strip().lower() in [c.lower() for c in tabel['kolom_numerik']] or nama_kolom.strip().lower() == "jumlah":
                                st.warning("Judul kolom sudah ada atau menggunakan nama 'Jumlah' yang dilindungi sistem!")
                            else:
                                init_history(tabel)
                                tabel['history'] = tabel['history'][:tabel['history_index'] + 1]
                                
                                nama_final = nama_kolom.strip()
                                tabel['kolom_numerik'].append(nama_final)
                                tabel['data'][nama_final] = col_data
                                
                                tabel['history'].append({
                                    'data': copy.deepcopy(tabel['data']),
                                    'kolom_numerik': copy.deepcopy(tabel['kolom_numerik']),
                                    'hapus_jumlah': tabel.get('hapus_jumlah', False),
                                    'active_sort_col': tabel['active_sort_col']
                                })
                                tabel['history_index'] += 1
                                
                                simpan_data(st.session_state.koleksi_tabel)
                                st.session_state.form_step = 0
                                st.session_state.edit_table_id = None
                                st.rerun()
                            
                    if col_cancel_new.button("❌ Batal", key=f"cancel_new_col_{tabel_id}"):
                        st.session_state.form_step = 0
                        st.session_state.edit_table_id = None
                        st.rerun()

            # Menentukan kolom apa saja yang masih ada
            kolom_tampil = []
            if len(kolom_numerik) > 0:
                kolom_tampil.extend(kolom_numerik)
                if not hapus_jumlah:
                    kolom_tampil.append("Jumlah")
            else:
                if not hapus_jumlah:
                    kolom_tampil.append("Jumlah")

            if not kolom_tampil:
                st.info("Semua kolom telah dihapus. Menghapus tabel secara otomatis...")
                st.session_state.koleksi_tabel.pop(i)
                simpan_data(st.session_state.koleksi_tabel)
                st.rerun()
                continue 

            # --- KONTROL KOLOM (DIUBAH MENJADI 2 DROPDOWN AGAR LEBIH JELAS) ---
            ctrl1, ctrl2 = st.columns(2)
            
            with ctrl1:
                with st.expander("📌 Pengaturan Urutan", expanded=False):
                    st.markdown("**Urutkan Peringkat Berdasarkan:**")
                    col_sort, col_dir = st.columns([2, 1])
                    
                    sort_idx = kolom_tampil.index(tabel['active_sort_col']) if tabel['active_sort_col'] in kolom_tampil else 0
                    sort_choice = col_sort.selectbox("Pilih Kolom:", kolom_tampil, index=sort_idx, key=f"sort_sel_{tabel_id}", label_visibility="collapsed")
                    
                    dir_choice = col_dir.selectbox("Arah:", ["⬇️ Terbesar", "⬆️ Terkecil"], index=0 if tabel['panah_bawah'] else 1, key=f"dir_sel_{tabel_id}", label_visibility="collapsed")
                    is_panah_bawah = (dir_choice == "⬇️ Terbesar")
                    
                    if sort_choice != tabel['active_sort_col'] or is_panah_bawah != tabel['panah_bawah']:
                        st.session_state.koleksi_tabel[i]['active_sort_col'] = sort_choice
                        st.session_state.koleksi_tabel[i]['panah_bawah'] = is_panah_bawah
                        simpan_data(st.session_state.koleksi_tabel)
                        st.rerun()
                        
            with ctrl2:
                with st.expander("🗑️ Hapus Kolom", expanded=False):
                    st.markdown("**Hapus Indikator/Kolom:**")
                    col_del_sel, col_del_btn = st.columns([2, 1])
                    del_choice = col_del_sel.selectbox("Pilih Kolom:", ["-- Pilih Kolom --"] + kolom_tampil, key=f"del_sel_{tabel_id}", label_visibility="collapsed")
                    
                    if col_del_btn.button("Hapus", key=f"btn_del_{tabel_id}", use_container_width=True):
                        if del_choice != "-- Pilih Kolom --":
                            nama_col = del_choice
                            # Pangkas riwayat ke depannya (jika user menghapus setelah melakukan undo)
                            st.session_state.koleksi_tabel[i]['history'] = st.session_state.koleksi_tabel[i]['history'][:st.session_state.koleksi_tabel[i]['history_index'] + 1]
                            
                            if nama_col == "Jumlah":
                                st.session_state.koleksi_tabel[i]['hapus_jumlah'] = True
                                if st.session_state.koleksi_tabel[i]['active_sort_col'] == "Jumlah":
                                    st.session_state.koleksi_tabel[i]['active_sort_col'] = kolom_numerik[0] if kolom_numerik else None
                            else:
                                st.session_state.koleksi_tabel[i]['kolom_numerik'].remove(nama_col)
                                del st.session_state.koleksi_tabel[i]['data'][nama_col]
                                if st.session_state.koleksi_tabel[i]['active_sort_col'] == nama_col:
                                    sisa_kolom = st.session_state.koleksi_tabel[i]['kolom_numerik']
                                    if sisa_kolom:
                                        st.session_state.koleksi_tabel[i]['active_sort_col'] = sisa_kolom[0]
                                    elif not st.session_state.koleksi_tabel[i].get('hapus_jumlah', False):
                                        st.session_state.koleksi_tabel[i]['active_sort_col'] = "Jumlah"
                            
                            # Simpan langkah penghapusan ini ke dalam history
                            st.session_state.koleksi_tabel[i]['history'].append({
                                'data': copy.deepcopy(st.session_state.koleksi_tabel[i]['data']),
                                'kolom_numerik': copy.deepcopy(st.session_state.koleksi_tabel[i]['kolom_numerik']),
                                'hapus_jumlah': st.session_state.koleksi_tabel[i].get('hapus_jumlah', False),
                                'active_sort_col': st.session_state.koleksi_tabel[i]['active_sort_col']
                            })
                            st.session_state.koleksi_tabel[i]['history_index'] += 1
                            
                            simpan_data(st.session_state.koleksi_tabel)
                            st.rerun()

            df = pd.DataFrame(tabel['data'])
            
            if list(df['Kecamatan']) != DAFTAR_KECAMATAN:
                df = df.set_index('Kecamatan').reindex(DAFTAR_KECAMATAN).reset_index()
                st.session_state.koleksi_tabel[i]['data'] = df.to_dict(orient='list')
                simpan_data(st.session_state.koleksi_tabel)
                tabel['data'] = st.session_state.koleksi_tabel[i]['data'] 
            
            if len(kolom_numerik) > 0:
                disabled_cols = ["Kecamatan"]
                edit_cols = ["Kecamatan"] + kolom_numerik
                
                if not hapus_jumlah:
                    df['Jumlah'] = df[kolom_numerik].sum(axis=1)
                    disabled_cols.append("Jumlah")
            else:
                disabled_cols = ["Kecamatan"]
                edit_cols = ["Kecamatan", "Jumlah"] if not hapus_jumlah else ["Kecamatan"]
                
            active_col = tabel['active_sort_col']
            
            render_cols = ["Kecamatan"] + kolom_tampil
            df_view = df[render_cols].sort_values(by=active_col, ascending=not tabel['panah_bawah']).reset_index(drop=True)
            df_berwarna = beri_warna_tabel(df_view, tabel['warna'], tabel['panah_bawah'], target_col=active_col)
            
            edited_df = st.data_editor(df_berwarna, use_container_width=True, hide_index=True, disabled=disabled_cols, key=f"editor_{tabel_id}")
            
            df_kembali_standar = edited_df[edit_cols].set_index('Kecamatan').reindex(DAFTAR_KECAMATAN).reset_index()
            data_baru = df_kembali_standar.to_dict(orient='list')
            
            if data_baru != tabel['data']:
                st.session_state.koleksi_tabel[i]['data'] = data_baru
                
                # Memastikan setiap editan sel (angka) disinkronkan ke dalam posisi riwayat (history) yang AKTIF
                # agar saat di undo/redo, data angka terbaru ini tidak ter-reset secara tidak sengaja
                if 'history' in st.session_state.koleksi_tabel[i] and st.session_state.koleksi_tabel[i]['history_index'] >= 0:
                    idx_hist = st.session_state.koleksi_tabel[i]['history_index']
                    st.session_state.koleksi_tabel[i]['history'][idx_hist]['data'] = copy.deepcopy(data_baru)
                    
                simpan_data(st.session_state.koleksi_tabel) 
                st.rerun()

            st.write("")