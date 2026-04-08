# Nama file: tab1_input.py
import streamlit as st
import pandas as pd
import uuid
import random
# Modifikasi: Mengimpor fungsi simpan_data dari utils
from utils import DAFTAR_KECAMATAN, beri_warna_tabel, simpan_data

def render_tab1():
    # --- FITUR TAMBAH DATA (WIZARD) ---
    if st.session_state.form_step == 0:
        if st.button("➕ Tambah Data Baru", type="primary"):
            st.session_state.form_step = 1
            st.session_state.temp_judul = ""
            st.session_state.temp_jml_kolom = 0 # Default diatur ke 0
            st.rerun()

    # LANGKAH 1
    if st.session_state.form_step == 1:
        with st.container(border=True):
            st.subheader("Langkah 1: Pengaturan Tabel")
            judul_input = st.text_input("Judul Tabel (misal: Infrastruktur 2024)", value=st.session_state.temp_judul)
            
            # Modifikasi: Memperbolehkan input 0 kolom
            jml_kolom = st.number_input("Berapa jumlah sub-kolom? (Isi 0 jika hanya ada satu data tunggal)", min_value=0, max_value=10, value=st.session_state.temp_jml_kolom, step=1)
            
            col_btn1, col_btn2 = st.columns([1, 4])
            if col_btn1.button("➡️ Mulai Isi Kolom", type="primary"):
                if judul_input.strip() == "":
                    st.warning("Judul tabel tidak boleh kosong!")
                else:
                    st.session_state.temp_judul = judul_input
                    st.session_state.temp_jml_kolom = jml_kolom
                    st.session_state.temp_current_col_idx = 0
                    st.session_state.temp_data = {"Kecamatan": DAFTAR_KECAMATAN.copy()}
                    st.session_state.temp_kolom_names = []
                    st.session_state.angka_acak_sementara = {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN}
                    st.session_state.form_step = 2
                    st.rerun()
            if col_btn2.button("Batal"):
                st.session_state.form_step = 0
                st.rerun()

    # LANGKAH 2
    if st.session_state.form_step == 2:
        idx_sekarang = st.session_state.temp_current_col_idx
        total_kolom = st.session_state.temp_jml_kolom
        
        with st.container(border=True):
            # Jika user memilih 0 kolom, langsung masuk ke input Jumlah
            if total_kolom == 0:
                st.subheader("Langkah 2: Mengisi Data Utama")
                nama_kolom = "Jumlah"
            else:
                st.subheader(f"Langkah 2: Mengisi Kolom {idx_sekarang + 1} dari {total_kolom}")
                nama_kolom = st.text_input("Judul Kolom Ini (misal: Panjang Jalan Rusak)", key=f"col_name_input_{idx_sekarang}")
            
            st.write("Masukkan nilai untuk masing-masing kecamatan:")
            grid_input = st.columns(3)
            for i, kec in enumerate(DAFTAR_KECAMATAN):
                nilai_def = st.session_state.angka_acak_sementara.get(kec, 0)
                with grid_input[i % 3]:
                    st.number_input(kec, value=nilai_def, step=1, key=f"val_{idx_sekarang}_{kec}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            def validasi_nama_kolom(nama):
                if total_kolom == 0: return None # Bebas validasi jika 0 kolom
                if not nama.strip(): return "Judul kolom tidak boleh kosong!"
                if nama.strip().lower() == "jumlah": return "Nama 'Jumlah' otomatis digunakan sistem."
                if nama in st.session_state.temp_kolom_names: return "Judul kolom sudah digunakan!"
                return None

            # Jika 0 kolom, tombolnya langsung Simpan Tabel
            if total_kolom == 0:
                if st.button("💾 Simpan Tabel", type="primary"):
                    data_kolom = [st.session_state[f"val_{idx_sekarang}_{kec}"] for kec in DAFTAR_KECAMATAN]
                    st.session_state.temp_data["Jumlah"] = data_kolom
                    
                    tabel_baru = {
                        "id": str(uuid.uuid4()),
                        "judul": st.session_state.temp_judul,
                        "data": st.session_state.temp_data,
                        "kolom_numerik": [], # Daftar sub-kolom dibiarkan kosong
                        "warna": "#FF4B4B", 
                        "active_sort_col": "Jumlah",
                        "panah_bawah": True 
                    }
                    st.session_state.koleksi_tabel.append(tabel_baru)
                    simpan_data(st.session_state.koleksi_tabel) # <-- BACKUP DATA
                    st.session_state.form_step = 0
                    st.rerun()
            else:
                if idx_sekarang < total_kolom - 1:
                    if st.button("➡️ Lanjut Kolom Selanjutnya", type="primary"):
                        error_msg = validasi_nama_kolom(nama_kolom)
                        if error_msg: st.warning(error_msg)
                        else:
                            data_kolom = [st.session_state[f"val_{idx_sekarang}_{kec}"] for kec in DAFTAR_KECAMATAN]
                            st.session_state.temp_data[nama_kolom] = data_kolom
                            st.session_state.temp_kolom_names.append(nama_kolom)
                            st.session_state.temp_current_col_idx += 1
                            st.session_state.angka_acak_sementara = {kec: random.randint(10, 999) for kec in DAFTAR_KECAMATAN}
                            st.rerun()
                else:
                    if st.button("💾 Simpan Tabel", type="primary"):
                        error_msg = validasi_nama_kolom(nama_kolom)
                        if error_msg: st.warning(error_msg)
                        else:
                            data_kolom = [st.session_state[f"val_{idx_sekarang}_{kec}"] for kec in DAFTAR_KECAMATAN]
                            st.session_state.temp_data[nama_kolom] = data_kolom
                            st.session_state.temp_kolom_names.append(nama_kolom)
                            
                            tabel_baru = {
                                "id": str(uuid.uuid4()),
                                "judul": st.session_state.temp_judul,
                                "data": st.session_state.temp_data,
                                "kolom_numerik": st.session_state.temp_kolom_names,
                                "warna": "#FF4B4B", 
                                "active_sort_col": st.session_state.temp_kolom_names[0],
                                "panah_bawah": True 
                            }
                            st.session_state.koleksi_tabel.append(tabel_baru)
                            simpan_data(st.session_state.koleksi_tabel) # <-- BACKUP DATA
                            st.session_state.form_step = 0
                            st.rerun()
            
            if st.button("Batalkan Pembuatan Tabel"):
                st.session_state.form_step = 0
                st.rerun()

    st.markdown("---")

    # --- TAMPILAN TABEL YANG SUDAH DISIMPAN ---
    if not st.session_state.koleksi_tabel:
        st.info("Belum ada data yang ditambahkan. Klik '+ Tambah Data Baru' untuk memulai.")
    else:
        st.caption("💡 Tip: Klik tombol urutan di atas kolom untuk menjadikan kolom tersebut acuan peringkat.")
        for i, tabel in enumerate(st.session_state.koleksi_tabel):
            tabel_id = tabel['id']
            kolom_numerik = tabel['kolom_numerik']
            
            top_col1, top_col2, top_col3 = st.columns([7, 1, 1])
            top_col1.markdown(f"### {tabel['judul']}")
            
            warna_baru = top_col2.color_picker("Warna", value=tabel['warna'], key=f"btn_warna_{tabel_id}", label_visibility="collapsed")
            if warna_baru != tabel['warna']:
                st.session_state.koleksi_tabel[i]['warna'] = warna_baru
                simpan_data(st.session_state.koleksi_tabel) # <-- BACKUP DATA
                st.rerun()
                
            if top_col3.button("❌", key=f"btn_hapus_{tabel_id}", help="Hapus Data Ini"):
                st.session_state.koleksi_tabel.pop(i)
                simpan_data(st.session_state.koleksi_tabel) # <-- BACKUP DATA
                st.rerun()

            kolom_tampil = kolom_numerik + ["Jumlah"] if len(kolom_numerik) > 0 else ["Jumlah"]
            btn_cols = st.columns(len(kolom_tampil))
            
            for j, nama_col in enumerate(kolom_tampil):
                is_active = (tabel['active_sort_col'] == nama_col)
                if is_active:
                    ikon = "⬇️" if tabel['panah_bawah'] else "⬆️"
                    btn_type = "primary"
                else:
                    ikon = "⚪" 
                    btn_type = "secondary"
                
                with btn_cols[j]:
                    if st.button(f"{ikon} {nama_col}", key=f"sort_{tabel_id}_{nama_col}", type=btn_type, use_container_width=True):
                        if is_active: st.session_state.koleksi_tabel[i]['panah_bawah'] = not tabel['panah_bawah']
                        else:
                            st.session_state.koleksi_tabel[i]['active_sort_col'] = nama_col
                            st.session_state.koleksi_tabel[i]['panah_bawah'] = True
                        simpan_data(st.session_state.koleksi_tabel) # <-- BACKUP DATA
                        st.rerun()

            df = pd.DataFrame(tabel['data'])
            
            # --- PERBAIKAN BUG (SELF-HEALING) ---
            # Jika urutan kecamatan di dalam database internal sempat bergeser karena proses sorting sebelumnya,
            # kita kembalikan paksa ke urutan standar (DAFTAR_KECAMATAN) agar AI di Tab 3 tidak tertukar barisnya.
            if list(df['Kecamatan']) != DAFTAR_KECAMATAN:
                df = df.set_index('Kecamatan').reindex(DAFTAR_KECAMATAN).reset_index()
                st.session_state.koleksi_tabel[i]['data'] = df.to_dict(orient='list')
                simpan_data(st.session_state.koleksi_tabel)
                tabel['data'] = st.session_state.koleksi_tabel[i]['data'] # Update referensi sementara
            
            # --- PENYESUAIAN PENGUNCIAN KOLOM ---
            if len(kolom_numerik) > 0:
                # Jika ada sub-kolom, 'Jumlah' dihitung otomatis, sehingga kolom Jumlah dikunci (tidak bisa diedit)
                df['Jumlah'] = df[kolom_numerik].sum(axis=1)
                disabled_cols = ["Kecamatan", "Jumlah"]
                edit_cols = ["Kecamatan"] + kolom_numerik
            else:
                # Jika 0 kolom, 'Jumlah' adalah data utama, maka kolom Jumlah BOLEH diedit
                disabled_cols = ["Kecamatan"]
                edit_cols = ["Kecamatan", "Jumlah"]
                
            active_col = tabel['active_sort_col']
            
            # Sorting HANYA diterapkan untuk tampilan UI (df_view), bukan mengubah data asli
            df_view = df.sort_values(by=active_col, ascending=not tabel['panah_bawah']).reset_index(drop=True)
            df_berwarna = beri_warna_tabel(df_view, tabel['warna'], tabel['panah_bawah'], target_col=active_col)
            
            edited_df = st.data_editor(df_berwarna, use_container_width=True, hide_index=True, disabled=disabled_cols, key=f"editor_{tabel_id}")
            
            # Menyimpan kembali data yang sudah diedit, lalu pastikan urutannya dikembalikan ke standar
            df_kembali_standar = edited_df[edit_cols].set_index('Kecamatan').reindex(DAFTAR_KECAMATAN).reset_index()
            data_baru = df_kembali_standar.to_dict(orient='list')
            
            if data_baru != tabel['data']:
                st.session_state.koleksi_tabel[i]['data'] = data_baru
                simpan_data(st.session_state.koleksi_tabel) # <-- BACKUP DATA
                st.rerun()

            st.write("")