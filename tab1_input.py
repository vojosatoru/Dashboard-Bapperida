# Nama file: tab1_input.py
import streamlit as st
import pandas as pd
import uuid
import random
# Mengimpor fungsi dari utils
from utils import DAFTAR_KECAMATAN, beri_warna_tabel, simpan_data

def render_tab1():
    # --- FITUR TAMBAH DATA (WIZARD) ---
    if st.session_state.form_step == 0:
        if st.button("➕ Tambah Data Baru", type="primary"):
            st.session_state.form_step = 1
            st.session_state.temp_judul = ""
            st.session_state.temp_jml_kolom = 1 # Default diatur ke 1
            st.rerun()

    # LANGKAH 1
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
                    st.session_state.form_step = 2
                    st.rerun()
            if col_btn2.button("Batal"):
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
            
            # Loop untuk merender semua kolom sekaligus dalam satu halaman panjang
            for idx in range(total_kolom):
                st.markdown(f"#### Kolom {idx + 1}")
                if total_kolom == 1:
                    st.info("Judul Kolom: **Jumlah** (Data Tunggal otomatis)")
                    nama_kolom = "Jumlah"
                else:
                    nama_kolom = st.text_input(f"Judul Kolom {idx + 1} (misal: Panjang Jalan Rusak)", key=f"col_name_input_{idx}")
                
                grid_input = st.columns(3)
                col_data = []
                for i, kec in enumerate(DAFTAR_KECAMATAN):
                    # Ambil angka acak dari memory yang di-generate di langkah 1
                    nilai_def = st.session_state.angka_acak_sementara.get(idx, {}).get(kec, 0)
                    val = grid_input[i % 3].number_input(kec, value=nilai_def, step=1, key=f"val_{idx}_{kec}")
                    col_data.append(val)
                
                all_names.append(nama_kolom)
                all_data[idx] = col_data
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            
            # Baris Tombol Kontrol (Kembali, Simpan, Batal)
            col_back, col_save, col_cancel = st.columns([1, 1, 3])
            
            if col_back.button("⬅️ Kembali"):
                st.session_state.form_step = 1 # Kembali ke langkah 1 tanpa menghapus memori
                st.rerun()
                
            if col_save.button("💾 Simpan Tabel", type="primary"):
                # Validasi Nama Kolom
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
                    # Rangkai data akhir
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
                        "hapus_jumlah": False # Penanda baru apakah kolom jumlah dihapus user
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
        st.info("Belum ada data yang ditambahkan. Klik '+ Tambah Data Baru' untuk memulai.")
    else:
        st.caption("💡 Tip: Klik tombol urutan di atas kolom untuk acuan peringkat. Gunakan 🗑️ untuk menghapus kolom tertentu.")
        for i, tabel in enumerate(st.session_state.koleksi_tabel):
            tabel_id = tabel['id']
            kolom_numerik = tabel['kolom_numerik']
            hapus_jumlah = tabel.get('hapus_jumlah', False) # Backward compatibility
            
            top_col1, top_col2, top_col3 = st.columns([7, 1, 1])
            top_col1.markdown(f"### {tabel['judul']}")
            
            warna_baru = top_col2.color_picker("Warna", value=tabel['warna'], key=f"btn_warna_{tabel_id}", label_visibility="collapsed")
            if warna_baru != tabel['warna']:
                st.session_state.koleksi_tabel[i]['warna'] = warna_baru
                simpan_data(st.session_state.koleksi_tabel) 
                st.rerun()
                
            if top_col3.button("❌", key=f"btn_hapus_tabel_{tabel_id}", help="Hapus Tabel Ini"):
                st.session_state.koleksi_tabel.pop(i)
                simpan_data(st.session_state.koleksi_tabel) 
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

            # Jika semua kolom telah dihapus oleh pengguna
            if not kolom_tampil:
                st.info("Semua kolom telah dihapus. Menghapus tabel secara otomatis...")
                st.session_state.koleksi_tabel.pop(i)
                simpan_data(st.session_state.koleksi_tabel)
                st.rerun()
                continue # Hindari error render dibawahnya

            # Menambahkan 1 kolom ekstra (kosong) di awal untuk mengimbangi lebar kolom "Kecamatan" pada tabel
            btn_cols = st.columns(len(kolom_tampil) + 1)
            
            for j, nama_col in enumerate(kolom_tampil):
                is_active = (tabel['active_sort_col'] == nama_col)
                if is_active:
                    ikon = "⬇️" if tabel['panah_bawah'] else "⬆️"
                    btn_type = "primary"
                else:
                    ikon = "⚪" 
                    btn_type = "secondary"
                
                # Gunakan indeks [j + 1] agar tombol berada di kolom ke-2 dan seterusnya
                with btn_cols[j + 1]:
                    # Tombol Sortir
                    if st.button(f"{ikon} {nama_col}", key=f"sort_{tabel_id}_{nama_col}", type=btn_type, use_container_width=True):
                        if is_active: st.session_state.koleksi_tabel[i]['panah_bawah'] = not tabel['panah_bawah']
                        else:
                            st.session_state.koleksi_tabel[i]['active_sort_col'] = nama_col
                            st.session_state.koleksi_tabel[i]['panah_bawah'] = True
                        simpan_data(st.session_state.koleksi_tabel)
                        st.rerun()
                    
                    # Tombol Hapus Individual Kolom
                    if st.button("🗑️ Hapus", key=f"del_col_{tabel_id}_{nama_col}", help=f"Hapus kolom {nama_col}", use_container_width=True):
                        if nama_col == "Jumlah":
                            st.session_state.koleksi_tabel[i]['hapus_jumlah'] = True
                            # Pindahkan active sort jika Jumlah sedang aktif
                            if st.session_state.koleksi_tabel[i]['active_sort_col'] == "Jumlah":
                                st.session_state.koleksi_tabel[i]['active_sort_col'] = kolom_numerik[0] if kolom_numerik else None
                        else:
                            st.session_state.koleksi_tabel[i]['kolom_numerik'].remove(nama_col)
                            del st.session_state.koleksi_tabel[i]['data'][nama_col]
                            # Pindahkan active sort jika kolom yang dihapus sedang aktif
                            if st.session_state.koleksi_tabel[i]['active_sort_col'] == nama_col:
                                sisa_kolom = st.session_state.koleksi_tabel[i]['kolom_numerik']
                                if sisa_kolom:
                                    st.session_state.koleksi_tabel[i]['active_sort_col'] = sisa_kolom[0]
                                elif not st.session_state.koleksi_tabel[i].get('hapus_jumlah', False):
                                    st.session_state.koleksi_tabel[i]['active_sort_col'] = "Jumlah"
                        
                        simpan_data(st.session_state.koleksi_tabel)
                        st.rerun()

            df = pd.DataFrame(tabel['data'])
            
            # --- SELF-HEALING: Kembalikan ke urutan DAFTAR_KECAMATAN ---
            if list(df['Kecamatan']) != DAFTAR_KECAMATAN:
                df = df.set_index('Kecamatan').reindex(DAFTAR_KECAMATAN).reset_index()
                st.session_state.koleksi_tabel[i]['data'] = df.to_dict(orient='list')
                simpan_data(st.session_state.koleksi_tabel)
                tabel['data'] = st.session_state.koleksi_tabel[i]['data'] 
            
            # --- PENYESUAIAN PENGUNCIAN KOLOM & PENAMPILAN ---
            if len(kolom_numerik) > 0:
                disabled_cols = ["Kecamatan"]
                edit_cols = ["Kecamatan"] + kolom_numerik
                
                # Kalkulasi Jumlah hanya jika belum dihapus
                if not hapus_jumlah:
                    df['Jumlah'] = df[kolom_numerik].sum(axis=1)
                    disabled_cols.append("Jumlah")
            else:
                disabled_cols = ["Kecamatan"]
                edit_cols = ["Kecamatan", "Jumlah"] if not hapus_jumlah else ["Kecamatan"]
                
            active_col = tabel['active_sort_col']
            
            # Hanya merender kolom yang ada (tidak dihapus)
            render_cols = ["Kecamatan"] + kolom_tampil
            df_view = df[render_cols].sort_values(by=active_col, ascending=not tabel['panah_bawah']).reset_index(drop=True)
            df_berwarna = beri_warna_tabel(df_view, tabel['warna'], tabel['panah_bawah'], target_col=active_col)
            
            edited_df = st.data_editor(df_berwarna, use_container_width=True, hide_index=True, disabled=disabled_cols, key=f"editor_{tabel_id}")
            
            # Simpan perubahan (hanya kolom yang diperbolehkan edit)
            df_kembali_standar = edited_df[edit_cols].set_index('Kecamatan').reindex(DAFTAR_KECAMATAN).reset_index()
            data_baru = df_kembali_standar.to_dict(orient='list')
            
            if data_baru != tabel['data']:
                st.session_state.koleksi_tabel[i]['data'] = data_baru
                simpan_data(st.session_state.koleksi_tabel) 
                st.rerun()

            st.write("")